"""
scraper.py
小山市オープンデータポータルのスクレイピングモジュール。
requests + BeautifulSoup4 を使用（Selenium不要）。
"""
import re
import time
import logging
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.city.oyama.tochigi.jp"
TOP_URL = f"{BASE_URL}/opendata.php"


@dataclass
class FileInfo:
    """データセット内の個別ファイル情報"""
    download_code: str          # opendata_download.php?code=XXX の XXX
    filename: str               # リンクテキスト（ファイル名として使用）
    format: str                 # "CSV形式" / "Excel形式" 等
    file_size: str              # "167.13KB" 等
    last_updated: str           # "2026年2月27日" 等（更新チェックの基準）
    download_url: str           # 完全なダウンロードURL


@dataclass
class DatasetInfo:
    """1件のデータセット（詳細ページ1ページ分）の情報"""
    dataset_code: str           # opendata.php?mode=detail&code=XX の XX
    title: str                  # データセット名
    published_date: str         # 公開日
    contact: str                # 連絡先
    creator: str                # 作成者
    files: list[FileInfo] = field(default_factory=list)


def _get_html(url: str, timeout: int = 30) -> BeautifulSoup:
    """URLのHTMLを取得してBeautifulSoupオブジェクトを返す"""
    logger.debug(f"GET {url}")
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def get_all_datasets(top_url: str = TOP_URL) -> list[dict]:
    """
    全カテゴリページ（?mode=group&group=N）を巡回して全データセット一覧を返す。

    トップページの各カテゴリ (group=1〜17) をGETリクエストで取得し、
    mode=detail の form から dataset_code と title を収集する。
    重複は除外する。

    Returns:
        list of dict: [{"dataset_code": "17", "title": "文化財一覧"}, ...]
    """
    # まずトップページからカテゴリ一覧を収集
    top_soup = _get_html(top_url)

    # group番号を持つカテゴリform（mode=group）を探す
    group_values = []
    for form in top_soup.find_all("form", action=re.compile(r"opendata\.php")):
        group_input = form.find("input", {"name": "group"})
        if group_input:
            gv = group_input.get("value", "").strip()
            if gv:
                group_values.append(gv)

    logger.info(f"カテゴリ数: {len(group_values)} 件 (group={group_values})")

    seen_codes: set[str] = set()
    datasets: list[dict] = []

    for group in group_values:
        time.sleep(1)  # サーバー負荷軽減のためのウェイト
        group_url = f"{top_url}?mode=group&group={group}"
        try:
            soup = _get_html(group_url)
        except requests.RequestException as e:
            logger.warning(f"カテゴリページ取得失敗 (group={group}): {e}")
            continue

        for form in soup.find_all("form", action=re.compile(r"opendata\.php")):
            mode_input = form.find("input", {"name": "mode", "value": "detail"})
            code_input = form.find("input", {"name": "code"})
            if mode_input and code_input:
                dataset_code = code_input.get("value", "").strip()
                if not dataset_code or dataset_code in seen_codes:
                    continue
                a_tag = form.find("a")
                title = a_tag.get_text(strip=True) if a_tag else f"code_{dataset_code}"
                datasets.append({"dataset_code": dataset_code, "title": title})
                seen_codes.add(dataset_code)

    logger.info(f"全カテゴリから {len(datasets)} 件のデータセットを検出")
    return datasets


def _parse_table_value(soup: BeautifulSoup, th_text: str) -> str:
    """tableのth テキストに対応するtdの値を返す"""
    th = soup.find("th", string=lambda t: t and t.strip() == th_text)
    if th:
        td = th.find_next_sibling("td")
        if td:
            return td.get_text(strip=True)
    return ""


def get_dataset_detail(dataset_code: str) -> Optional[DatasetInfo]:
    """
    データセット詳細ページを解析して DatasetInfo を返す。

    Args:
        dataset_code: opendata.php?mode=detail&code=XX の XX
    Returns:
        DatasetInfo or None（取得失敗時）
    """
    url = f"{TOP_URL}?mode=detail&code={dataset_code}"
    try:
        soup = _get_html(url)
    except requests.RequestException as e:
        logger.error(f"詳細ページ取得失敗 (code={dataset_code}): {e}")
        return None

    # h2タグからタイトル取得（breadcrumb最後のliでも可）
    contents_div = soup.find("div", id="contents")
    if not contents_div:
        logger.warning(f"contentsセクションが見つかりません (code={dataset_code})")
        return None

    title_tag = contents_div.find("h2")
    title = title_tag.get_text(strip=True) if title_tag else f"code_{dataset_code}"

    # openDataTable01 からメタ情報取得
    meta_table = contents_div.find("table", class_="openDataTable01")
    published_date = ""
    contact = ""
    creator = ""
    if meta_table:
        published_date = _parse_table_value(meta_table, "公開日")
        contact = _parse_table_value(meta_table, "連絡先")
        creator = _parse_table_value(meta_table, "作成者")

    # h3「データ」以下のul からファイルリスト取得
    data_h3 = contents_div.find("h3", string=lambda t: t and t.strip() == "データ")
    files = []
    if data_h3:
        data_ul = data_h3.find_next_sibling("ul")
        if data_ul:
            for li in data_ul.find_all("li", recursive=False):
                file_info = _parse_file_li(li)
                if file_info:
                    files.append(file_info)

    dataset = DatasetInfo(
        dataset_code=dataset_code,
        title=title,
        published_date=published_date,
        contact=contact,
        creator=creator,
        files=files,
    )
    logger.info(f"詳細取得完了: [{dataset_code}] {title} ({len(files)} ファイル)")
    return dataset


def _parse_file_li(li) -> Optional[FileInfo]:
    """
    データセクションの<li>要素からFileInfoを生成する。
    """
    a_tag = li.find("a", href=re.compile(r"opendata_download\.php"))
    if not a_tag:
        return None

    href = a_tag.get("href", "")
    # download code を href から抽出: opendata_download.php?code=427
    m = re.search(r"code=(\d+)", href)
    if not m:
        return None
    download_code = m.group(1)

    filename = a_tag.get_text(strip=True)
    download_url = f"{BASE_URL}/{href}" if not href.startswith("http") else href

    # openDataTable02 からファイル詳細取得
    file_table = li.find("table", class_="openDataTable02")
    file_format = ""
    file_size = ""
    last_updated = ""
    if file_table:
        file_format = _parse_table_value(file_table, "形式")
        file_size = _parse_table_value(file_table, "ファイルサイズ")
        last_updated = _parse_table_value(file_table, "最終更新日")

    return FileInfo(
        download_code=download_code,
        filename=filename,
        format=file_format,
        file_size=file_size,
        last_updated=last_updated,
        download_url=download_url,
    )
