#!/usr/bin/env python3

import sys
import os

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.scrapers.xilinx_scraper import XilinxScraper
from src.scrapers.altera_scraper import AlteraScraper

def test_exclusion_filters():
    """改善された除外フィルターをテスト"""
    print("=== 除外フィルターテスト ===")
    
    # Xilinxスクレイパーのテスト
    xilinx_config = {
        'base_url': 'https://docs.amd.com/search/all',
        'search_params': {'query': 'DSP'}
    }
    xilinx_scraper = XilinxScraper(xilinx_config)
    
    # Alteraスクレイパーのテスト
    altera_config = {
        'base_url': 'https://www.intel.com/content/www/us/en/products/details/fpga/stratix/10/docs.html',
        'search_params': {'query': 'DSP'}
    }
    altera_scraper = AlteraScraper(altera_config)
    
    # 除外すべきタイトルのテスト
    excluded_titles = [
        "包括的な用語",
        "強制労働に関する声明",
        "Modern Slavery Statement",
        "英国税務戦略",
        "UK Tax Strategy",
        "Privacy Policy",
        "Terms and Conditions",
        "Contact Us",
        "About Us",
        "Search Results",
        "Documentation Home"
    ]
    
    # 含まれるべきタイトルのテスト
    included_titles = [
        "System Generator for DSP",
        "DSP Builder (Advanced Blockset): Handbook",
        "Nios V Processor Reference Manual",
        "Stratix Variable Precision DSP Blocks User Guide",
        "FIR Compiler User Guide",
        "Vivado Design Suite User Guide"
    ]
    
    print("\n--- Xilinxスクレイパー ---")
    print("除外されるべきタイトル:")
    for title in excluded_titles:
        is_excluded_title = xilinx_scraper._is_excluded_title(title)
        is_excluded_fpga = not xilinx_scraper._is_fpga_related(title)
        result = is_excluded_title or is_excluded_fpga
        status = "✓ 除外" if result else "✗ 含まれる"
        print(f"  {title}: {status}")
    
    print("\n含まれるべきタイトル:")
    for title in included_titles:
        is_excluded_title = xilinx_scraper._is_excluded_title(title)
        is_excluded_fpga = not xilinx_scraper._is_fpga_related(title)
        result = is_excluded_title or is_excluded_fpga
        status = "✗ 除外" if result else "✓ 含まれる"
        print(f"  {title}: {status}")
    
    print("\n--- Alteraスクレイパー ---")
    print("除外されるべきタイトル:")
    for title in excluded_titles:
        is_excluded_title = altera_scraper._is_excluded_title(title)
        is_excluded_fpga = not altera_scraper._is_fpga_related(title)
        result = is_excluded_title or is_excluded_fpga
        status = "✓ 除外" if result else "✗ 含まれる"
        print(f"  {title}: {status}")
    
    print("\n含まれるべきタイトル:")
    for title in included_titles:
        is_excluded_title = altera_scraper._is_excluded_title(title)
        is_excluded_fpga = not altera_scraper._is_fpga_related(title)
        result = is_excluded_title or is_excluded_fpga
        status = "✗ 除外" if result else "✓ 含まれる"
        print(f"  {title}: {status}")
    
    # URL除外テスト
    print("\n--- URL除外テスト ---")
    excluded_urls = [
        "https://docs.amd.com/modern-slavery-statement",
        "https://docs.amd.com/uk-tax-strategy",
        "https://docs.amd.com/privacy-policy",
        "https://docs.amd.com/contact-us",
        "https://www.intel.com/content/www/us/en/privacy/intel-privacy-notice.html",
        "https://www.intel.com/content/www/us/en/careers.html"
    ]
    
    included_urls = [
        "https://docs.amd.com/r/en-US/pg149-fir-compiler/System-Generator-for-DSP",
        "https://www.intel.com/content/www/us/en/docs/programmable/683337/25-1.html",
        "https://docs.amd.com/v/u/en-US/ug949-vivado-design-methodology"
    ]
    
    print("除外されるべきURL:")
    for url in excluded_urls:
        is_excluded_xilinx = xilinx_scraper._is_excluded_url(url)
        is_excluded_altera = altera_scraper._is_excluded_url(url)
        status_x = "✓" if is_excluded_xilinx else "✗"
        status_a = "✓" if is_excluded_altera else "✗"
        print(f"  {url}")
        print(f"    Xilinx: {status_x}, Altera: {status_a}")
    
    print("\n含まれるべきURL:")
    for url in included_urls:
        is_excluded_xilinx = xilinx_scraper._is_excluded_url(url)
        is_excluded_altera = altera_scraper._is_excluded_url(url)
        status_x = "✗" if is_excluded_xilinx else "✓"
        status_a = "✗" if is_excluded_altera else "✓"
        print(f"  {url}")
        print(f"    Xilinx: {status_x}, Altera: {status_a}")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_exclusion_filters()
