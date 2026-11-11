#!/home/code4oyama/.env/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wsgiref.handlers import CGIHandler

    # a2wsgi のバージョン違いに対応
    try:
        from a2wsgi import ASGIMiddleware
    except ImportError:
        from a2wsgi import ASGItoWSGI as ASGIMiddleware

    from fastapi.openapi.docs import get_swagger_ui_html
    from main import app

    # 1. FastAPI のプレフィックス判定誤認を防ぐため root_path を強制クリア
    app.root_path = ""

    # 2. /docs へのアクセス時に明示的に /v1.0/openapi.json を指定して Swagger UI を生成
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/docs"]

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/v1.0/openapi.json",
            title=app.title + " - Swagger UI",
        )

    # 3. OpenAPI 仕様書内の servers を /v1.0 に設定（Swagger UIの「Try it out」用）
    orig_openapi = app.openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = orig_openapi()
        schema["servers"] = [{"url": "/v1.0"}]
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

    raw_wsgi_app = ASGIMiddleware(app)

    # さくらのCGI環境用に SCRIPT_NAME / PATH_INFO を補正するラッパー
    def cgi_wsgi_app(environ, start_response):
        # SCRIPT_NAME を空にして、FastAPI に PATH_INFO だけで判定させる
        environ["SCRIPT_NAME"] = ""

        # PATH_INFO を抽出（未設定の場合は REQUEST_URI から補完）
        path_info = environ.get("PATH_INFO")
        if not path_info:
            req_uri = environ.get("REQUEST_URI", "")
            path_info = req_uri.split("?")[0] if req_uri else "/"

        if not path_info.startswith("/"):
            path_info = "/" + path_info

        # プレフィックスが含まれている場合は除去して FastAPI ルートにマッチさせる
        if path_info.startswith("/v1.0"):
            path_info = path_info[len("/v1.0"):] or "/"
        elif path_info.startswith("/api/v1.0"):
            path_info = path_info[len("/api/v1.0"):] or "/"

        environ["PATH_INFO"] = path_info

        return raw_wsgi_app(environ, start_response)

    if __name__ == "__main__":
        CGIHandler().run(cgi_wsgi_app)

except Exception as e:
    # サーバーのエラーログ（Apache error.log）にスタックトレースを出力
    traceback.print_exc(file=sys.stderr)

    # DEBUG モードが有効な場合のみ画面にスタックトレースを表示
    debug_mode = os.getenv("DEBUG", "").lower() in ("1", "true")
    if debug_mode:
        sys.stdout.write("Status: 500 Internal Server Error\r\n")
        sys.stdout.write("Content-Type: text/plain; charset=utf-8\r\n\r\n")
        sys.stdout.write("=== Python Execution Error (Debug Mode) ===\n")
        traceback.print_exc(file=sys.stdout)
    else:
        sys.stdout.write("Status: 500 Internal Server Error\r\n")
        sys.stdout.write("Content-Type: application/json; charset=utf-8\r\n\r\n")
        sys.stdout.write('{"detail": "Internal Server Error"}\n')

