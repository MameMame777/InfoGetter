import unittest
import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.scrapers.xilinx_scraper import XilinxScraper
from src.scrapers.altera_scraper import AlteraScraper
from src.utils.email_sender import EmailSender
from src.utils.file_handler import FileHandler
from src.models.document import Document, DataSourceType


class TestScrapers(unittest.TestCase):
    """スクレイパーのテスト"""
    
    def setUp(self):
        self.xilinx_config = {
            'name': 'xilinx',
            'base_url': 'https://docs.amd.com/search/all?query=Versal',
            'type': 'web_scraping'
        }
        
        self.altera_config = {
            'name': 'altera',
            'base_url': 'https://www.intel.com/content/www/us/en/products/details/fpga/stratix/10/docs.html',
            'type': 'web_scraping'
        }
    
    def test_xilinx_scraper_initialization(self):
        """Xilinxスクレイパーの初期化テスト"""
        scraper = XilinxScraper(self.xilinx_config)
        self.assertEqual(scraper.source_name, 'xilinx')
        self.assertEqual(scraper.get_source_type(), DataSourceType.WEB_SCRAPING)
    
    def test_altera_scraper_initialization(self):
        """Alteraスクレイパーの初期化テスト"""
        scraper = AlteraScraper(self.altera_config)
        self.assertEqual(scraper.source_name, 'altera')
        self.assertEqual(scraper.get_source_type(), DataSourceType.WEB_SCRAPING)
    
    def test_document_creation(self):
        """ドキュメント作成テスト"""
        scraper = XilinxScraper(self.xilinx_config)
        doc = scraper._create_document(
            name="Test Document",
            url="https://example.com/test.pdf",
            category="Data Sheet",
            fpga_series="Versal",
            file_type="pdf"
        )
        
        self.assertEqual(doc.name, "Test Document")
        self.assertEqual(doc.source, "xilinx")
        self.assertEqual(doc.category, "Data Sheet")
        self.assertEqual(doc.fpga_series, "Versal")
        self.assertEqual(doc.file_type, "pdf")
    
    def test_fpga_series_extraction(self):
        """FPGAシリーズ抽出テスト"""
        scraper = XilinxScraper(self.xilinx_config)
        
        # Xilinxシリーズのテスト
        self.assertEqual(scraper._extract_fpga_series("Versal ACAP Data Sheet"), "Versal")
        self.assertEqual(scraper._extract_fpga_series("Zynq-7000 User Guide"), "Zynq")
        self.assertEqual(scraper._extract_fpga_series("Artix-7 FPGA Manual"), "Artix")
        
        # Alteraシリーズのテスト
        altera_scraper = AlteraScraper(self.altera_config)
        self.assertEqual(altera_scraper._extract_fpga_series("Stratix 10 DSP Guide"), "Stratix")
        self.assertEqual(altera_scraper._extract_fpga_series("Arria 10 User Manual"), "Arria")
    
    def test_category_extraction(self):
        """カテゴリ抽出テスト"""
        scraper = XilinxScraper(self.xilinx_config)
        
        self.assertEqual(scraper._extract_category("Versal ACAP Data Sheet"), "Data Sheet")
        self.assertEqual(scraper._extract_category("Zynq-7000 User Guide"), "User Guide")
        self.assertEqual(scraper._extract_category("DSP IP Core Manual"), "IP Core")
        self.assertEqual(scraper._extract_category("Reference Guide"), "Reference")
    
    def test_file_type_extraction(self):
        """ファイルタイプ抽出テスト"""
        scraper = XilinxScraper(self.xilinx_config)
        
        self.assertEqual(scraper._extract_file_type("https://example.com/doc.pdf"), "pdf")
        self.assertEqual(scraper._extract_file_type("https://example.com/page.html"), "html")
        self.assertEqual(scraper._extract_file_type("https://example.com/guide"), "html")


class TestFileHandler(unittest.TestCase):
    """ファイルハンドラーのテスト"""
    
    def setUp(self):
        self.config = {
            'json_file': 'test_results/test_output.json',
            'create_backup': False
        }
        self.file_handler = FileHandler(self.config)
    
    def test_stats_calculation(self):
        """統計計算テスト"""
        # テスト用のドキュメントを作成
        doc1 = Document(
            name="Test Doc 1",
            url="https://example.com/doc1.pdf",
            source="xilinx",
            source_type=DataSourceType.WEB_SCRAPING,
            category="Data Sheet",
            fpga_series="Versal",
            file_type="pdf",
            scraped_at="2025-01-01T00:00:00",
            hash="hash1"
        )
        
        doc2 = Document(
            name="Test Doc 2",
            url="https://example.com/doc2.html",
            source="altera",
            source_type=DataSourceType.WEB_SCRAPING,
            category="User Guide",
            fpga_series="Stratix",
            file_type="html",
            scraped_at="2025-01-01T00:00:00",
            hash="hash2"
        )
        
        results = {
            'xilinx': [doc1],
            'altera': [doc2]
        }
        
        stats = self.file_handler.get_stats(results)
        
        self.assertEqual(stats['total_documents'], 2)
        self.assertEqual(stats['by_source']['xilinx'], 1)
        self.assertEqual(stats['by_source']['altera'], 1)
        self.assertEqual(stats['by_category']['Data Sheet'], 1)
        self.assertEqual(stats['by_category']['User Guide'], 1)
        self.assertEqual(stats['by_fpga_series']['Versal'], 1)
        self.assertEqual(stats['by_fpga_series']['Stratix'], 1)
        self.assertEqual(stats['by_file_type']['pdf'], 1)
        self.assertEqual(stats['by_file_type']['html'], 1)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        if os.path.exists('test_results'):
            shutil.rmtree('test_results')


if __name__ == '__main__':
    unittest.main()
