"""
main.py
小山市オープンデータ 月次バッチ処理のエントリーポイント。

単一SQLite DB (db/oyama_opendata.db) に全42データセットを集約管理。
1データセット = 1テーブル構成（同データセット内の複数CSVは縦結合）。
"""
import argparse
import logging
import sys
import time
from pathlib import Path

import requests

import scraper
import downloader
import db_manager

# ---------------------------------------------------------------------------
# ディレクトリ設定
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
CSV_DIR = SCRIPT_DIR / "csv"
NON_CSV_DIR = SCRIPT_DIR / "csv" / "non_csv"
DB_DIR = SCRIPT_DIR / "db"

# ---------------------------------------------------------------------------
# ロギング設定
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("main")


def process_dataset(
    dataset: scraper.DatasetInfo,
    dry_run: bool,
    force: bool,
) -> dict:
    """
    1データセットの処理（全ファイルの更新チェック・DL → 1テーブル作成）を行う。

    Returns:
        {"dataset_code": str, "updated": bool, "files_processed": int, "errors": int}
    """
    ds_code = dataset.dataset_code
    logger.info(f"\n--- データセット [{ds_code}] {dataset.title} ({len(dataset.files)} ファイル) ---")

    # 管理DBにデータセット情報を登録
    db_manager.upsert_dataset(DB_DIR, dataset)

    dataset_has_updates = False
    downloaded_csv_paths = []
    errors = 0

    for file_info in dataset.files:
        dc = file_info.download_code
        is_csv = "CSV" in file_info.format.upper()
        dest_dir = CSV_DIR if is_csv else NON_CSV_DIR

        # 管理DBにファイルメタ情報を登録
        db_manager.upsert_file_meta(DB_DIR, ds_code, file_info)

        # 更新チェック（ローカルにファイルが存在する場合はDLスキップ）
        local_file_exists = (dest_dir / file_info.filename).exists() or bool(list(dest_dir.glob(f"*{file_info.filename}*")))
        stored_date = db_manager.get_stored_last_updated(DB_DIR, dc)
        already_dl = db_manager.is_already_downloaded(DB_DIR, dc)

        needs_download = (not local_file_exists) and (force or (not already_dl) or (stored_date != file_info.last_updated))

        if needs_download:
            dataset_has_updates = True
            reason = "強制" if force else ("新規" if stored_date is None else f"更新あり ({stored_date} -> {file_info.last_updated})")
            logger.info(f"  [{dc}] {reason}: {file_info.filename}")

            if dry_run:
                logger.info(f"  [{dc}] [DRY-RUN] ダウンロードをスキップ")
                continue

            try:
                time.sleep(1)  # サーバー負荷軽減のためのウェイト
                local_path = downloader.download_file(
                    url=file_info.download_url,
                    dest_dir=dest_dir,
                    preferred_filename=file_info.filename,
                )
                db_manager.update_file_downloaded(DB_DIR, dc, local_path)
                if is_csv:
                    downloaded_csv_paths.append(local_path)
            except requests.RequestException as e:
                logger.error(f"  [{dc}] ダウンロード失敗: {e}")
                errors += 1
        else:
            logger.debug(f"  [{dc}] スキップ (更新なし): {file_info.filename}")
            # すでに保存されているパスを取得
            if is_csv:
                local_path = CSV_DIR / file_info.filename
                if local_path.exists():
                    downloaded_csv_paths.append(local_path)
                else:
                    # 命名揺れでローカルパスが見つからない場合はワイルドカードや代替探求
                    found = list(CSV_DIR.glob(f"*{file_info.filename}*"))
                    if found:
                        downloaded_csv_paths.append(found[0])

    # データセットに更新があった場合、または強制実行の場合、単一テーブルを再構築
    if not dry_run and (dataset_has_updates or force):
        if downloaded_csv_paths:
            success = db_manager.rebuild_dataset_table(DB_DIR, ds_code, downloaded_csv_paths)
            if not success:
                errors += 1
        else:
            logger.info(f"  [{ds_code}] 対象のCSVファイルが存在しないためテーブル作成スキップ")

    return {
        "dataset_code": ds_code,
        "updated": dataset_has_updates,
        "files_processed": len(dataset.files),
        "errors": errors,
    }


def main(dry_run: bool = False, force: bool = False) -> None:
    """メインバッチ処理"""
    logger.info("=" * 60)
    logger.info("小山市オープンデータ 月次バッチ処理 (単一DB 1データセット1テーブル) 開始")
    if dry_run:
        logger.info("[DRY-RUN モード] ダウンロード・DB作成はスキップします")
    if force:
        logger.info("[FORCE モード] 全データセット・全ファイルを再処理します")
    logger.info("=" * 60)

    # 必要なディレクトリを事前作成
    for d in [CSV_DIR, NON_CSV_DIR, DB_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    # Step 1: トップページから全カテゴリを巡回してデータセット一覧を取得
    logger.info("Step 1: データセット一覧を取得中...")
    try:
        datasets_list = scraper.get_all_datasets()
    except requests.RequestException as e:
        logger.critical(f"トップページの取得に失敗しました: {e}")
        sys.exit(1)

    if not datasets_list:
        logger.warning("データセットが1件も見つかりませんでした。処理を終了します。")
        sys.exit(0)

    logger.info(f"  検出件数: {len(datasets_list)} データセット")

    stats = {"datasets": len(datasets_list), "files": 0, "updated_datasets": 0, "errors": 0}

    # Step 2: 各データセットを処理
    for idx, ds_entry in enumerate(datasets_list, 1):
        ds_code = ds_entry["dataset_code"]
        ds_title = ds_entry["title"]
        logger.info(f"\nProgress [{idx}/{len(datasets_list)}]: code={ds_code} {ds_title}")

        time.sleep(1)  # サーバー負荷軽減のためのウェイト
        dataset = scraper.get_dataset_detail(ds_code)
        if dataset is None:
            logger.error(f"  詳細ページ取得失敗 (code={ds_code}) - スキップ")
            stats["errors"] += 1
            continue

        res = process_dataset(dataset, dry_run, force)
        stats["files"] += res["files_processed"]
        if res["updated"]:
            stats["updated_datasets"] += 1
        stats["errors"] += res["errors"]

    logger.info("\n" + "=" * 60)
    logger.info("処理完了 サマリー")
    logger.info(f"  DBファイル        : {db_manager.get_db_path(DB_DIR)}")
    logger.info(f"  全データセット数  : {stats['datasets']}")
    logger.info(f"  更新データセット数: {stats['updated_datasets']}")
    logger.info(f"  全対象ファイル数  : {stats['files']}")
    logger.info(f"  エラー数          : {stats['errors']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="小山市オープンデータ 月次バッチ処理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="チェックのみ実施")
    parser.add_argument("--force", action="store_true", help="全テーブル再作成・強制実行")
    args = parser.parse_args()
    main(dry_run=args.dry_run, force=args.force)
