"""
downloader.py
ファイルダウンロードモジュール。
"""
import os
import re
import logging
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# ファイル名として使えない文字を置換
_INVALID_CHARS_RE = re.compile(r'[\\/*?:"<>|]')


def _sanitize_filename(name: str) -> str:
    """ファイル名に使えない文字をアンダースコアに置換する"""
    return _INVALID_CHARS_RE.sub("_", name).strip()


def _filename_from_response(resp: requests.Response, fallback: str) -> str:
    """
    Content-Disposition ヘッダーからファイル名を取得する。
    取得できない場合は fallback を返す。
    """
    cd = resp.headers.get("Content-Disposition", "")
    if cd:
        # filename*=UTF-8''... (RFC 5987)
        m = re.search(r"filename\*=UTF-8''([^;]+)", cd, re.IGNORECASE)
        if m:
            from urllib.parse import unquote
            return _sanitize_filename(unquote(m.group(1)))
        # filename="..."
        m = re.search(r'filename="?([^";\r\n]+)"?', cd)
        if m:
            return _sanitize_filename(m.group(1).strip())
    return fallback


def download_file(
    url: str,
    dest_dir: str | Path,
    preferred_filename: str = "",
    timeout: int = 60,
    chunk_size: int = 8192,
) -> Path:
    """
    指定URLのファイルをダウンロードして保存する。

    Args:
        url: ダウンロードURL
        dest_dir: 保存先ディレクトリ
        preferred_filename: 優先使用するファイル名（指定がなければサーバーから取得）
        timeout: タイムアウト秒数
        chunk_size: チャンクサイズ（バイト）

    Returns:
        保存したファイルのPathオブジェクト

    Raises:
        requests.RequestException: ダウンロード失敗時
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f"ダウンロード開始: {url}")
    with requests.get(url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()

        # ファイル名決定（preferred > Content-Disposition > URLのパス末尾）
        if preferred_filename:
            filename = _sanitize_filename(preferred_filename)
        else:
            fallback = _sanitize_filename(url.split("?")[0].split("/")[-1]) or "download"
            filename = _filename_from_response(resp, fallback)

        filepath = dest_dir / filename
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

    size_kb = filepath.stat().st_size / 1024
    logger.info(f"ダウンロード完了: {filepath} ({size_kb:.1f} KB)")
    return filepath
