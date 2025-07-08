import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.main import InfoGatherer

def test_basic_scraping():
    """基本的なスクレイピングテスト"""
    print("=== FPGA IP Document Scraper Test ===")
    
    try:
        # 設定ファイルのパスを指定
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        
        # InfoGathererを初期化
        print("Initializing InfoGatherer...")
        gatherer = InfoGatherer(config_path)
        
        # メール送信を無効にしてテスト実行
        print("Starting scraping test (without email)...")
        results = gatherer.run(sources=['xilinx'], send_email=False)
        
        # 結果を表示
        print(f"\n=== Results ===")
        total_docs = sum(len(docs) for docs in results.values())
        print(f"Total documents found: {total_docs}")
        
        for source, docs in results.items():
            print(f"\nSource: {source}")
            print(f"Documents found: {len(docs)}")
            
            # 最初の3つのドキュメントを表示
            for i, doc in enumerate(docs[:3]):
                print(f"  {i+1}. {doc.name}")
                print(f"     URL: {doc.url}")
                print(f"     Category: {doc.category}")
                print(f"     FPGA Series: {doc.fpga_series}")
                print(f"     File Type: {doc.file_type}")
                print()
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_scraping()
