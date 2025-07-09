# FPGA IP Document Scraper

FPGAのIPコアに関するドキュメントを自動的に収集するWebスクレイピングツールです。

## 機能

- **マルチソース対応**: Xilinx、Altera、arXivから自動でドキュメント収集
- **Webスクレイピング**: XilinxとAlteraのドキュメントサイトからIPコア情報を収集
- **API統合**: arXiv APIによる学術論文の自動収集
- **オブジェクト指向設計**: 新しいスクレイパーを簡単に追加可能
- **柔軟な戦略**: requests + BeautifulSoupからSeleniumまで自動フォールバック
- **設定可能な取得件数**: ソースごとにmax_resultsを個別設定
- **結果保存**: JSON形式でドキュメント情報を保存
- **環境変数対応**: セキュアなメール認証情報管理
- **メール通知**: 収集結果をメールで通知
- **ログ管理**: 詳細なログ出力
- **統計情報**: 収集結果の統計を表示

## プロジェクト構造

```
InfoGetter/
├── src/
│   ├── main.py              # メインスクリプト
│   ├── models/              # データモデル
│   │   └── document.py      # ドキュメントモデル
│   ├── scrapers/            # スクレイパー実装
│   │   ├── base_scraper.py  # 基底クラス
│   │   ├── xilinx_scraper.py # Xilinxスクレイパー
│   │   ├── altera_scraper.py # Alteraスクレイパー
│   │   └── arxiv_scraper.py  # arXivスクレイパー
│   └── utils/               # ユーティリティ
│       ├── email_sender.py  # メール送信
│       └── file_handler.py  # ファイル操作
├── config/
│   ├── settings.yaml        # メイン設定ファイル
│   ├── email_credentials.yaml # メール認証情報（.gitignore推奨）
│   └── recipients.yaml      # 受信者リスト（.gitignore推奨）
├── test/                    # テストスクリプト
├── logs/                    # ログファイル出力先
├── results/                 # JSON結果出力先
├── TECINFO/                 # 技術文書・開発知見
├── requirements.txt         # 依存関係
└── README.md               # このファイル
```

## インストール

1. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

2. 設定ファイルを編集:
```yaml
# config/settings.yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    recipients_file: "config/recipients.yaml"
    credentials_file: "config/email_credentials.yaml"
```

3. メール認証情報を設定（推奨: 環境変数を使用）:
```bash
# 環境変数での設定（推奨）
export EMAIL_SENDER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

または設定ファイルで：
```yaml
# config/email_credentials.yaml
email:
  sender: "your-email@gmail.com"
  password: "your-app-password"  # Gmailアプリパスワードを使用

# config/recipients.yaml  
recipients:
  - "recipient@example.com"
```

## 使用方法

### 基本的な使用

```bash
python src/main.py
```

### オプション

```bash
# 特定のソースのみスクレイピング
python src/main.py --sources xilinx

# メール通知を無効にして実行
python src/main.py --no-email

# カスタム設定ファイルを指定
python src/main.py --config path/to/config.yaml
```

### プログラムからの使用

```python
from src.main import InfoGatherer

# 初期化
gatherer = InfoGatherer('config/settings.yaml')

# スクレイピング実行
results = gatherer.run(sources=['xilinx', 'altera'])

# 結果の確認
for source, documents in results.items():
    print(f"{source}: {len(documents)} documents found")
```

## 設定

### データソース設定

```yaml
data_sources:
  xilinx:
    name: "xilinx"
    type: "web_scraping"
    strategy: "selenium"  # requests または selenium
    base_url: "https://docs.amd.com/search/all"
    rate_limit: 2  # リクエスト間隔（秒）
    max_results: 5  # 取得する最大件数
    search_params:
      query: "DSP"
      document_types: ["Data Sheet", "User Guides & Manuals"]
      product_types: ["IP Cores (Adaptive SoC & FPGA)"]
```

### 通知設定

#### configフォルダ構成

```
config/
├── settings.yaml       　　 # メイン設定ファイル
├── email_credentials.yaml 　# メール送信用の認証情報（.gitignore推奨）
└── recipients.yaml          # メール受信者リスト　(.gitignore推奨)
```

設定例：

```yaml
# config/settings.yaml
# 通知設定
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    recipients_file: "config/recipients.yaml"
    credentials_file: "config/email_credentials.yaml"

# config/settings.yaml  
data_sources:
  xilinx:
    name: "xilinx"
    type: "web_scraping"
    strategy: "selenium"
    base_url: "https://docs.amd.com/search/all"
    rate_limit: 2
    max_results: 5  # 取得する最大件数
    search_params:
      query: "DSP"
      document_types: ["Data Sheet", "User Guides & Manuals"]
      product_types: ["IP Cores (Adaptive SoC & FPGA)"]
  
  altera:
    name: "altera"
    type: "web_scraping"
    strategy: "selenium"
    base_url: "https://www.intel.com/content/www/us/en/products/details/fpga/stratix/10/docs.html"
    rate_limit: 2
    max_results: 10  # 取得する最大件数
    search_params:
      query: "DSP"
      sort: "Relevancy"

  arxiv:
    name: "arxiv"
    type: "api"
    base_url: "http://export.arxiv.org/api/query"
    rate_limit: 1
    max_results: 10  # 各カテゴリから取得する最大件数
    categories: ["cs.AR", "cs.AI"]  # Hardware Architecture, Artificial Intelligence

# config/email_credentials.yaml
email:
  sender: "NAME@gmail.com"
  password: "password"  # アプリパスワードを使用することを推奨
# config/recipients.yaml
recipients:
  - "NAME@outlook.jp"

```

## 出力形式

収集されたドキュメント情報は以下の形式でJSONファイルに保存されます：

```json
{
  "scan_info": {
    "timestamp": "2025-07-08T10:30:00",
    "total_sources": 2,
    "total_documents": 15
  },
  "sources": {
    "xilinx": {
      "search_url": "https://docs.amd.com/search/all?query=DSP&value-filters=...",
      "document_count": 8,
      "documents": [
        {
          "name": "Versal ACAP DSP Engine User Guide",
          "url": "https://docs.amd.com/...",
          "source": "xilinx",
          "source_type": "DataSourceType.WEB_SCRAPING",
          "search_url": "https://docs.amd.com/search/all?query=DSP&value-filters=...",
          "category": "User Guide",
          "file_type": "pdf",
          "api_metadata": null
        }
      ]
    },
    "altera": {
      "search_url": "https://www.intel.com/content/www/us/en/products/details/fpga/stratix/10/docs.html?q=DSP&s=Relevancy",
      "document_count": 7,
      "documents": [
        {
          "name": "DSP Builder (Advanced Blockset): Handbook",
          "url": "https://www.intel.com/...",
          "source": "altera",
          "source_type": "DataSourceType.WEB_SCRAPING",
          "search_url": "https://www.intel.com/content/www/us/en/products/details/fpga/stratix/10/docs.html?q=DSP&s=Relevancy",
          "category": "Handbook",
          "file_type": "pdf",
          "api_metadata": null
        }
      ]
    }
  }
}
```

### JSONフィールドの説明

- **scan_info**: スキャン全体の情報
  - `timestamp`: スキャン実行時刻
  - `total_sources`: 処理したソース数
  - `total_documents`: 取得したドキュメント総数

- **sources**: ソース別のドキュメント情報
  - `search_url`: 検索に使用したURL
  - `document_count`: 取得したドキュメント数
  - `documents`: ドキュメント配列
    - `name`: ドキュメント名
    - `url`: ドキュメントURL
    - `source`: ソース名（xilinx, altera）
    - `source_type`: ソースタイプ（web_scraping, rest_api, rss_feed）
    - `search_url`: 検索に使用したURL
    - `category`: カテゴリ（User Guide, Data Sheet, IP Core等）
    - `file_type`: ファイルタイプ（pdf, html等）
    - `api_metadata`: API固有のメタデータ（通常null）

## テスト

### 基本テスト
```bash
# 基本スクレイピングテスト
python test/test_scrapers.py

# 最大結果数設定テスト
python test/test_max_results.py

# 環境変数確認テスト
python test/test_env_check.py
```

### 個別コンポーネントテスト  
```bash
# Xilinxスクレイパーテスト
python test/test_selenium_xilinx.py

# Alteraスクレイパーテスト  
python test/test_selenium_altera.py

# arXiv APIテスト
python test/test_arxiv.py
```

## 新しいスクレイパーの追加

1. `src/scrapers/` に新しいスクレイパークラスを作成
2. `BaseScraper` を継承
3. 必要なメソッドを実装
4. `src/main.py` にスクレイパーを登録

```python
# src/scrapers/new_scraper.py
from .base_scraper import BaseScraper
from ..models.document import Document, DataSourceType

class NewScraper(BaseScraper):
    def get_source_type(self) -> DataSourceType:
        return DataSourceType.WEB_SCRAPING
    
    def scrape_documents(self) -> List[Document]:
        # 実装
        pass
```

## トラブルシューティング

### Seleniumエラー

ChromeDriverが見つからない場合：
```bash
pip install webdriver-manager
```

### メール送信エラー

**環境変数を使用した設定（推奨）:**
```bash
export EMAIL_SENDER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

**または設定ファイルを使用:**
Gmailを使用する場合はアプリパスワードを設定してください：

1. Google アカウントの2段階認証を有効化
2. アプリパスワードを生成
3. `config/email_credentials.yaml` に設定:
```yaml
email:
  sender: "your-email@gmail.com"  
  password: "your-app-password"  # 16文字のアプリパスワード
```

### ログ確認

ログファイルは `logs/scraper.log` に出力されます：

```bash
tail -f logs/scraper.log
```

## 追加ドキュメント

このプロジェクトには詳細な技術文書が `TECINFO/` ディレクトリに含まれています：

### 開発関連文書
- [📚 開発知見とベストプラクティス](TECINFO/DEVELOPMENT_INSIGHTS.md) - プロジェクト開発で得られた知見と設計思想
- [🎯 システム最終状況](TECINFO/SYSTEM_STATUS_FINAL.md) - 本番環境準備完了状況とテスト結果
- [📋 技術情報まとめ](TECINFO/TECINFO.md) - 基本的な技術情報とURL一覧

### トラブルシューティング
- [🔧 WebDriver関連のトラブルシューティング](TECINFO/WEBDRIVER_TROUBLESHOOTING.md) - ブラウザドライバーの問題解決
- [🐛 デバッグ知見](TECINFO/DEBUGGING_INSIGHTS.md) - 開発中に遭遇した問題と解決策
- [⚙️ WebDriver技術詳細](TECINFO/WEBDRIVER_TECHNICAL_INSIGHTS.md) - WebDriverの技術的な詳細情報

### 運用ガイド
- [⏰ タスクスケジューラーガイド](TECINFO/TASK_SCHEDULER_GUIDE.md) - Windows環境での自動実行設定
- [🚀 タスクスケジューラークイックスタート](TECINFO/TASK_SCHEDULER_QUICKSTART.md) - 簡単セットアップガイド

これらの文書は開発・運用・トラブルシューティングに役立つ詳細な情報を提供しています。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能要求は、GitHubのIssuesでお知らせください。
