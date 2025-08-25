import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.main import InfoGatherer

def test_search_url_display():
    """検索URLの表示テスト"""
    print("=== 検索URL表示テスト ===")
    
    try:
        # 設定ファイルのパス
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        
        # InfoGathererを初期化
        gatherer = InfoGatherer(config_path)
        
        # Xilinxのスクレイピングを実行
        print("Testing Xilinx scraper with search URL...")
        results = gatherer.run(sources=['xilinx'], send_email=False)
        
        # 結果の確認
        print(f"\n=== 結果確認 ===")
        
        for source, docs in results.items():
            print(f"\n--- {source.upper()} ---")
            print(f"Documents found: {len(docs)}")
            
            if docs and docs[0].search_url:
                print(f"Search URL used: {docs[0].search_url}")
                
                # URLの中身を確認
                search_url = docs[0].search_url
                if "query=DSP" in search_url:
                    print("✅ クエリパラメータが設定値と一致しています (query=DSP)")
                elif "query=Versal" in search_url:
                    print("✅ クエリパラメータが設定値と一致しています (query=Versal)")
                else:
                    print("❌ クエリパラメータが設定値と一致していません")
                
                if "value-filters=" in search_url:
                    print("✅ ドキュメントフィルターが適用されています")
                
                if "date-filters=" in search_url:
                    print("✅ 日付フィルターが適用されています")
                    
                if "content-lang=en-US" in search_url:
                    print("✅ 言語設定が適用されています")
            else:
                print("❌ 検索URLが記録されていません")
            
            # 上位3つのドキュメントの詳細を表示
            print(f"\nTop 3 documents:")
            for i, doc in enumerate(docs[:3]):
                print(f"  {i+1}. {doc.name}")
                print(f"     URL: {doc.url}")
                print(f"     Search URL: {doc.search_url}")
                print(f"     Category: {doc.category}, Series: {doc.fpga_series}")
                print()
        
        # JSONファイルの確認
        import json
        json_file = os.path.join(project_root, 'results', 'fpga_documents.json')
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            print(f"\n=== 保存データ確認 ===")
            for source_name, source_data in saved_data.get('sources', {}).items():
                if 'search_url' in source_data:
                    print(f"{source_name} search URL: {source_data['search_url']}")
                else:
                    print(f"{source_name}: search URLが保存されていません")
        
        print("\n=== テスト完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_url_display()
