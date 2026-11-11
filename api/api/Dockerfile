FROM python:3.12-alpine

# 環境変数の設定 (Pythonの標準出力のバッファリング無効化など)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# MySQLクライアント（mysqlclient）のビルド等に必要なシステムパッケージをインストール
# 軽量なAlpine環境ではビルドツールを明示的に入れる必要があります
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconfig \
    python3-dev \
    bash \
    zlib-dev \
    libjpeg-turbo-dev \
    freetype-dev

# 依存関係ファイルのコピー
COPY requirements.txt /app/

# pipのアップグレードおよび依存関係のインストール
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ローカルのソースコードはdocker-compose.ymlのvolumesでマウントされます
# サーバープロセス起動はcomposeのcommandで行います
WORKDIR /app/v1.0

EXPOSE 8000
