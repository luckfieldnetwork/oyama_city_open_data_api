import os
from fastapi import APIRouter, Depends, Request
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
def get_sys_datasets(request: Request, session: Session = Depends(get_session)):
    return get_records(session, "sys_datasets", dict(request.query_params))

@router.get("/sys_files")
def get_sys_files(request: Request, session: Session = Depends(get_session)):
    return get_records(session, "sys_files", dict(request.query_params))

@router.get("/sys_columns")
def get_sys_columns(request: Request, session: Session = Depends(get_session)):
    return get_records(session, "sys_columns", dict(request.query_params))
