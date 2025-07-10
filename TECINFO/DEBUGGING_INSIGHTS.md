# FPGAスクレイピングプロジェクト デバッグ知見集

## プロジェクト概要
FPGAのIPコア情報を自動収集するWebスクレイピングツールの開発において得られた知見をまとめました。

## 技術スタック
- Python 3.10
- Selenium + BeautifulSoup
- Pydantic (データモデル)
- PyYAML (設定管理)
- requests (HTTP通信)

## 主要なデバッグ事例と解決策

### 1. インポートエラーの解決

**問題**：
```python
ImportError: attempted relative import beyond top-level package
```

**原因**：
- 相対インポート（`from ..models import`）がパッケージ外で使用された
- Pythonのパス設定が不適切

**解決策**：
```python
# 各モジュールに以下を追加
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 絶対インポートに変更
from src.models.document import Document, DataSourceType
```

**学んだこと**：
- 相対インポートは慎重に使用する
- プロジェクトルートをPythonパスに明示的に追加する
- 開発時とテスト時のパス設定を統一する

### 2. Webスクレイピング戦略の改善

**問題**：
- 初期版では一般的なPDFリンクのみ取得
- FPGA関連でないドキュメントが多数混入

**改善前**：
```python
link_selectors = [
    'a[href*="pdf"]',
    'a[href*="doc"]',
    'a[title*="PDF"]',
]
```

**改善後**：
```python
link_selectors = [
    '.search-result-item a',
    '.result-item a',
    '.document-item a',
    'a[href*="guide"]',
    'a[href*="manual"]',
    'a[href*="datasheet"]',
    'a[title*="Data Sheet"]',
    'a[title*="Specification"]',
]

# FPGA関連判定機能を追加
def _is_fpga_related(self, text: str) -> bool:
    fpga_keywords = [
        'fpga', 'ip core', 'dsp', 'versal', 'zynq', 'artix', 
        'kintex', 'virtex', 'spartan', 'adaptive soc', 'acap'
    ]
    exclude_keywords = [
        'privacy', 'legal', 'terms', 'corporate', 'financial'
    ]
    # 判定ロジック
```

**結果**：
- 取得ドキュメント数：25件 → 56件
- FPGA関連度：大幅改善
- 分類精度：向上

### 3. Seleniumの最適化

**問題**：
- 初期読み込み時間が長い
- ヘッドレスモードでの安定性不足

**最適化**：
```python
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

# 待機戦略の改善
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)
time.sleep(5)  # 動的コンテンツの読み込み待機
```

**学んだこと**：
- ヘッドレスモードでは適切なオプション設定が重要
- 動的コンテンツの読み込み完了を適切に待機する
- WebDriverManagerを使用してドライバー管理を自動化

### 4. データ構造の設計

**問題**：
- 初期のシンプルなJSON構造では拡張性が低い

**改善前**：
```json
{
  "name": "document name",
  "url": "URL"
}
```

**改善後**：
```python
class Document(BaseModel):
    name: str
    url: HttpUrl
    source: str
    source_type: DataSourceType
    category: Optional[str] = None
    fpga_series: Optional[str] = None
    file_type: Optional[str] = None
    scraped_at: datetime
    hash: str
```

**メリット**：
- 型安全性の向上
- データ検証の自動化
- 将来の拡張に対する柔軟性

### 5. 設定管理の改善

**問題**：
- ハードコーディングされたURL
- 環境に依存する設定

**解決策**：
```yaml
# config/settings.yaml
data_sources:
  xilinx:
    name: "xilinx"
    type: "web_scraping"
    strategy: "selenium"
    base_url: "https://docs.amd.com/search/all..."
    rate_limit: 2

notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    sender_password: "NAME_password"  # 環境変数推奨
```

**学んだこと**：
- 設定ファイルとコードの分離
- 環境変数を使用した機密情報の管理
- YAMLによる構造化設定

## パフォーマンス最適化

### 1. 重複排除の実装
```python
# 重複チェック
if any(doc.url == full_url for doc in documents):
    continue

# ハッシュによる重複検出
def _generate_hash(self, content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()
```

### 2. レート制限の実装
```python
# 設定ファイルで制御
rate_limit = self.config.get('rate_limit', 1)
if rate_limit > 0:
    time.sleep(rate_limit)
```

### 3. フォールバック戦略
```python
# requests → Selenium の自動フォールバック
try:
    documents = self._scrape_with_requests()
    if not documents:
        documents = self._scrape_with_selenium()
except Exception:
    documents = self._scrape_with_selenium()
```

## エラーハンドリングのベストプラクティス

### 1. 階層的なエラーハンドリング
```python
# 個別のリンク処理でのエラー
try:
    # リンク処理
except Exception as e:
    self.logger.warning(f"Error parsing link: {e}")
    continue

# スクレイパー全体でのエラー
try:
    documents = scraper.scrape_documents()
except Exception as e:
    self.logger.error(f"Error scraping {source_name}: {e}")
    results[source_name] = []
```

### 2. ログ設定の重要性
```python
# ファイルとコンソールの両方にログ出力
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler = logging.FileHandler(log_file, encoding='utf-8')
console_handler = logging.StreamHandler()
```

## テスト戦略

### 1. 単体テスト
```python
def test_fpga_series_extraction(self):
    scraper = XilinxScraper(self.config)
    self.assertEqual(scraper._extract_fpga_series("Versal ACAP"), "Versal")
    self.assertEqual(scraper._extract_fpga_series("Zynq-7000"), "Zynq")
```

### 2. 統合テスト
```python
def test_basic_scraping():
    gatherer = InfoGatherer(config_path)
    results = gatherer.run(sources=['xilinx'], send_email=False)
    assert len(results) > 0
```

## 今後の改善点

### 1. API統合の準備
- 統一的なインターフェースの設計
- DataSourceTypeの拡張
- ファクトリーパターンの実装

### 2. 監視・メトリクス
- スクレイピング成功率の監視
- パフォーマンスメトリクスの収集
- 異常検知機能

### 3. 差分検出
- 前回結果との比較
- 新規ドキュメントの特定
- 更新通知の改善

## 運用上の注意点

### 1. レート制限の遵守
- サイトの利用規約を確認
- 適切な間隔でのリクエスト
- 503エラーの適切な処理

### 2. メンテナンス性
- セレクターの定期的な確認
- サイト構造変更への対応
- ログの定期的な確認

### 3. セキュリティ
- 認証情報の適切な管理
- 環境変数の使用
- HTTPSの使用

## まとめ

このプロジェクトを通じて得られた主要な知見：

1. **設計の重要性**: 拡張性を考慮した初期設計が後の開発を大幅に効率化
2. **エラーハンドリング**: 段階的なエラーハンドリングと適切なログ出力
3. **テスト駆動**: 早期のテスト実装による品質向上
4. **設定管理**: コードと設定の分離による柔軟性向上
5. **段階的改善**: 小さな改善の積み重ねが大きな成果につながる

これらの知見は、今後のAPI統合フェーズや他のスクレイピングプロジェクトにも活用できる貴重な資産となります。
