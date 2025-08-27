from abc import ABC, abstractmethod
from typing import List
import hashlib
import logging
from datetime import datetime
import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.models.document import Document, DataSourceType


class BaseScraper(ABC):
    """Webスクレイピングの基底クラス"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.source_name = config.get('name', 'unknown')
        
    @abstractmethod
    def get_source_type(self) -> DataSourceType:
        """データソースの種類を返す"""
        pass
    
    @abstractmethod
    def scrape_documents(self) -> List[Document]:
        """ドキュメントをスクレイピングする"""
        pass
    
    def _generate_hash(self, content: str) -> str:
        """コンテンツのハッシュを生成"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _create_document(self, name: str, url: str, category: str = None, 
                        fpga_series: str = None, file_type: str = None, 
                        search_url: str = None, abstract: str = None, content: str = None) -> Document:
        """Documentオブジェクトを作成"""
        content_for_hash = f"{name}{url}{category or ''}{fpga_series or ''}"
        
        return Document(
            name=name,
            url=url,
            source=self.source_name,
            source_type=self.get_source_type(),
            search_url=search_url,
            category=category,
            fpga_series=fpga_series,
            file_type=file_type,
            abstract=abstract,
            content=content,  # contentフィールドを正しく設定
            scraped_at=datetime.now(),
            hash=self._generate_hash(content_for_hash)
        )
    
    def validate_data(self, documents: List[Document]) -> List[Document]:
        """データの検証"""
        validated_docs = []
        for doc in documents:
            if doc.name and doc.url:
                validated_docs.append(doc)
            else:
                self.logger.warning(f"Invalid document data: {doc}")
        return validated_docs
    
    def scrape_with_retry(self, max_retries: int = 3, delay: int = 2) -> List[Document]:
        """リトライ機能付きスクレイピング"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Scraping attempt {attempt + 1}/{max_retries}")
                documents = self.scrape_documents()
                
                if documents:
                    self.logger.info(f"Successfully scraped {len(documents)} documents")
                    return documents
                else:
                    self.logger.warning(f"No documents found in attempt {attempt + 1}")
                    
            except Exception as e:
                last_exception = e
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    self.logger.info(f"Waiting {delay} seconds before retry...")
                    import time
                    time.sleep(delay)
                    delay *= 2  # 指数バックオフ
        
        # 全ての試行が失敗した場合
        error_msg = f"All {max_retries} attempts failed"
        if last_exception:
            error_msg += f". Last error: {last_exception}"
        self.logger.error(error_msg)
        
        return []
