#!/usr/bin/env python3
"""代替ブラウザ（Firefox）設定スクリプト"""

import os
import sys
import platform
import subprocess
import requests
import zipfile
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def print_header(title):
    """ヘッダーを表示"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_firefox_installation():
    """Firefoxのインストール状況を確認"""
    print_header("Firefox インストール確認")
    
    try:
        if platform.system() == "Windows":
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
            
            for firefox_path in firefox_paths:
                if os.path.exists(firefox_path):
                    print(f"✅ Firefox発見: {firefox_path}")
                    
                    # バージョン確認
                    try:
                        result = subprocess.run([firefox_path, "--version"], 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            version = result.stdout.strip()
                            print(f"✅ Firefox バージョン: {version}")
                            return True, firefox_path
                    except Exception as e:
                        print(f"⚠️ Firefoxバージョン確認エラー: {e}")
                        return True, firefox_path  # パスは有効
            
            print("❌ Firefoxが見つかりませんでした")
            return False, None
        else:
            print(f"⚠️ {platform.system()}はサポートされていません")
            return False, None
            
    except Exception as e:
        print(f"❌ Firefox確認エラー: {e}")
        return False, None

def install_geckodriver():
    """GeckoDriverをインストール"""
    print_header("GeckoDriver インストール")
    
    try:
        # webdriver-managerでGeckoDriverをインストール
        print("🔄 webdriver-manager経由でGeckoDriverをインストール中...")
        
        from webdriver_manager.firefox import GeckoDriverManager
        
        driver_path = GeckoDriverManager().install()
        print(f"✅ GeckoDriver取得成功: {driver_path}")
        
        # ファイル確認
        if os.path.exists(driver_path):
            file_size = os.path.getsize(driver_path)
            print(f"✅ ファイル確認: {file_size} bytes")
            
            if file_size == 0:
                print("❌ ファイルサイズが0です")
                return False, None
            
            return True, driver_path
        else:
            print(f"❌ ファイルが存在しません: {driver_path}")
            return False, None
        
    except Exception as e:
        print(f"❌ GeckoDriverインストールエラー: {e}")
        
        # 手動ダウンロードを試行
        print("🔄 手動ダウンロードを試行中...")
        return download_geckodriver_manually()

def download_geckodriver_manually():
    """GeckoDriverを手動でダウンロード"""
    print_header("GeckoDriver 手動ダウンロード")
    
    try:
        # GitHub APIから最新リリース情報を取得
        api_url = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
        
        print("📥 最新バージョン情報を取得中...")
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API呼び出し失敗: HTTP {response.status_code}")
            return False, None
        
        release_data = response.json()
        version = release_data["tag_name"]
        print(f"📥 最新GeckoDriverバージョン: {version}")
        
        # プラットフォーム確認
        if platform.system() == "Windows":
            if platform.architecture()[0] == "64bit":
                platform_suffix = "win64.zip"
            else:
                platform_suffix = "win32.zip"
        else:
            print(f"❌ サポートされていないプラットフォーム: {platform.system()}")
            return False, None
        
        # ダウンロードURLを検索
        download_url = None
        for asset in release_data["assets"]:
            if platform_suffix in asset["name"]:
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            print(f"❌ 対応するダウンロードファイルが見つかりません: {platform_suffix}")
            return False, None
        
        print(f"📥 ダウンロードURL: {download_url}")
        
        # ダウンロード先ディレクトリ作成
        download_dir = Path.home() / "geckodriver_manual"
        download_dir.mkdir(exist_ok=True)
        
        zip_path = download_dir / "geckodriver.zip"
        driver_path = download_dir / "geckodriver.exe"
        
        # 既存ファイルがあれば削除
        if zip_path.exists():
            zip_path.unlink()
        if driver_path.exists():
            driver_path.unlink()
        
        # ダウンロード実行
        print("📥 GeckoDriverをダウンロード中...")
        response = requests.get(download_url, timeout=30)
        
        if response.status_code == 200:
            with open(zip_path, "wb") as f:
                f.write(response.content)
            print(f"✅ ダウンロード完了: {zip_path}")
            
            # ZIPファイルを展開
            print("📦 ZIPファイルを展開中...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            if driver_path.exists():
                print(f"✅ GeckoDriver展開完了: {driver_path}")
                return True, str(driver_path)
            else:
                print("❌ GeckoDriverの展開に失敗")
                return False, None
        else:
            print(f"❌ ダウンロード失敗: HTTP {response.status_code}")
            return False, None
        
    except Exception as e:
        print(f"❌ 手動ダウンロードエラー: {e}")
        return False, None

def test_firefox_webdriver(geckodriver_path):
    """Firefox WebDriverをテスト"""
    print_header("Firefox WebDriver テスト")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        
        print(f"🧪 テスト対象GeckoDriver: {geckodriver_path}")
        
        # ファイル確認
        if not os.path.exists(geckodriver_path):
            print(f"❌ ファイルが存在しません: {geckodriver_path}")
            return False
        
        file_size = os.path.getsize(geckodriver_path)
        print(f"📊 ファイルサイズ: {file_size} bytes")
        
        if file_size == 0:
            print("❌ ファイルサイズが0です")
            return False
        
        # Firefox Optionsの設定
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-dev-shm-usage')
        
        # WebDriverサービスの作成
        service = Service(geckodriver_path)
        
        # WebDriverの起動テスト
        print("🚀 Firefox WebDriverを起動中...")
        driver = webdriver.Firefox(service=service, options=firefox_options)
        
        print("✅ Firefox WebDriver起動成功")
        
        # 簡単なテスト
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ テストページ取得成功: {title}")
        
        driver.quit()
        print("✅ Firefox WebDriver終了成功")
        
        print(f"\n🎉 成功！Firefox WebDriverが利用可能です")
        print(f"GeckoDriverパス: {geckodriver_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firefox WebDriverテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_firefox_scraper_config():
    """Firefox用のスクレイパー設定を作成"""
    print_header("Firefox用設定作成")
    
    try:
        # 設定ファイルのパス
        config_dir = Path(project_root) / "config"
        firefox_config_path = config_dir / "firefox_settings.yaml"
        
        # Firefox設定の内容
        firefox_config = """# Firefox WebDriver設定
browser:
  type: "firefox"
  headless: true
  options:
    - "--no-sandbox"
    - "--disable-dev-shm-usage"
    - "--disable-extensions"
  
  # GeckoDriverのパス（手動設定する場合）
  # geckodriver_path: "C:/path/to/geckodriver.exe"
  
webdriver:
  # webdriver-managerを使用（推奨）
  use_manager: true
  
  # タイムアウト設定
  page_load_timeout: 30
  implicit_wait: 10
  
# スクレイピング設定
scraping:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
  request_delay: 2.0
  retry_count: 3
"""
        
        # 設定ファイルを作成
        config_dir.mkdir(exist_ok=True)
        
        with open(firefox_config_path, 'w', encoding='utf-8') as f:
            f.write(firefox_config)
        
        print(f"✅ Firefox設定ファイル作成: {firefox_config_path}")
        
        return True, firefox_config_path
        
    except Exception as e:
        print(f"❌ 設定ファイル作成エラー: {e}")
        return False, None

def create_firefox_scraper_example():
    """Firefox用スクレイパーのサンプルコードを作成"""
    print_header("Firefox スクレイパー サンプル作成")
    
    try:
        # サンプルファイルのパス
        example_path = Path(project_root) / "firefox_scraper_example.py"
        
        # サンプルコード
        example_code = '''#!/usr/bin/env python3
"""Firefox WebDriverを使用したスクレイパーのサンプル"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

def create_firefox_driver(headless=True, custom_geckodriver_path=None):
    """Firefox WebDriverを作成"""
    try:
        # Firefox Optionsの設定
        firefox_options = Options()
        
        if headless:
            firefox_options.add_argument('--headless')
        
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-dev-shm-usage')
        firefox_options.add_argument('--disable-extensions')
        
        # User-Agentの設定
        firefox_options.set_preference("general.useragent.override", 
                                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0")
        
        # GeckoDriverのパス設定
        if custom_geckodriver_path and os.path.exists(custom_geckodriver_path):
            print(f"カスタムGeckoDriverを使用: {custom_geckodriver_path}")
            service = Service(custom_geckodriver_path)
        else:
            print("webdriver-manager経由でGeckoDriverを取得")
            geckodriver_path = GeckoDriverManager().install()
            service = Service(geckodriver_path)
        
        # WebDriverの作成
        driver = webdriver.Firefox(service=service, options=firefox_options)
        
        # タイムアウト設定
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        print("✅ Firefox WebDriver作成成功")
        return driver
        
    except Exception as e:
        print(f"❌ Firefox WebDriver作成エラー: {e}")
        raise

def test_firefox_scraping():
    """Firefox WebDriverでのスクレイピングテスト"""
    driver = None
    
    try:
        print("Firefox WebDriverでのスクレイピングテストを開始...")
        
        # カスタムパスがある場合はここで指定
        # custom_path = r"C:\\Users\\YourUser\\geckodriver_manual\\geckodriver.exe"
        custom_path = None
        
        # WebDriverを作成
        driver = create_firefox_driver(headless=True, custom_geckodriver_path=custom_path)
        
        # テストページにアクセス
        print("テストページにアクセス中...")
        driver.get("https://www.google.com")
        
        # ページタイトル取得
        title = driver.title
        print(f"✅ ページタイトル: {title}")
        
        # 基本的な要素取得テスト
        search_box = driver.find_element("name", "q")
        if search_box:
            print("✅ 検索ボックス要素の取得成功")
        
        print("🎉 Firefox WebDriverでのスクレイピングテスト成功！")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("✅ WebDriver終了")

if __name__ == "__main__":
    print("Firefox WebDriver スクレイピング サンプル")
    print("=" * 50)
    
    test_firefox_scraping()
'''
        
        # サンプルファイルを作成
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_code)
        
        print(f"✅ Firefox スクレイパー サンプル作成: {example_path}")
        
        return True, example_path
        
    except Exception as e:
        print(f"❌ サンプル作成エラー: {e}")
        return False, None

def main():
    """メイン処理"""
    print("Firefox WebDriver セットアップツール")
    print("=" * 60)
    print("このツールはFirefoxをChromeの代替として設定します")
    
    # システム情報表示
    print_header("システム情報")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"アーキテクチャ: {platform.architecture()}")
    print(f"Python: {platform.python_version()}")
    
    # Step 1: Firefox確認
    print("\n🔧 Step 1: Firefox インストール確認")
    firefox_installed, firefox_path = check_firefox_installation()
    
    if not firefox_installed:
        print("❌ Firefoxがインストールされていません")
        print("📥 Firefoxをダウンロード: https://www.mozilla.org/firefox/")
        return False
    
    # Step 2: GeckoDriverインストール
    print("\n🔧 Step 2: GeckoDriver インストール")
    geckodriver_success, geckodriver_path = install_geckodriver()
    
    if not geckodriver_success:
        print("❌ GeckoDriverのインストールに失敗")
        return False
    
    # Step 3: Firefox WebDriverテスト
    print("\n🔧 Step 3: Firefox WebDriver テスト")
    if not test_firefox_webdriver(geckodriver_path):
        print("❌ Firefox WebDriverテストに失敗")
        return False
    
    # Step 4: 設定ファイル作成
    print("\n🔧 Step 4: Firefox用設定作成")
    config_success, config_path = create_firefox_scraper_config()
    
    if config_success:
        print(f"✅ 設定ファイル作成成功: {config_path}")
    
    # Step 5: サンプルコード作成
    print("\n🔧 Step 5: サンプルコード作成")
    example_success, example_path = create_firefox_scraper_example()
    
    if example_success:
        print(f"✅ サンプルコード作成成功: {example_path}")
    
    # 完了メッセージ
    print_header("セットアップ完了")
    print("🎉 Firefox WebDriverのセットアップが完了しました！")
    print()
    print("次の手順:")
    print("1. 既存のスクレイパーでChromeDriverをFirefoxに変更")
    print("2. 設定ファイルでFirefoxオプションを調整")
    print("3. サンプルコードを参考にFirefox用スクレイパーを作成")
    print()
    print(f"GeckoDriverパス: {geckodriver_path}")
    print(f"設定ファイル: {config_path if config_success else '作成失敗'}")
    print(f"サンプルコード: {example_path if example_success else '作成失敗'}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Firefox WebDriverセットアップが正常に完了しました！")
        else:
            print("\n❌ セットアップに失敗しました。")
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
