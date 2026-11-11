import os
from typing import Generator
from sqlmodel import create_engine, Session

POSSIBLE_DB_PATHS = [
    os.getenv("OYAMA_DB_PATH"),
    # さくらインターネット新環境用 (www/api/v1.0/... -> db/oyama_opendata.db)
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "db", "oyama_opendata.db")),
    # さくらインターネット旧環境用 (www/code4oyama/api/v1.0/... -> db/oyama_opendata.db)
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "db", "oyama_opendata.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "db", "oyama_opendata.db")),
    # 他の標準的な候補
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "db", "oyama_opendata.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db", "oyama_opendata.db")),
    # ローカルリポジトリ環境用 (scraping/db/oyama_opendata.db)
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scraping", "db", "oyama_opendata.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scraping", "db", "oyama_opendata.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scraping", "db", "oyama_opendata.db")),
]

def get_db_path() -> str:
    for path in POSSIBLE_DB_PATHS:
        if path and os.path.exists(path):
            return path
    return POSSIBLE_DB_PATHS[1]

def get_engine():
    db_path = get_db_path()
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
