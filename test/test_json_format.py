#!/usr/bin/env python3

import sys
import os
import json

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import InfoGatherer

def test_json_format():
    """JSONフォーマットのテスト"""
    print("=== JSONフォーマットテスト ===")
    
    # 設定ファイルを指定
    config_path = os.path.join(project_root, 'config', 'settings.yaml')
    
    # InfoGathererを初期化
    gatherer = InfoGatherer(config_path)
    
    # Xilinxのみをテスト（速度向上のため）
    results = gatherer.run_scraping(sources=['xilinx'])
    
    # 結果ファイルを読み込み
    with open('results/fpga_documents.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print("\n=== JSONフォーマット確認 ===")
    print(f"総ソース数: {json_data['scan_info']['total_sources']}")
    print(f"総ドキュメント数: {json_data['scan_info']['total_documents']}")
    
    # Xilinxセクションを確認
    if 'xilinx' in json_data['sources']:
        xilinx_data = json_data['sources']['xilinx']
        print(f"\nXilinx:")
        print(f"  search_url: {xilinx_data.get('search_url', 'N/A')}")
        print(f"  document_count: {xilinx_data['document_count']}")
        
        # 最初のドキュメントのフィールドを確認
        if xilinx_data['documents']:
            first_doc = xilinx_data['documents'][0]
            print(f"\n最初のドキュメントのフィールド:")
            for key, value in first_doc.items():
                print(f"  {key}: {value}")
            
            # 不要なフィールドが含まれていないことを確認
            excluded_fields = ['fpga_series', 'last_updated', 'scraped_at', 'hash']
            found_excluded = []
            for field in excluded_fields:
                if field in first_doc:
                    found_excluded.append(field)
            
            if found_excluded:
                print(f"\n❌ 以下の不要なフィールドが見つかりました: {found_excluded}")
            else:
                print(f"\n✅ 不要なフィールドは正常に除外されています")
    
    # Alteraセクションを確認（存在する場合）
    if 'altera' in json_data['sources']:
        altera_data = json_data['sources']['altera']
        print(f"\nAltera:")
        print(f"  search_url: {altera_data.get('search_url', 'N/A')}")
        print(f"  document_count: {altera_data['document_count']}")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_json_format()
