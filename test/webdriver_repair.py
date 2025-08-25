#!/usr/bin/env python3
"""WebDriver修復・再インストールスクリプト"""

import os
import sys
import platform
import shutil
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

def check_chrome_version():
    """Chromeのバージョンを確認"""
    print_header("Chrome バージョン確認")
    
    try:
        # Windows用のChromeバージョン確認
        if platform.system() == "Windows":
            import winreg
            
            # レジストリからChromeバージョンを取得
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon") as key:
                    version, _ = winreg.QueryValueEx(key, "version")
                    print(f"✅ Chrome バージョン: {version}")
                    return version
            except FileNotFoundError:
                pass
            
            # 別の場所を確認
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome\BLBeacon") as key:
                    version, _ = winreg.QueryValueEx(key, "version")
                    print(f"✅ Chrome バージョン: {version}")
                    return version
            except FileNotFoundError:
                pass
            
            # chrome.exeから直接確認
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    try:
                        result = subprocess.run([chrome_path, "--version"], 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            version = result.stdout.strip().split()[-1]
                            print(f"✅ Chrome バージョン: {version}")
                            return version
                    except Exception as e:
                        print(f"⚠️ Chromeバージョン取得エラー: {e}")
        
        print("❌ Chromeのバージョンを取得できませんでした")
        return None
        
    except Exception as e:
        print(f"❌ Chrome確認エラー: {e}")
        return None

def clean_webdriver_cache():
    """WebDriverキャッシュをクリア"""
    print_header("WebDriver キャッシュクリア")
    
    try:
        # webdriver-managerのキャッシュディレクトリを確認
        cache_dirs = []
        
        # ユーザーホームディレクトリ内のキャッシュ
        home = Path.home()
        possible_cache_dirs = [
            home / ".wdm",
            home / ".cache" / "selenium",
            home / "AppData" / "Local" / "selenium",
            home / "AppData" / "Roaming" / "selenium"
        ]
        
        for cache_dir in possible_cache_dirs:
            if cache_dir.exists():
                cache_dirs.append(cache_dir)
                print(f"📁 キャッシュディレクトリ発見: {cache_dir}")
        
        if not cache_dirs:
            print("ℹ️ キャッシュディレクトリが見つかりませんでした")
            return True
        
        for cache_dir in cache_dirs:
            try:
                print(f"🗑️ 削除中: {cache_dir}")
                shutil.rmtree(cache_dir)
                print(f"✅ 削除完了: {cache_dir}")
            except Exception as e:
                print(f"⚠️ 削除エラー: {cache_dir} - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ キャッシュクリアエラー: {e}")
        return False

def reinstall_webdriver_manager():
    """webdriver-managerを再インストール"""
    print_header("webdriver-manager 再インストール")
    
    try:
        # 現在のwebdriver-managerをアンインストール
        print("🔄 webdriver-manager をアンインストール中...")
        result = subprocess.run([sys.executable, "-m", "pip", "uninstall", 
                               "webdriver-manager", "-y"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ webdriver-manager アンインストール完了")
        else:
            print(f"⚠️ アンインストール警告: {result.stderr}")
        
        # Seleniumも念のため更新
        print("🔄 Selenium を更新中...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", 
                               "--upgrade", "selenium"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Selenium 更新完了")
        else:
            print(f"⚠️ Selenium更新警告: {result.stderr}")
        
        # webdriver-managerを再インストール
        print("🔄 webdriver-manager を再インストール中...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", 
                               "webdriver-manager"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ webdriver-manager 再インストール完了")
            return True
        else:
            print(f"❌ 再インストールエラー: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ 再インストールエラー: {e}")
        return False

def download_chromedriver_manually(version=None):
    """ChromeDriverを手動でダウンロード"""
    print_header("ChromeDriver 手動ダウンロード")
    
    try:
        # ChromeDriverのダウンロードURL確認
        if not version:
            print("ℹ️ Chromeバージョンが不明なため、最新版をダウンロードします")
            
        # ChromeDriver APIから最新バージョンを取得
        try:
            response = requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE", timeout=10)
            if response.status_code == 200:
                latest_version = response.text.strip()
                print(f"📥 最新ChromeDriverバージョン: {latest_version}")
            else:
                print("⚠️ 最新バージョン情報の取得に失敗")
                latest_version = "114.0.5735.90"  # フォールバック
        except Exception as e:
            print(f"⚠️ バージョン取得エラー: {e}")
            latest_version = "114.0.5735.90"  # フォールバック
        
        # プラットフォーム確認
        if platform.system() == "Windows":
            if platform.architecture()[0] == "64bit":
                platform_suffix = "win32"  # ChromeDriverは64bit Windowsでもwin32を使用
            else:
                platform_suffix = "win32"
        else:
            print(f"❌ サポートされていないプラットフォーム: {platform.system()}")
            return False
        
        # ダウンロードURL構築
        download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_{platform_suffix}.zip"
        print(f"📥 ダウンロードURL: {download_url}")
        
        # ダウンロード先ディレクトリ作成
        download_dir = Path.home() / "chromedriver_manual"
        download_dir.mkdir(exist_ok=True)
        
        zip_path = download_dir / "chromedriver.zip"
        driver_path = download_dir / "chromedriver.exe"
        
        # 既存ファイルがあれば削除
        if zip_path.exists():
            zip_path.unlink()
        if driver_path.exists():
            driver_path.unlink()
        
        # ダウンロード実行
        print("📥 ChromeDriverをダウンロード中...")
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
                print(f"✅ ChromeDriver展開完了: {driver_path}")
                
                # テスト実行
                return test_manual_chromedriver(str(driver_path))
            else:
                print("❌ ChromeDriverの展開に失敗")
                return False
        else:
            print(f"❌ ダウンロード失敗: HTTP {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ 手動ダウンロードエラー: {e}")
        return False

def test_manual_chromedriver(driver_path):
    """手動ダウンロードしたChromeDriverをテスト"""
    print_header("ChromeDriver 動作テスト")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        print(f"🧪 テスト対象: {driver_path}")
        
        # ファイル確認
        if not os.path.exists(driver_path):
            print(f"❌ ファイルが存在しません: {driver_path}")
            return False
        
        file_size = os.path.getsize(driver_path)
        print(f"📊 ファイルサイズ: {file_size} bytes")
        
        if file_size == 0:
            print("❌ ファイルサイズが0です")
            return False
        
        # Chrome Optionsの設定
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        # WebDriverサービスの作成
        service = Service(driver_path)
        
        # WebDriverの起動テスト
        print("🚀 WebDriverを起動中...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ WebDriver起動成功")
        
        # 簡単なテスト
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ テストページ取得成功: {title}")
        
        driver.quit()
        print("✅ WebDriver終了成功")
        
        print(f"\n🎉 成功！使用可能なChromeDriver: {driver_path}")
        print("このパスを設定ファイルに追加することを検討してください。")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webdriver_manager_after_repair():
    """修復後のwebdriver-managerをテスト"""
    print_header("修復後 WebDriver Manager テスト")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ webdriver-manager インポート成功")
        
        # ChromeDriverの取得
        print("📥 ChromeDriverを取得中...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver取得成功: {driver_path}")
        
        # ファイル確認
        if os.path.exists(driver_path):
            file_size = os.path.getsize(driver_path)
            print(f"✅ ファイル確認成功: {driver_path} ({file_size} bytes)")
            
            if file_size == 0:
                print("❌ ファイルサイズが0です")
                return False
        else:
            print(f"❌ ファイルが存在しません: {driver_path}")
            return False
        
        # Chrome Optionsの設定
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # WebDriverサービスの作成
        service = Service(driver_path)
        
        # WebDriverの起動テスト
        print("🚀 WebDriverを起動中...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ WebDriver起動成功")
        
        # 簡単なテスト
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ テストページ取得成功: {title}")
        
        driver.quit()
        print("✅ WebDriver終了成功")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン処理"""
    print("WebDriver 修復ツール")
    print("=" * 60)
    print("このツールはWebDriverの問題を診断・修復します")
    
    # システム情報表示
    print_header("システム情報")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"アーキテクチャ: {platform.architecture()}")
    print(f"Python: {platform.python_version()}")
    
    # Chromeバージョン確認
    chrome_version = check_chrome_version()
    
    # 修復プロセス開始
    print_header("修復プロセス開始")
    
    # Step 1: キャッシュクリア
    print("🔧 Step 1: WebDriverキャッシュをクリア")
    if clean_webdriver_cache():
        print("✅ キャッシュクリア完了")
    else:
        print("⚠️ キャッシュクリアに問題がありました")
    
    # Step 2: webdriver-manager再インストール
    print("\n🔧 Step 2: webdriver-manager再インストール")
    if reinstall_webdriver_manager():
        print("✅ 再インストール完了")
        
        # Step 3: 修復後テスト
        print("\n🔧 Step 3: 修復後テスト")
        if test_webdriver_manager_after_repair():
            print("\n🎉 修復完了！WebDriverが正常に動作しています。")
            return True
        else:
            print("\n⚠️ webdriver-managerでの修復に失敗。手動ダウンロードを試行します。")
    else:
        print("⚠️ 再インストールに問題がありました")
    
    # Step 4: 手動ダウンロード
    print("\n🔧 Step 4: ChromeDriverを手動ダウンロード")
    if download_chromedriver_manually(chrome_version):
        print("\n🎉 手動ダウンロードで修復完了！")
        return True
    else:
        print("\n❌ 手動ダウンロードも失敗しました")
    
    # 修復失敗時の追加情報
    print_header("追加のトラブルシューティング")
    print("修復に失敗した場合の対処法:")
    print("1. セキュリティソフトがChromeDriverをブロックしていないか確認")
    print("2. Google Chromeを最新版に更新")
    print("3. 管理者権限でスクリプトを実行")
    print("4. 別のブラウザ（Firefox）の使用を検討")
    print("5. ファイアウォール設定の確認")
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 修復が正常に完了しました！")
        else:
            print("\n❌ 修復に失敗しました。追加のサポートが必要です。")
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
