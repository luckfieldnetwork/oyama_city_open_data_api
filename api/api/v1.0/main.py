import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import system, datasets

root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(
    title="小山市オープンデータ API (非公式)",
    description="小山市が公開しているオープンデータカタログのデータを正規化・集約して提供するREST APIです。本APIは有志による非公式プロジェクトです。",
    version="1.0.0",
    license_info={
        "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "url": "https://creativecommons.org/licenses/by/4.0/deed.ja",
    },
    root_path=root_path,
)

# オープンデータAPIとして外部フロントエンドからの呼び出しを許可 (CORS設定)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(datasets.router)
