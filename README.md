# FPGA IP Document Scraper

FPGAのIPコアに関するドキュメントを自動的に収集するWebスクレイピングツールです。

## 機能

- **Webスクレイピング**: XilinxとAlteraのドキュメントサイトからIPコア情報を収集
- **オブジェクト指向設計**: 新しいスクレイパーを簡単に追加可能
- **柔軟な戦略**: requests + BeautifulSoupからSeleniumまで自動フォールバック
- **結果保存**: JSON形式でドキュメント情報を保存
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
│   │   └── altera_scraper.py # Alteraスクレイパー
│   └── utils/               # ユーティリティ
│       ├── email_sender.py  # メール送信
│       └── file_handler.py  # ファイル操作
├── config/
│   └── settings.yaml        # 設定ファイル
├── test/
│   └── test_scrapers.py     # テストスクリプト
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
    sender_email: "your_email@gmail.com"
    sender_password: "your_app_password"
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
    base_url: "https://docs.amd.com/search/all?query=Versal"
    rate_limit: 2  # リクエスト間隔（秒）
```

### 通知設定

```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "your_email@gmail.com"
    sender_password: "your_app_password"  # 環境変数EMAIL_PASSWORDからも取得可能
    recipients:
      - "recipient@example.com"
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
      "document_count": 8,
      "documents": [
        {
          "name": "Versal ACAP DSP Engine User Guide",
          "url": "https://docs.amd.com/...",
          "source": "xilinx",
          "category": "User Guide",
          "fpga_series": "Versal",
          "file_type": "pdf",
          "scraped_at": "2025-07-08T10:30:00",
          "hash": "abc123..."
        }
      ]
    }
  }
}
```

## テスト

```bash
python -m pytest test/test_scrapers.py -v
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

Gmailを使用する場合はアプリパスワードを設定してください：
1. Google アカウントの2段階認証を有効化
2. アプリパスワードを生成
3. 設定ファイルまたは環境変数 `EMAIL_PASSWORD` に設定

### ログ確認

ログファイルは `logs/scraper.log` に出力されます：
```bash
tail -f logs/scraper.log
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能要求は、GitHubのIssuesでお知らせください。
