from typing import Optional
from sqlmodel import SQLModel, Field

class SysDataset(SQLModel, table=True):
    __tablename__ = "sys_datasets"
    dataset_code: Optional[str] = Field(default=None, primary_key=True)
    title: Optional[str] = None
    table_name: Optional[str] = None
    published_date: Optional[str] = None
    contact: Optional[str] = None
    creator: Optional[str] = None
    last_checked: Optional[str] = None
    file_count: Optional[int] = None

class SysFile(SQLModel, table=True):
    __tablename__ = "sys_files"
    download_code: Optional[str] = Field(default=None, primary_key=True)
    dataset_code: Optional[str] = None
    filename: Optional[str] = None
    format: Optional[str] = None
    file_size: Optional[str] = None
    last_updated: Optional[str] = None
    local_path: Optional[str] = None
    is_downloaded: Optional[int] = None
    last_downloaded: Optional[str] = None

class SysColumn(SQLModel, table=True):
    __tablename__ = "sys_columns"
    table_name: str = Field(primary_key=True)
    column_name: str = Field(primary_key=True)
    logical_name: str
