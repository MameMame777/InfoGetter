import yaml
import logging
import os
import sys
from typing import Dict, List
from datetime import datetime, timedelta
import glob

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scrapers.xilinx_scraper import XilinxScraper
from src.scrapers.altera_scraper import AlteraScraper
from src.scrapers.arxiv_scraper import ArxivScraper
from src.utils.email_sender import EmailSender
from src.utils.file_handler import FileHandler
from src.models.document import Document


class InfoGatherer:
    """メインのスクレイピング制御クラス"""
    
    def _clear_log_file(self):
        """ログファイルを初期化（既存のログを削除）"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        log_file = os.path.join(log_dir, 'scraper.log')
        
        try:
            # ログディレクトリが存在しない場合は作成
            os.makedirs(log_dir, exist_ok=True)
            
            # 既存のログファイルを削除
            if os.path.exists(log_file):
                os.remove(log_file)
                
            # 新しい空のログファイルを作成
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("")  # 空のファイルを作成
                
        except Exception as e:
            print(f"Warning: Could not clear log file: {e}")
    
    def _cleanup_old_files(self, days_threshold: int = None):
        """
        Clean up files older than specified days from results directory
        
        Args:
            days_threshold: Number of days to keep files (default: from config)
        """
        try:
            # Check if cleanup is enabled
            cleanup_config = self.config.get('cleanup', {})
            if not cleanup_config.get('enabled', True):
                return
            
            # Use provided threshold or config value
            if days_threshold is None:
                days_threshold = cleanup_config.get('keep_days', 7)
            
            # Get results directory path
            results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
            
            if not os.path.exists(results_dir):
                return
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            
            # Get file types to clean from config
            file_types = cleanup_config.get('file_types', ["*.json", "*.backup_*", "*.log", "*.txt"])
            
            # Build file patterns
            file_patterns = [os.path.join(results_dir, file_type) for file_type in file_types]
            
            deleted_files = []
            
            for pattern in file_patterns:
                for file_path in glob.glob(pattern):
                    try:
                        # Skip current main files
                        filename = os.path.basename(file_path)
                        if filename in ['fpga_documents.json', 'arxiv_recent_papers.json', 'arxiv_previous_papers.json']:
                            continue
                            
                        # Get file modification time
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        # Check if file is older than threshold
                        if file_mtime < cutoff_date:
                            os.remove(file_path)
                            deleted_files.append(filename)
                            
                    except Exception as e:
                        print(f"Warning: Could not delete file {file_path}: {e}")
            
            if deleted_files:
                print(f"Cleaned up {len(deleted_files)} old files from results directory (keeping files newer than {days_threshold} days):")
                for file_name in deleted_files:
                    print(f"  - {file_name}")
            else:
                print(f"No old files found to clean up in results directory (keeping files newer than {days_threshold} days)")
                
        except Exception as e:
            print(f"Warning: Could not cleanup old files: {e}")
    
    def __init__(self, config_path: str = None):
        """InfoGathererを初期化"""
        # ログファイルを初期化（既存のログを削除）
        self._clear_log_file()
        
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml')
        
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Clean up old files from results directory
        cleanup_days = self.config.get('cleanup', {}).get('keep_days', 7)
        self._cleanup_old_files(cleanup_days)
        
        # コンポーネントの初期化
        self.file_handler = FileHandler(self.config.get('output', {}))
        self.email_sender = EmailSender(self.config.get('notifications', {}).get('email', {}))
        
        # スクレイパーの初期化
        self.scrapers = self._initialize_scrapers()
        
        self.logger.info("InfoGatherer initialized successfully")
    
    def _load_config(self, config_path: str) -> dict:
        """設定ファイルをロード"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _setup_logging(self):
        """ログ設定"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/scraper.log')
        
        # ログディレクトリを作成
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # ログフォーマット
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # ルートロガー設定
        logging.basicConfig(
            level=log_level,
            handlers=[file_handler, console_handler]
        )
    
    def _initialize_scrapers(self) -> Dict[str, object]:
        """スクレイパーを初期化"""
        scrapers = {}
        data_sources = self.config.get('data_sources', {})
        
        scraper_classes = {
            'xilinx': XilinxScraper,
            'altera': AlteraScraper,
            'arxiv': ArxivScraper
        }
        
        for source_name, config in data_sources.items():
            if config.get('type') in ['web_scraping', 'api']:
                scraper_class = scraper_classes.get(source_name)
                if scraper_class:
                    scrapers[source_name] = scraper_class(config)
                    self.logger.info(f"Initialized {source_name} scraper")
                else:
                    self.logger.warning(f"Unknown scraper: {source_name}")
        
        return scrapers
    
    def run_scraping(self, sources: List[str] = None) -> Dict[str, List[Document]]:
        """スクレイピングを実行"""
        self.logger.info("Starting scraping process")
        
        if sources is None:
            sources = list(self.scrapers.keys())
        
        results = {}
        
        for source_name in sources:
            if source_name not in self.scrapers:
                self.logger.warning(f"Scraper not found: {source_name}")
                continue
            
            try:
                self.logger.info(f"Scraping from {source_name}")
                scraper = self.scrapers[source_name]
                documents = scraper.scrape_documents()
                results[source_name] = documents
                
                self.logger.info(f"Successfully scraped {len(documents)} documents from {source_name}")
                
                # レート制限
                import time
                rate_limit = self.config.get('data_sources', {}).get(source_name, {}).get('rate_limit', 1)
                if rate_limit > 0:
                    time.sleep(rate_limit)
                
            except Exception as e:
                self.logger.error(f"Error scraping {source_name}: {e}")
                results[source_name] = []
        
        return results
    
    def process_and_notify(self, results: Dict[str, List[Document]], 
                          send_email: bool = True) -> str:
        """結果を処理して通知"""
        try:
            # 結果をファイルに保存
            output_file = self.file_handler.save_results(results)
            
            # 統計情報を取得
            stats = self.file_handler.get_stats(results)
            self.logger.info(f"Processing complete. Total documents: {stats['total_documents']}")
            
            # メール通知
            if send_email and self.config.get('notifications', {}).get('email', {}).get('enabled', False):
                self.email_sender.send_notification(results, output_file)
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error in process_and_notify: {e}")
            raise
    
    def run(self, sources: List[str] = None, send_email: bool = True) -> Dict[str, List[Document]]:
        """完全なスクレイピングプロセスを実行"""
        try:
            # スクレイピング実行
            results = self.run_scraping(sources)
            
            # 結果処理と通知
            output_file = self.process_and_notify(results, send_email)
            
            self.logger.info(f"Scraping process completed. Results saved to: {output_file}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in run: {e}")
            raise


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FPGA IP Document Scraper')
    parser.add_argument('--sources', nargs='+', help='Sources to scrape (xilinx, altera)')
    parser.add_argument('--no-email', action='store_true', help='Disable email notifications')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--no-cleanup', action='store_true', help='Disable cleanup of old files')
    parser.add_argument('--cleanup-days', type=int, default=7, help='Number of days to keep files (default: 7)')
    
    args = parser.parse_args()
    
    try:
        # InfoGathererを初期化
        gatherer = InfoGatherer(args.config)
        
        # Manual cleanup if requested with custom days
        if not args.no_cleanup and args.cleanup_days != 7:
            gatherer._cleanup_old_files(args.cleanup_days)
        
        # スクレイピング実行
        results = gatherer.run(
            sources=args.sources,
            send_email=not args.no_email
        )
        
        # 結果サマリーを表示
        total_docs = sum(len(docs) for docs in results.values())
        print(f"\nScraping completed successfully!")
        print(f"Total documents found: {total_docs}")
        
        for source, docs in results.items():
            print(f"  {source}: {len(docs)} documents")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
