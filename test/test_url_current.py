#!/usr/bin/env python3

import sys
import os
import yaml

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scrapers.xilinx_scraper import XilinxScraper
from src.scrapers.altera_scraper import AlteraScraper

def test_url_construction():
    """現在の設定でURLがどのように構築されるかテスト"""
    
    # 設定ファイルの読み込み
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'settings.yaml')
    
    print(f"Loading config from: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("\n=== Current Configuration ===")
    print(f"Xilinx query: {config['data_sources']['xilinx']['search_params']['query']}")
    print(f"Altera query: {config['data_sources']['altera']['search_params']['query']}")
    
    print("\n=== Testing URL Construction ===")
    
    # Xilinxスクレイパーのテスト
    xilinx_config = config['data_sources']['xilinx']
    xilinx_scraper = XilinxScraper(xilinx_config)
    xilinx_url = xilinx_scraper._build_search_url()
    print(f"Xilinx URL: {xilinx_url}")
    
    # Alteraスクレイパーのテスト
    altera_config = config['data_sources']['altera']
    altera_scraper = AlteraScraper(altera_config)
    altera_url = altera_scraper._build_search_url()
    print(f"Altera URL: {altera_url}")
    
    # URLパラメータの確認
    print("\n=== URL Parameter Analysis ===")
    if 'query=DSP' in xilinx_url:
        print("✓ Xilinx URL contains 'query=DSP'")
    else:
        print("✗ Xilinx URL does NOT contain 'query=DSP'")
        if 'query=' in xilinx_url:
            # query=の後の部分を抽出
            import re
            match = re.search(r'query=([^&]+)', xilinx_url)
            if match:
                print(f"  Found query parameter: {match.group(1)}")
    
    if 'DSP' in altera_url:
        print("✓ Altera URL contains 'DSP'")
    else:
        print("✗ Altera URL does NOT contain 'DSP'")

if __name__ == "__main__":
    test_url_construction()
