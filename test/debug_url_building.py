import sys
import os
import yaml

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scrapers.xilinx_scraper import XilinxScraper

def debug_url_building():
    """URL構築のデバッグ"""
    print("=== URL構築デバッグ ===")
    
    # 設定ファイルを直接読み込み
    config_path = os.path.join(project_root, 'config', 'settings.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    print("設定ファイルの内容:")
    xilinx_config = config_data['data_sources']['xilinx']
    print(f"  base_url: {xilinx_config['base_url']}")
    print(f"  search_params: {xilinx_config['search_params']}")
    print(f"  query value: {xilinx_config['search_params']['query']}")
    
    # スクレイパーを作成してURL構築をテスト
    print("\n=== スクレイパーでのURL構築テスト ===")
    scraper = XilinxScraper(xilinx_config)
    
    # URL構築メソッドを直接呼び出し
    built_url = scraper._build_search_url()
    print(f"構築されたURL: {built_url}")
    
    # パラメータを個別に確認
    if "query=DSP" in built_url:
        print("✅ query=DSP が正しく設定されています")
    elif "query=Versal" in built_url:
        print("❌ query=Versal のままです（設定が反映されていません）")
    else:
        print("❓ queryパラメータが見つかりません")
    
    # 設定を手動で変更してテスト
    print("\n=== 手動設定変更テスト ===")
    test_config = xilinx_config.copy()
    test_config['search_params'] = test_config['search_params'].copy()
    test_config['search_params']['query'] = 'DSP'
    
    print(f"テスト用設定: query = {test_config['search_params']['query']}")
    
    test_scraper = XilinxScraper(test_config)
    test_url = test_scraper._build_search_url()
    print(f"テスト用URL: {test_url}")
    
    if "query=DSP" in test_url:
        print("✅ 手動変更では正しく動作します")
    else:
        print("❌ 手動変更でも問題があります")

if __name__ == "__main__":
    debug_url_building()
