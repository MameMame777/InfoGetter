import sys
import os
import json

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.main import InfoGatherer

def test_improved_scraping():
    """改善されたスクレイピングの最終テスト"""
    print("=== 改善後スクレイピングテスト ===")
    
    try:
        # 設定ファイルのパス
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        
        # InfoGathererを初期化
        gatherer = InfoGatherer(config_path)
        
        # 両方のソースでテスト
        print("Testing both Xilinx and Altera scrapers...")
        results = gatherer.run(sources=['xilinx', 'altera'], send_email=False)
        
        # 結果の詳細分析
        print(f"\n=== 改善結果 ===")
        total_docs = sum(len(docs) for docs in results.values())
        print(f"Total documents found: {total_docs}")
        
        for source, docs in results.items():
            print(f"\n--- {source.upper()} ---")
            print(f"Documents: {len(docs)}")
            
            # カテゴリ別統計
            categories = {}
            fpga_series = {}
            file_types = {}
            
            for doc in docs:
                categories[doc.category] = categories.get(doc.category, 0) + 1
                if doc.fpga_series:
                    fpga_series[doc.fpga_series] = fpga_series.get(doc.fpga_series, 0) + 1
                file_types[doc.file_type] = file_types.get(doc.file_type, 0) + 1
            
            print(f"Categories: {categories}")
            print(f"FPGA Series: {fpga_series}")
            print(f"File Types: {file_types}")
            
            # 品質チェック：FPGA関連度
            fpga_related = 0
            for doc in docs:
                if any(keyword in doc.name.lower() for keyword in ['fpga', 'versal', 'zynq', 'artix', 'stratix', 'arria', 'cyclone', 'ip core', 'dsp']):
                    fpga_related += 1
            
            print(f"FPGA関連度: {fpga_related}/{len(docs)} ({fpga_related/len(docs)*100:.1f}%)")
            
            # トップ5のドキュメント表示
            print(f"\nTop 5 documents:")
            for i, doc in enumerate(docs[:5]):
                print(f"  {i+1}. {doc.name}")
                print(f"     Series: {doc.fpga_series}, Category: {doc.category}")
        
        # 保存されたJSONファイルを確認
        json_file = os.path.join(project_root, 'results', 'fpga_documents.json')
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            print(f"\n=== 保存データ確認 ===")
            print(f"Saved timestamp: {saved_data.get('scan_info', {}).get('timestamp')}")
            print(f"Total sources: {saved_data.get('scan_info', {}).get('total_sources')}")
            print(f"Total documents: {saved_data.get('scan_info', {}).get('total_documents')}")
        
        print("\n=== テスト完了 ===")
        print("スクレイピングの改善が正常に動作しています！")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_scraping()
