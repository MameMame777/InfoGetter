#!/usr/bin/env python3
"""
簡単なテストスクリプト
"""

import os
import sys
import yaml

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.scrapers.xilinx_scraper import XilinxScraper


def simple_test():
    """簡単なテスト"""
    print("🔍 改善されたXilinxスクレイパーのテスト")
    
    # 設定ファイルを読み込み
    config_path = os.path.join(project_root, 'config', 'settings.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    xilinx_config = config['data_sources']['xilinx']
    
    # スクレイパーを初期化
    scraper = XilinxScraper(xilinx_config)
    
    # URL構築をテスト
    search_url = scraper._build_search_url()
    print(f"🔗 構築されたURL: {search_url}")
    
    # 設定値を確認
    print(f"📊 設定値:")
    print(f"  max_results: {xilinx_config.get('max_results', 100)}")
    print(f"  scroll_pages: {xilinx_config.get('scroll_pages', 5)}")
    print(f"  query: {xilinx_config.get('search_params', {}).get('query', 'Unknown')}")
    
    # スクレイピング実行
    try:
        print("\n🚀 スクレイピング開始...")
        documents = scraper.scrape_documents()
        
        print(f"✅ 取得完了: {len(documents)} 件")
        
        # 重複チェック
        urls = [doc.url for doc in documents]
        unique_urls = set(urls)
        duplicate_count = len(urls) - len(unique_urls)
        
        print(f"📈 重複分析:")
        print(f"  総件数: {len(urls)}")
        print(f"  ユニーク: {len(unique_urls)}")
        print(f"  重複: {duplicate_count}")
        
        if duplicate_count > 0:
            print(f"  重複率: {duplicate_count / len(urls) * 100:.1f}%")
        else:
            print("  重複率: 0% (完璧！)")
        
        # 最初の3件を表示
        print(f"\n📝 サンプル結果:")
        for i, doc in enumerate(documents[:3]):
            print(f"  {i+1}. {doc.name}")
            print(f"     URL: {doc.url}")
            print(f"     カテゴリ: {doc.category}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    simple_test()