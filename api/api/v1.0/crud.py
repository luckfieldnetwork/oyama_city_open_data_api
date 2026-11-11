import os
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from sqlmodel import Session, text
from database import get_db_path

import logging
import os
import re
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from sqlmodel import Session, text
from database import get_db_path

logger = logging.getLogger(__name__)

# テーブル名・カラム名に使用可能な識別子の正規表現パターン
IDENTIFIER_RE = re.compile(r"^[a-zA-Z0-9_]+$")

def get_records(
    session: Session,
    table_name: str,
    filters: Optional[Dict[str, Any]] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    # テーブル名のバリデーション
    if not table_name or not IDENTIFIER_RE.match(table_name):
        raise HTTPException(status_code=400, detail="Invalid table name.")

    db_path = get_db_path()
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at path: {db_path}")
        raise HTTPException(
            status_code=500,
            detail="Database service temporarily unavailable."
        )

    try:
        # テーブルの有効なカラム名一覧を取得（ホワイトリスト検証用）
        col_res = session.exec(text(f'PRAGMA table_info("{table_name}")')).fetchall()
        valid_columns = {col[1] for col in col_res}
        if not valid_columns:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' does not exist.")

        query_str = f'SELECT * FROM "{table_name}"'
        params = {}
        where_clauses = []

        # カラム指定フィルター（完全一致）
        if filters:
            param_idx = 0
            for k, v in filters.items():
                if v is not None and v != "":
                    # カラム名の検証（正規表現およびテーブルのカラム存在チェック）
                    if not IDENTIFIER_RE.match(k) or k not in valid_columns:
                        continue
                    param_key = f"filter_{param_idx}"
                    where_clauses.append(f'"{k}" = :{param_key}')
                    params[param_key] = v
                    param_idx += 1

        # キーワード検索（q）：テーブル内の全カラムに対して部分一致
        if q and q.strip():
            q_clauses = []
            for j, col_name in enumerate(valid_columns):
                q_key = f"q_param_{j}"
                q_clauses.append(f'"{col_name}" LIKE :{q_key}')
                params[q_key] = f"%{q.strip()}%"
            if q_clauses:
                where_clauses.append("(" + " OR ".join(q_clauses) + ")")

        if where_clauses:
            query_str += " WHERE " + " AND ".join(where_clauses)

        # ページネーション (limit上限も念のためガード)
        safe_limit = min(max(limit, 1), 1000) if limit is not None else 50
        query_str += " LIMIT :limit"
        params["limit"] = safe_limit

        if offset is not None and offset > 0:
            query_str += " OFFSET :offset"
            params["offset"] = offset

        result = session.exec(text(query_str), params=params)
        rows = result.mappings().all()
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error on table '{table_name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while querying the database."
        )

