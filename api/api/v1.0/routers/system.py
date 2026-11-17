import os
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session
from database import get_db_path, get_session
from crud import get_records

router = APIRouter()

@router.get("/")
def read_root():
    db_path = get_db_path()
    return {
        "status": "ok",
        "service": "oyama_city_open_data_api",
        "endpoints_count": 39,
        "db_ready": os.path.exists(db_path)
    }

@router.get("/sys_datasets")
def get_sys_datasets(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "sys_datasets", filters=filters, q=q, limit=limit, offset=offset)

@router.get("/sys_files")
def get_sys_files(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "sys_files", filters=filters, q=q, limit=limit, offset=offset)

@router.get("/sys_columns")
def get_sys_columns(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "sys_columns", filters=filters, q=q, limit=limit, offset=offset)
