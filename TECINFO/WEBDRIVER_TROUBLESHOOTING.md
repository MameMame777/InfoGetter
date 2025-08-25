# WebDriver エラー解決ガイド

**OSError: [WinError 193] %1 は有効な Win32 アプリケーションではありません** エラーが発生した場合の対処法

## 📋 症状
- Seleniumを使用したスクレイピング時にこのエラーが発生
- ChromeDriverまたはGeckoDriverが正常に動作しない
- WebDriverの初期化でエラーが発生

## 🔧 解決手順

### 1. 一括修復ツールの使用（推奨）

最も簡単な方法：
```batch
# バッチファイルをダブルクリック
webdriver_fix.bat
```

または

```powershell
# PowerShellで実行
python webdriver_master.py
```

### 2. 手動修復手順

#### ステップ1: 基本診断
```powershell
python test_webdriver.py
```

#### ステップ2: Chrome修復
```powershell
python webdriver_repair.py
```

#### ステップ3: Firefox代替設定（Chrome修復が失敗した場合）
```powershell
python firefox_setup.py
```

## 🛠️ 提供されるツール

### `webdriver_master.py`
- 統合診断・修復ツール
- メニュー形式で操作
- 全自動修復モードあり

### `webdriver_repair.py`
- ChromeDriverの問題を自動修復
- キャッシュクリア
- webdriver-manager再インストール
- 手動ChromeDriverダウンロード

### `firefox_setup.py`
- Firefox WebDriverの設定
- GeckoDriver自動インストール
- 設定ファイル作成
- サンプルコード生成

### `test_webdriver.py`
- 基本的な診断
- システム情報表示
- WebDriverの動作確認

## 📝 設定ファイルでのブラウザー選択

### Chrome使用（デフォルト）
```yaml
data_sources:
  xilinx:
    browser:
      type: "chrome"
      headless: true
```

### Firefox使用
```yaml
data_sources:
  altera:
    browser:
      type: "firefox"
      headless: true
```

### カスタムドライバーパス指定
```yaml
data_sources:
  xilinx:
    browser:
      type: "chrome"
      chromedriver_path: "C:/path/to/chromedriver.exe"
```

## 🔍 よくある問題と解決策

### 問題1: ChromeDriverバージョン不一致
**症状**: SessionNotCreatedException
**解決策**: 
```powershell
python webdriver_repair.py
```

### 問題2: WebDriverキャッシュ破損
**症状**: FileNotFoundError, OSError
**解決策**: キャッシュクリア
```powershell
# 自動実行
python webdriver_repair.py

# 手動削除
rmdir /s C:\Users\%USERNAME%\.wdm
rmdir /s C:\Users\%USERNAME%\.cache\selenium
```

### 問題3: セキュリティソフトの干渉
**症状**: WebDriverが起動しない
**解決策**:
1. セキュリティソフトの除外設定に追加
2. Firefoxを代替ブラウザとして使用
```powershell
python firefox_setup.py
```

### 問題4: 管理者権限の問題
**症状**: Permission denied
**解決策**: PowerShellを管理者権限で実行

## 🧪 修復後のテスト

### スクレイパーテスト
```powershell
python test_scrapers_after_fix.py
```

### arXiv統合テスト
```powershell
python test_arxiv.py
```

### 完全なスクレイピングテスト
```powershell
python -m src.main
```

## 📞 追加サポート

### ログファイルの確認
- `logs/scraper.log`
- コンソール出力を保存して確認

### 環境情報の収集
```powershell
python -c "
import platform, sys
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Architecture: {platform.architecture()}')
"
```

### 手動ChromeDriverダウンロード
1. https://chromedriver.chromium.org/
2. Chromeバージョンに対応するDriverをダウンロード
3. 設定ファイルでパスを指定

## ✅ 成功確認

修復が成功すると以下のメッセージが表示されます：
```
🎉 すべてのスクレイパーが正常に動作しています！
```

## 🔄 代替ブラウザ設定

Chrome修復が困難な場合、Firefoxを代替として使用：

1. Firefox設定ツール実行:
```powershell
python firefox_setup.py
```

2. 設定ファイル更新:
```yaml
default_browser:
  type: "firefox"
```

3. テスト実行:
```powershell
python test_scrapers_after_fix.py
```

これで WebDriver の問題は解決されるはずです！
