# 小山市オープンデータ API & スクレイピングシステム (oyama_city_open_data_api)

> [!NOTE]
> 本プロジェクトは有志によって開発されている**非公式（Unofficial）**なプロジェクトです。小山市公式のAPIサービスではありません。

小山市が公開しているオープンデータカタログから各種データ（CSV等）を自動取得・正規化してSQLiteデータベースへ集約し、FastAPIによるREST APIとして提供するプロジェクトです。

---

## 📁 ディレクトリ構成

```text
oyama_city_open_data_api/
├── api/                           # APIサーバー
│   ├── docker-compose.yml         # Nginx + FastAPI コンテナ構成
│   ├── nginx/                     # リバースプロキシ設定
│   │   └── default.conf
│   └── api/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── v1.0/                  # FastAPI アプリケーション本体
│           ├── main.py            # アプリケーションエントリーポイント
│           ├── database.py        # DB接続・セッション管理
│           ├── crud.py            # データ取得クエリ処理
│           ├── models.py          # SQLModel/SQLAlchemy モデル定義
│           ├── index.cgi          # さくらインターネット等 CGI実行用ラッパー
│           ├── .htaccess          # CGIリライト設定
│           ├── routers/           # APIエンドポイントルーター
│           └── schemas/           # Pydanticスキーマ定義
├── scraping/                      # データ収集・DB構築スクリプト
│   ├── main.py                    # 月次バッチ実行スクリプト
│   ├── scraper.py                 # カタログサイトスクレイピング
│   ├── downloader.py              # ファイルダウンロード
│   ├── db_manager.py              # SQLite DB作成・データ正規化インポート
│   ├── requirements.txt           # スクレイピング依存ライブラリ
│   ├── csv/                       # ダウンロードしたCSV保存先 (.gitkeep)
│   │   └── non_csv/               # PDF/Excel等の非CSVファイル保存先 (.gitkeep)
│   ├── db/                        # 生成されたSQLite DB保存先 (.gitkeep)
│   └── doc/                       # スクレイピング用ドキュメント
├── doc/                           # 仕様書ドキュメント
│   └── db_schema.md               # 全テーブル・カラム詳細仕様書
└── README.md
```

---

## 🛠️ 機能概要

1. **データ収集バッチ (`scraping/`)**
   - 小山市オープンデータカタログサイトを巡回し、全42データセット（CSV/PDF/Excel等）の更新をチェック・ダウンロード。
   - 複数年度・複数月に分かれたCSVデータを単一のテーブルに縦結合（UNION）してインポート。
   - カラム名を英語物理名に正規化し、単一のSQLiteデータベース（`scraping/db/oyama_opendata.db`）に集約。

2. **Web API サーバー (`api/`)**
   - SQLiteデータベースをソースとし、FastAPIによってオープンデータをJSON形式で提供。
   - Swagger UI（インタラクティブなAPIドキュメント）を標準提供。
   - Docker（Nginx + FastAPI）によるコンテナ運用、または共有サーバー（さくらインターネットのCGI/WSGI環境）での運用に対応。

---

## 🚀 クイックスタート

### 1. データ収集・データベース構築 (`scraping/`)

APIを動かす前に、オープンデータを収集してSQLiteデータベースを生成します。

```powershell
# scraping ディレクトリへ移動
cd scraping

# 依存パッケージのインストール
pip install -r requirements.txt

# データ取得＆DB生成バッチの実行
python main.py
```
> 実行が完了すると、`scraping/db/oyama_opendata.db` に全データセットが集約されたデータベースが生成されます。

主なコマンドライン引数：
- `python main.py --dry-run` : 実際のダウンロードやDB更新を行わずにチェックのみ実施
- `python main.py --force` : 更新有無に関わらず全ファイルを強制再取得

---

### 2. APIサーバーの起動 (`api/`)

#### 方式 A: Docker Compose を使用する場合（推奨）

```powershell
cd api

# コンテナのビルドと起動
docker-compose up -d --build
```
起動後、ブラウザで以下のURLにアクセスします：
- **Swagger UI (APIドキュメント)**: [http://localhost/v1.0/docs](http://localhost/v1.0/docs)
- **API エンドポイント例**: [http://localhost/v1.0/datasets](http://localhost/v1.0/datasets)

#### 方式 B: ローカル Python 環境で直接起動する場合

```powershell
cd api/api

# 仮想環境の作成とライブラリインストール
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# サーバー起動 (v1.0 ディレクトリに移動して起動)
cd v1.0
uvicorn main:app --reload --port 8000
```
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 共有サーバー環境（さくらインターネット等）での運用

本プロジェクトのAPIは、さくらインターネット等のレンタルサーバー環境（Apache + CGI + Python）でも動作するように設計されています。

- `api/api/v1.0/index.cgi`: CGI環境でFastAPIを動作させるためのエントリーポイント（`a2wsgi` 経由）
- `api/api/v1.0/.htaccess`: すべてのリクエストを `index.cgi` に転送するリライト設定
- サーバー上のパス構造に応じて、`database.py` が自動的に適切なDBパスを探索します。

---

## 📖 データベース仕様

データベースに含まれる全テーブルおよびカラム定義の詳細については、[doc/db_schema.md](file:///c:/Users/ospre/work/oyama_city_open_data_api/doc/db_schema.md) を参照してください。
全42データセット、36データテーブルの物理名・論理名・データ型が記載されています。

---

## 📜 ライセンス・クレジット表記

- **オープンデータの出典・権利関係**:
  - 本システムで収集・提供しているオープンデータは、小山市公式ホームページ上の「[小山市オープンデータカタログ](https://www.city.oyama.tochigi.jp/opendata.php)」の公開データを基に加工・集約したものです。
  - 元データは [クリエイティブ・コモンズ 表示 4.0 国際 ライセンス (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.ja) の下で提供されています。
  - 出典表記例：*小山市オープンデータ（小山市）、クリエイティブ・コモンズ・ライセンス 表示4.0国際に基づき加工して作成*
- **ソースコードのライセンス**:
  - 本リポジトリのソースコードは [MIT License](https://opensource.org/licenses/MIT) の下で公開されています。

---

## ⚠️ 免責事項 (Disclaimer)

1. 本ソフトウェアおよびAPIは現状有姿（AS-IS）で提供されます。
2. 小山市ならびに本ソフトウェアの開発者は、データの正確性、網羅性、最新性、特定目的への適合性について一切の保証を行いません。
3. 利用者が本ソフトウェア、API、またはオープンデータを用いて行う一切の行為および生じた損害・トラブルについて、小山市および開発者は何らの責任も負いません。
