#!/usr/bin/env python3
"""Selenium WebDriver診断スクリプト"""

import os
import sys
import platform

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_system_info():
    """システム情報を表示"""
    print("=== システム情報 ===")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"アーキテクチャ: {platform.architecture()}")
    print(f"マシン: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print()

def test_webdriver_manager():
    """webdriver-managerのテスト"""
    print("=== WebDriver Manager テスト ===")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ webdriver-manager インポート成功")
        
        # ChromeDriverの取得
        print("ChromeDriverを取得中...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver取得成功: {driver_path}")
        
        # ファイルが存在するか確認
        if os.path.exists(driver_path):
            print(f"✅ ファイル存在確認: {driver_path}")
            
            # ファイルサイズ確認
            file_size = os.path.getsize(driver_path)
            print(f"✅ ファイルサイズ: {file_size} bytes")
            
            if file_size == 0:
                print("❌ ファイルサイズが0です - ダウンロードが失敗している可能性")
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
        print("WebDriverサービスを作成中...")
        service = Service(driver_path)
        
        # WebDriverの起動テスト
        print("WebDriverを起動中...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ WebDriver起動成功")
        
        # 簡単なテスト
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ テストページ取得成功: {title}")
        
        driver.quit()
        print("✅ WebDriver終了成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ WebDriverテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_chrome_path():
    """手動でChromeDriverパスを指定するテスト"""
    print("\n=== 手動ChromeDriverパステスト ===")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        # 一般的なChromeDriverの場所を確認
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            r"C:\chromedriver.exe",
            r".\chromedriver.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ ChromeDriverを発見: {path}")
                
                try:
                    chrome_options = Options()
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    
                    service = Service(path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.get("https://www.google.com")
                    print(f"✅ 手動パステスト成功: {path}")
                    driver.quit()
                    return True
                    
                except Exception as e:
                    print(f"❌ 手動パステストエラー: {e}")
            else:
                print(f"❌ ファイルが見つかりません: {path}")
        
        return False
        
    except Exception as e:
        print(f"❌ 手動テストエラー: {e}")
        return False

def provide_solutions():
    """解決策を提示"""
    print("\n=== 解決策 ===")
    print("1. webdriver-managerの再インストール:")
    print("   pip uninstall webdriver-manager")
    print("   pip install webdriver-manager")
    print()
    print("2. Chromeブラウザの確認:")
    print("   Google Chromeがインストールされているか確認")
    print()
    print("3. セキュリティソフトの確認:")
    print("   ウイルス対策ソフトがChromeDriverをブロックしていないか確認")
    print()
    print("4. 手動ChromeDriverダウンロード:")
    print("   https://chromedriver.chromium.org/ から手動ダウンロード")
    print()
    print("5. 代替ブラウザの使用:")
    print("   Firefox（geckodriver）やEdge（edgedriver）の使用を検討")

if __name__ == "__main__":
    print("Selenium WebDriver 診断ツール")
    print("=" * 50)
    
    # システム情報表示
    test_system_info()
    
    # WebDriver Manager テスト
    if test_webdriver_manager():
        print("\n✅ WebDriver Manager テスト完了 - 正常に動作しています")
    else:
        print("\n❌ WebDriver Manager テストに失敗")
        
        # 手動パステスト
        if test_manual_chrome_path():
            print("✅ 手動パステスト成功 - 既存のChromeDriverが利用可能")
        else:
            print("❌ 手動パステストも失敗")
    
    # 解決策を提示
    provide_solutions()
    
    print("\n診断完了")
