#!/usr/bin/env python3
"""arXivスクレイパーのテストスクリプト"""

import os
import sys
import json

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scrapers.arxiv_scraper import ArxivScraper
from src.main import InfoGatherer

def test_arxiv_scraper():
    """arXivスクレイパーの単体テスト"""
    print("=== arXiv Scraper Test ===")
    
    # テスト設定
    config = {
        'name': 'arxiv',
        'type': 'api',
        'base_url': 'http://export.arxiv.org/api/query',
        'categories': ['cs.AR', 'cs.AI'],
        'max_results': 3,  # テスト用に少数に設定
        'enable_diff': True,
        'sort_by': 'lastUpdatedDate',
        'sort_order': 'descending',
        'rate_limit': 1
    }
    
    # スクレイパーを初期化
    scraper = ArxivScraper(config)
    
    # スクレイピング実行
    documents = scraper.scrape_documents()
    
    print(f"取得した論文数: {len(documents)}")
    
    for i, doc in enumerate(documents[:3], 1):  # 最初の3件を表示
        print(f"\n--- 論文 {i} ---")
        print(f"タイトル: {doc.name}")
        print(f"カテゴリ: {doc.category}")
        print(f"URL: {doc.url}")
        print(f"アブストラクト: {doc.abstract[:100]}...")
    
    return documents

def test_full_integration():
    """統合テスト（arXivを含む）"""
    print("\n=== Full Integration Test ===")
    
    try:
        # InfoGathererを初期化
        info_gatherer = InfoGatherer()
        
        # arXivのみをテスト
        results = info_gatherer.run_scraping(sources=['arxiv'])
        
        if 'arxiv' in results:
            arxiv_results = results['arxiv']
            print(f"arXiv結果: {len(arxiv_results)}件")
            
            # 結果をファイルに保存
            json_file = info_gatherer.file_handler.save_results(results)
            print(f"結果を保存: {json_file}")
            
            # メール送信テスト（実際には送信しない）
            print("メール送信機能をテスト...")
            # info_gatherer.send_notification(results, json_file)
            
        else:
            print("arXiv結果が見つかりません")
            
    except Exception as e:
        print(f"統合テストでエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 単体テスト
    documents = test_arxiv_scraper()
    
    # 統合テスト
    test_full_integration()
    
    print("\n=== Test Completed ===")
