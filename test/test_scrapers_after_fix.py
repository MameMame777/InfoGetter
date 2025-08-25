#!/usr/bin/env python3
"""修復後のWebDriverテストスクリプト"""

import sys
import os
import traceback

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.getcwd())

def test_xilinx_scraper():
    """Xilinx スクレイパーのテスト"""
    try:
        print("=== Xilinx スクレイパー テスト ===")
        
        import yaml
        from src.scrapers.xilinx_scraper import XilinxScraper
        
        # 設定ファイル読み込み
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        xilinx_config = config['data_sources']['xilinx']
        print("✅ 設定ファイル読み込み完了")
        
        # スクレイパー作成
        scraper = XilinxScraper(xilinx_config)
        print("✅ Xilinx スクレイパー作成完了")
        
        # WebDriver作成テスト
        driver = scraper._create_webdriver()
        print("✅ WebDriver作成完了")
        
        # テストページアクセス
        driver.get('https://www.google.com')
        title = driver.title
        print(f"✅ テストページアクセス成功: {title}")
        
        # 終了
        driver.quit()
        print("✅ WebDriver終了完了")
        
        return True
        
    except Exception as e:
        print(f"❌ Xilinx スクレイパーテストエラー: {e}")
        traceback.print_exc()
        return False

def test_altera_scraper():
    """Altera スクレイパーのテスト"""
    try:
        print("\n=== Altera スクレイパー テスト ===")
        
        import yaml
        from src.scrapers.altera_scraper import AlteraScraper
        
        # 設定ファイル読み込み
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        altera_config = config['data_sources']['altera']
        print("✅ 設定ファイル読み込み完了")
        
        # スクレイパー作成
        scraper = AlteraScraper(altera_config)
        print("✅ Altera スクレイパー作成完了")
        
        # WebDriver作成テスト
        driver = scraper._create_webdriver()
        print("✅ WebDriver作成完了")
        
        # テストページアクセス
        driver.get('https://www.google.com')
        title = driver.title
        print(f"✅ テストページアクセス成功: {title}")
        
        # 終了
        driver.quit()
        print("✅ WebDriver終了完了")
        
        return True
        
    except Exception as e:
        print(f"❌ Altera スクレイパーテストエラー: {e}")
        traceback.print_exc()
        return False

def main():
    """メインテスト"""
    print("WebDriver 修復後テスト")
    print("=" * 50)
    
    # Xilinx テスト
    xilinx_ok = test_xilinx_scraper()
    
    # Altera テスト
    altera_ok = test_altera_scraper()
    
    # 結果表示
    print("\n=== テスト結果 ===")
    print(f"Xilinx: {'✅ 成功' if xilinx_ok else '❌ 失敗'}")
    print(f"Altera: {'✅ 成功' if altera_ok else '❌ 失敗'}")
    
    if xilinx_ok and altera_ok:
        print("\n🎉 すべてのスクレイパーが正常に動作しています！")
    else:
        print("\n⚠️ 一部のスクレイパーに問題があります。")
    
    return xilinx_ok and altera_ok

if __name__ == "__main__":
    main()
