#!/usr/bin/env python3
"""WebDriver統合テスト・修復スクリプト"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def print_header(title):
    """ヘッダーを表示"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def run_script(script_name, description):
    """スクリプトを実行"""
    print_header(f"{description}")
    print(f"🚀 実行中: {script_name}")
    
    try:
        script_path = Path(project_root) / script_name
        
        if not script_path.exists():
            print(f"❌ スクリプトが見つかりません: {script_path}")
            return False
        
        # スクリプト実行
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} 完了")
            return True
        else:
            print(f"⚠️ {description} で問題が発生しました (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} 実行エラー: {e}")
        return False

def test_current_scrapers():
    """現在のスクレイパーをテスト"""
    print_header("スクレイパー動作テスト")
    
    try:
        from src.scrapers.xilinx_scraper import XilinxScraper
        from src.scrapers.altera_scraper import AlteraScraper
        import yaml
        
        # 設定ファイル読み込み
        config_path = Path(project_root) / "config" / "settings.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Xilinxスクレイパーテスト
        print("🧪 Xilinx スクレイパーテスト中...")
        try:
            xilinx_config = config['data_sources']['xilinx']
            xilinx_scraper = XilinxScraper(xilinx_config)
            
            # WebDriverの作成テストのみ（実際のスクレイピングは行わない）
            driver = xilinx_scraper._create_webdriver()
            driver.get("https://www.google.com")
            title = driver.title
            driver.quit()
            
            print(f"✅ Xilinx スクレイパー正常動作: {title}")
        except Exception as e:
            print(f"❌ Xilinx スクレイパーエラー: {e}")
        
        # Alteraスクレイパーテスト
        print("🧪 Altera スクレイパーテスト中...")
        try:
            altera_config = config['data_sources']['altera']
            altera_scraper = AlteraScraper(altera_config)
            
            # WebDriverの作成テストのみ
            driver = altera_scraper._create_webdriver()
            driver.get("https://www.google.com")
            title = driver.title
            driver.quit()
            
            print(f"✅ Altera スクレイパー正常動作: {title}")
        except Exception as e:
            print(f"❌ Altera スクレイパーエラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ スクレイパーテスト実行エラー: {e}")
        return False

def show_menu():
    """メニューを表示"""
    print_header("WebDriver 統合診断・修復ツール")
    print("以下のオプションから選択してください:")
    print()
    print("1. 基本診断 - 現在のWebDriverの状態を確認")
    print("2. Chrome修復 - ChromeDriverの問題を修復")
    print("3. Firefox設定 - Firefoxを代替ブラウザとして設定")
    print("4. スクレイパーテスト - 修復後のスクレイパー動作確認")
    print("5. 全自動修復 - 診断から修復まで自動実行")
    print("6. 終了")
    print()

def main():
    """メイン処理"""
    print("WebDriver 統合診断・修復ツール")
    print("=" * 60)
    print("このツールはWebDriverの問題を包括的に診断・修復します")
    
    # システム情報表示
    print_header("システム情報")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"アーキテクチャ: {platform.architecture()}")
    print(f"Python: {platform.python_version()}")
    
    while True:
        show_menu()
        
        try:
            choice = input("選択してください (1-6): ").strip()
            
            if choice == "1":
                # 基本診断
                run_script("test_webdriver.py", "基本診断")
                
            elif choice == "2":
                # Chrome修復
                success = run_script("webdriver_repair.py", "Chrome修復")
                if success:
                    print("\n修復完了後、スクレイパーテストを実行することをお勧めします。")
                
            elif choice == "3":
                # Firefox設定
                success = run_script("firefox_setup.py", "Firefox設定")
                if success:
                    print("\n設定完了後、config/settings.yamlでブラウザーをFirefoxに変更してください。")
                
            elif choice == "4":
                # スクレイパーテスト
                test_current_scrapers()
                
            elif choice == "5":
                # 全自動修復
                print_header("全自動修復モード")
                print("診断から修復まで自動で実行します...")
                
                # Step 1: 基本診断
                print("\n🔧 Step 1: 基本診断")
                diagnostic_success = run_script("test_webdriver.py", "基本診断")
                
                if not diagnostic_success:
                    # Step 2: Chrome修復試行
                    print("\n🔧 Step 2: Chrome修復")
                    repair_success = run_script("webdriver_repair.py", "Chrome修復")
                    
                    if not repair_success:
                        # Step 3: Firefox設定
                        print("\n🔧 Step 3: Firefox代替設定")
                        firefox_success = run_script("firefox_setup.py", "Firefox設定")
                        
                        if firefox_success:
                            print("\n⚠️ Firefoxが設定されました。設定ファイルを更新してください。")
                        else:
                            print("\n❌ 全ての修復方法が失敗しました。")
                            continue
                
                # Step 4: 最終テスト
                print("\n🔧 Step 4: 最終動作確認")
                test_current_scrapers()
                
                print("\n🎉 全自動修復プロセス完了")
                
            elif choice == "6":
                print("\n終了します。")
                break
                
            else:
                print("❌ 無効な選択です。1-6の数字を入力してください。")
                
        except KeyboardInterrupt:
            print("\n\n⚠️ プログラムが中断されました。")
            break
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
        
        input("\nEnterキーを押して続行...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
