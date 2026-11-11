"""
db_manager.py
単一 SQLite3 データベース (db/oyama_opendata.db) 管理モジュール。

管理テーブル:
  - sys_datasets: データセットのメタ情報
  - sys_files: 各ファイルのダウンロード管理情報
  - sys_columns: 物理名と論理名（日本語表記）のマッピング情報

データテーブル:
  - データセットごとに1テーブル (全42データセット中、CSVが存在する36データセット)
  - 同一データセット内の複数CSVは1つのテーブルに統合インポート
  - カラム名はすべて英語物理名に正規化
  - _source_file カラムを自動追加
"""
import csv
import io
import logging
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

SINGLE_DB_FILENAME = "oyama_opendata.db"
CSV_ENCODINGS = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]

# データセットコード -> 英語テーブル名マッピング
DATASET_TABLE_NAMES = {
    "2":  "bus_routes_gtfs",
    "3":  "farmland_stats",
    "4":  "crop_harvest_stats",
    "5":  "forestry_fishery_stats",
    "6":  "school_students",
    "7":  "nursery_schools",
    "8":  "designated_cultural_properties",
    "9":  "lifelong_learning_facilities",
    "10": "insured_category1",
    "11": "nursing_care_certified",
    "12": "home_care_recipients",
    "13": "community_care_recipients",
    "14": "facility_care_recipients",
    "15": "nursing_care_benefits",
    "16": "nursing_care_providers",
    "17": "cultural_properties",
    "18": "event_info",
    "19": "manufacturing_mining_stats",
    "20": "sightseeing_info",
    "21": "fire_rescue_ambulance_stats",
    "24": "fire_trucks",
    "25": "fire_dept_coop_businesses",
    "26": "fire_dept_support_businesses",
    "27": "first_aid_stations",
    "28": "fire_hydrants",
    "29": "flood_hazard_maps",
    "30": "onuma_hazard_maps",
    "31": "landslide_hazard_maps",
    "32": "earthquake_hazard_maps",
    "33": "farmland_rent_rates",
    "34": "population_by_district",
    "35": "population_by_age",
    "36": "public_wifi",
    "37": "commercial_service_stats",
    "38": "park_facilities",
    "39": "drainage_pump_stations",
    "40": "agricultural_sewage_facilities",
    "41": "aed_locations",
    "43": "bicycle_parking_lots",
    "44": "public_housing",
    "45": "childcare_facilities",
    "46": "medical_institutions_v2",
    "47": "calendar_events",
    "48": "budget_settlement_info",
    "50": "police_fire_facilities",
    "51": "tourist_facilities",
    "58": "evacuation_sites",
    "59": "medical_institutions",
    "67": "public_toilets",
}

# 日本語論理名 -> 英語物理名 マッピング辞書
COLUMN_NAME_MAP = {
    # 識別・行政コード
    "都道府県コード又は市区町村コード": "city_code",
    "全国地方公共団体コード": "city_code",
    "市区町村コード": "city_code",
    "行政区コード": "district_code",
    "POIコード": "poi_code",
    "NO": "id",
    "No": "id",
    "ID": "id",
    "行": "id",
    "学校ID": "school_id",
    "町字ID": "town_id",
    "認定番号": "certification_number",
    "管理番号": "management_number",
    "事業所番号": "facility_number",
    "医療機関コード": "medical_institution_code",

    # 名称・地域
    "都道府県名": "prefecture",
    "所在地_都道府県": "prefecture",
    "学校所在地_都道府県名": "prefecture",
    "市区町村名": "city",
    "所在地_市区町村": "city",
    "学校所在地_市区町村名": "city",
    "地方公共団体名": "organization_name",
    "学校所在地_行政区名": "district_name",
    "名称": "name",
    "イベント名": "name",
    "小山市消防団協力事業所名": "name",
    "事業所名": "name",
    "学校名称": "name",
    "店舗名": "name",
    "施設名": "name",
    "協会名": "name",
    "介護サービス事業所名称": "name",
    "名称_カナ": "name_kana",
    "イベント名_カナ": "name_kana",
    "学校名称_カナ": "name_kana",
    "協会名カナ": "name_kana",
    "介護サービス事業所名称_カナ": "name_kana",
    "名称_通称": "name_alias",
    "名称_英語": "name_en",
    "名称_英字": "name_en",
    "法人の名称": "corporate_name",
    "団体名": "organization_name",
    "地区": "district",
    "地区名": "district_name",
    "地域名": "region_name",
    "場所名称": "location_name",
    "大字町丁名": "town_name",

    # 住所・位置情報
    "住所": "address",
    "所在地": "address",
    "所在": "address",
    "所在地_連結表記": "address",
    "通学区域の住所": "address",
    "連絡先住所": "address",
    "建物名等_方書": "address_detail",
    "方書": "address_detail",
    "所在地_町字": "town_address",
    "所在地_番地以下": "street_address",
    "設置位置": "location",
    "緯度": "latitude",
    "経度": "longitude",
    "標高": "elevation",
    "EPSGコード": "epsg_code",

    # 連絡先
    "電話番号": "phone_number",
    "TEL": "phone_number",
    "連絡先電話番号": "phone_number",
    "問い合わせ先_電話番号": "phone_number",
    "内線番号": "extension_number",
    "連絡先内線番号": "extension_number",
    "問い合わせ先_電話番号_内線番号": "extension_number",
    "FAX番号": "fax_number",
    "法人番号": "corporate_number",
    "情報の管理主体_法人番号": "corporate_number",
    "郵便番号": "postal_code",
    "連絡先メールアドレス": "email",
    "問い合わせ先_メールアドレス": "email",
    "URL": "url",
    "問い合わせ先_webフォーム": "web_form_url",
    "連絡先FormURL": "web_form_url",

    # 時間・日時
    "利用可能曜日": "available_days",
    "診療曜日": "available_days",
    "開始時間": "start_time",
    "診療開始時間": "start_time",
    "利用開始時間": "start_time",
    "終了時間": "end_time",
    "診療終了時間": "end_time",
    "利用終了時間": "end_time",
    "利用可能時間特記事項": "available_hours_notes",
    "利用可能日時特記事項": "available_hours_notes",
    "診療日時特記事項": "available_hours_notes",
    "提供可能時間": "available_hours_notes",
    "認可等年月日": "approval_date",
    "通学区域_登録年月日": "registration_date",
    "通学区域_廃止日": "abolition_date",
    "公開日": "published_date",
    "最終更新日": "last_updated_date",
    "基準年月日": "reference_date",
    "文化財指定日": "designation_date",
    "開店年": "opening_year",
    "開店月": "opening_month",
    "登録年": "registration_year",
    "交付年": "grant_year",
    "年": "year",
    "月": "month",
    "元号": "era",
    "年次": "year_era",
    "年次_西暦": "year_ad",
    "時間外における対応": "after_hours_care",

    # 属性・分類
    "種別": "category",
    "区分": "category",
    "種類": "category",
    "分類": "category",
    "業態": "category",
    "文化財分類": "category",
    "医療機関の種類": "category",
    "行政サービス拠点種別": "category",
    "消防団車両種別": "category",
    "サービス種類": "service_type",
    "実施サービス": "service_type",
    "サービス分類": "service_category",
    "診療科目": "medical_departments",
    "病床数": "bed_count",
    "収容定員": "capacity",
    "受入年齢": "accepted_age",
    "一時預かりの有無": "temporary_care_available",
    "小児対応設備の有無": "pediatric_equipment_available",
    "屋内外": "indoor_outdoor",
    "最大駐輪台数": "max_bicycle_capacity",
    "公簿面積": "registered_area",
    "店舗面積": "store_area",
    "台数": "vehicle_count",
    "車両メーカー": "vehicle_manufacturer",
    "消防団車両所属": "vehicle_affiliation",
    "消防団車両名称": "vehicle_name",

    # 災害避難情報
    "災害種別_洪水": "disaster_flood",
    "災害種別_崖崩れ_土石流及び地滑り": "disaster_landslide",
    "災害種別_高潮": "disaster_storm_surge",
    "災害種別_地震": "disaster_earthquake",
    "災害種別_津波": "disaster_tsunami",
    "災害種別_大規模な火事": "disaster_fire",
    "災害種別_内水氾濫": "disaster_inundation",
    "災害種別_火山現象": "disaster_volcano",
    "指定避難所との重複": "is_duplicate_shelter",
    "想定収容人数": "estimated_capacity",
    "対象となる町会_自治会": "target_associations",

    # 人口・統計情報
    "総人口": "total_population",
    "男性": "male_population",
    "女性": "female_population",
    "男_人": "male_population",
    "女_人": "female_population",
    "世帯数": "household_count",
    "世帯数_世帯": "household_count",
    "合計_人": "total_count",
    "第１号被保険者_人": "insured_category1_count",
    "第２号被保険者_人": "insured_category2_count",
    "計_人": "total_count",
    "計": "total_count",
    "構成比": "ratio",
    "増加率": "growth_rate",
    "年齢": "age",

    # その他
    "説明": "description",
    "概要": "description",
    "概要_英語": "description_en",
    "説明_英語": "description_en",
    "備考": "remarks",
    "特記事項": "remarks",
    "バリアフリー情報": "barrier_free_info",
    "画像": "image_url",
    "画像_ライセンス": "image_license",
    "SSID": "ssid",
    "提供エリア": "service_area",
    "ライセンス": "license",
    "文字コード": "charset",
}


def get_db_path(db_dir: Path) -> Path:
    """単一DBファイルのパスを返す"""
    return db_dir / SINGLE_DB_FILENAME


def get_connection(db_dir: Path) -> sqlite3.Connection:
    """単一DBへの接続を返す（初期化未実施なら自動初期化）"""
    db_path = get_db_path(db_dir)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _init_sys_schema(conn)
    return conn


def _init_sys_schema(conn: sqlite3.Connection) -> None:
    """システム管理テーブルのスキーマを初期化する"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sys_datasets (
            dataset_code   TEXT PRIMARY KEY,
            title          TEXT NOT NULL,
            table_name     TEXT,
            published_date TEXT,
            contact        TEXT,
            creator        TEXT,
            last_checked   TEXT,
            file_count     INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS sys_files (
            download_code   TEXT PRIMARY KEY,
            dataset_code    TEXT NOT NULL,
            filename        TEXT,
            format          TEXT,
            file_size       TEXT,
            last_updated    TEXT,
            local_path      TEXT,
            is_downloaded   INTEGER DEFAULT 0,
            last_downloaded TEXT,
            FOREIGN KEY (dataset_code) REFERENCES sys_datasets(dataset_code)
        );

        CREATE TABLE IF NOT EXISTS sys_columns (
            table_name   TEXT NOT NULL,
            column_name  TEXT NOT NULL,
            logical_name TEXT NOT NULL,
            PRIMARY KEY (table_name, column_name)
        );
    """)
    conn.commit()


def get_table_name_for_dataset(dataset_code: str, title: str = "") -> str:
    """データセットコードに対応する英語テーブル名を返す"""
    if dataset_code in DATASET_TABLE_NAMES:
        return DATASET_TABLE_NAMES[dataset_code]
    clean_title = re.sub(r"[^\w]", "_", title).strip("_")
    return f"ds_{dataset_code}_{clean_title}" if clean_title else f"ds_{dataset_code}"


def _to_physical_col_name(logical_name: str) -> str:
    """論理名（日本語項目名）を英語物理名に変換・正規化"""
    cleaned = logical_name.strip()
    if cleaned in COLUMN_NAME_MAP:
        return COLUMN_NAME_MAP[cleaned]

    # すでに半角英数字・アンダースコアのみの場合
    if re.match(r"^[a-zA-Z0-9_]+$", cleaned):
        res = cleaned.lower()
        if res[0].isdigit():
            res = "col_" + res
        return res

    # 日本語が含まれる・未定義のカラムの場合のフォールバック変換
    res = re.sub(r"[^\w]", "_", cleaned, flags=re.UNICODE)
    res = re.sub(r"_+", "_", res).strip("_")
    if not res:
        res = "column"
    if res[0].isdigit():
        res = "col_" + res
    return res.lower()


def upsert_dataset(db_dir: Path, dataset) -> None:
    """データセットメタ情報を sys_datasets に登録/更新"""
    tbl_name = get_table_name_for_dataset(dataset.dataset_code, dataset.title)
    with get_connection(db_dir) as conn:
        conn.execute("""
            INSERT INTO sys_datasets (dataset_code, title, table_name, published_date,
                                     contact, creator, last_checked, file_count)
            VALUES (:code, :title, :tbl, :pub, :contact, :creator, :checked, :fc)
            ON CONFLICT(dataset_code) DO UPDATE SET
                title          = excluded.title,
                table_name     = excluded.table_name,
                published_date = excluded.published_date,
                contact        = excluded.contact,
                creator        = excluded.creator,
                last_checked   = excluded.last_checked,
                file_count     = excluded.file_count
        """, {
            "code":    dataset.dataset_code,
            "title":   dataset.title,
            "tbl":     tbl_name,
            "pub":     dataset.published_date,
            "contact": dataset.contact,
            "creator": dataset.creator,
            "checked": datetime.now().isoformat(),
            "fc":      len(dataset.files),
        })
        conn.commit()


def upsert_file_meta(db_dir: Path, dataset_code: str, file_info) -> None:
    """ファイルメタ情報を sys_files に登録/更新"""
    with get_connection(db_dir) as conn:
        conn.execute("""
            INSERT INTO sys_files (download_code, dataset_code, filename, format,
                                  file_size, last_updated)
            VALUES (:dc, :dsc, :fn, :fmt, :fs, :lu)
            ON CONFLICT(download_code) DO UPDATE SET
                filename     = excluded.filename,
                format       = excluded.format,
                file_size    = excluded.file_size,
                last_updated = excluded.last_updated
        """, {
            "dc":  file_info.download_code,
            "dsc": dataset_code,
            "fn":  file_info.filename,
            "fmt": file_info.format,
            "fs":  file_info.file_size,
            "lu":  file_info.last_updated,
        })
        conn.commit()


def update_file_downloaded(
    db_dir: Path,
    download_code: str,
    local_path: Path,
) -> None:
    """ダウンロード完了後のファイル状態更新"""
    with get_connection(db_dir) as conn:
        conn.execute("""
            UPDATE sys_files
            SET is_downloaded   = 1,
                local_path      = :lp,
                last_downloaded = :ld
            WHERE download_code = :dc
        """, {
            "dc": download_code,
            "lp": str(local_path),
            "ld": datetime.now().isoformat(),
        })
        conn.commit()


def get_stored_last_updated(db_dir: Path, download_code: str) -> Optional[str]:
    """登録されている最終更新日を取得"""
    with get_connection(db_dir) as conn:
        row = conn.execute(
            "SELECT last_updated FROM sys_files WHERE download_code = ?",
            (download_code,)
        ).fetchone()
    return row["last_updated"] if row else None


def is_already_downloaded(db_dir: Path, download_code: str) -> bool:
    """ダウンロード済みか判定"""
    with get_connection(db_dir) as conn:
        row = conn.execute(
            "SELECT is_downloaded FROM sys_files WHERE download_code = ?",
            (download_code,)
        ).fetchone()
    return bool(row and row["is_downloaded"])


def _read_csv_file(filepath: Path) -> Optional[Tuple[List[str], List[List[str]]]]:
    """CSVファイルを読み込み (headers, data_rows) を返す"""
    if not filepath.exists():
        return None
    content = filepath.read_bytes()
    for encoding in CSV_ENCODINGS:
        try:
            text_data = content.decode(encoding)
            if "\ufffd" in text_data:
                continue
            reader = csv.reader(io.StringIO(text_data))
            rows = [r for r in reader if r]
            if not rows:
                return None
            headers = [h.strip() for h in rows[0]]
            data_rows = rows[1:]
            return headers, data_rows
        except (UnicodeDecodeError, csv.Error):
            continue
    logger.error(f"CSVデコード失敗: {filepath.name}")
    return None


def rebuild_dataset_table(
    db_dir: Path,
    dataset_code: str,
    csv_file_paths: List[Path],
) -> bool:
    """
    データセットに含まれるすべてのCSVファイルを1つのテーブルに統合インポートする。
    全カラム名を英語物理名に正規化し、sys_columns に論理名マッピングを登録する。
    """
    table_name = get_table_name_for_dataset(dataset_code)

    # 1. 全CSVから (物理名, 論理名) のペア（ユニークな物理名順序）を抽出
    physical_cols_union: List[str] = []
    logical_map: Dict[str, str] = {} # physical -> logical
    file_data_list = []

    for filepath in csv_file_paths:
        res = _read_csv_file(filepath)
        if res is None:
            continue
        headers, data_rows = res
        for orig_h in headers:
            phys_h = _to_physical_col_name(orig_h)
            if phys_h != "_source_file" and phys_h not in physical_cols_union:
                # 重複カラム名の回避
                counter = 1
                base_phys = phys_h
                while phys_h in physical_cols_union:
                    phys_h = f"{base_phys}_{counter}"
                    counter += 1
                physical_cols_union.append(phys_h)
                logical_map[phys_h] = orig_h
        file_data_list.append((filepath.name, headers, data_rows))

    if not file_data_list:
        logger.warning(f"[{dataset_code}] インポート可能なCSVデータがありません")
        return False

    # 2. テーブル定義作成 (_source_file を先頭に付与)
    columns = ["_source_file"] + physical_cols_union
    col_defs = ", ".join(f'"{c}" TEXT' for c in columns)

    conn = get_connection(db_dir)
    try:
        conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        conn.execute(f'CREATE TABLE "{table_name}" ({col_defs})')

        # sys_columns テーブルに論理名マッピングを登録
        conn.execute('DELETE FROM sys_columns WHERE table_name = ?', (table_name,))
        sys_col_rows = [(table_name, "_source_file", "元ファイル名")]
        for p_col in physical_cols_union:
            sys_col_rows.append((table_name, p_col, logical_map[p_col]))
        conn.executemany(
            'INSERT INTO sys_columns (table_name, column_name, logical_name) VALUES (?, ?, ?)',
            sys_col_rows
        )

        # 3. 全CSV行データをマッピングして挿入
        placeholders = ", ".join("?" * len(columns))
        insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'

        total_rows = 0
        for filename, headers, data_rows in file_data_list:
            # 元のヘッダー名 -> 物理カラム名
            header_to_phys = {}
            for h in headers:
                p_name = _to_physical_col_name(h)
                header_to_phys[h] = p_name

            rows_to_insert = []
            for row in data_rows:
                row_dict = {}
                for h, val in zip(headers, row):
                    p_name = header_to_phys[h]
                    row_dict[p_name] = val
                mapped_row = [filename] + [row_dict.get(c, None) for c in physical_cols_union]
                rows_to_insert.append(mapped_row)

            conn.executemany(insert_sql, rows_to_insert)
            total_rows += len(rows_to_insert)

        conn.commit()
        logger.info(
            f"データセット [{dataset_code}] テーブル作成完了: {table_name} "
            f"({len(file_data_list)} CSVファイル, 計 {total_rows} 行, {len(columns)} カラム)"
        )
        return True
    except sqlite3.Error as e:
        logger.error(f"テーブル作成エラー (dataset_code={dataset_code}, table={table_name}): {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
