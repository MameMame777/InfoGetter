import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import logging
import sys
from typing import List
from datetime import datetime

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.scrapers.base_scraper import BaseScraper
from src.models.document import Document, DataSourceType


class ArxivScraper(BaseScraper):
    """arXiv API を使用した論文情報スクレイパー"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://export.arxiv.org/api/query')
        self.categories = config.get('categories', ['cs.AR', 'cs.AI'])
        self.max_results = config.get('max_results', 10)
        self.enable_diff = config.get('enable_diff', True)
        self.sort_by = config.get('sort_by', 'lastUpdatedDate')
        self.sort_order = config.get('sort_order', 'descending')
        self.rate_limit = config.get('rate_limit', 1)
        
        # 差分管理用ファイル
        self.previous_results_file = "results/arxiv_previous_papers.json"
        self.diff_results_file = "results/arxiv_diff_papers.json"
        
    def get_source_type(self) -> DataSourceType:
        """データソースの種類を返す"""
        return DataSourceType.API
    
    def scrape_documents(self) -> List[Document]:
        """arXiv APIから論文情報をスクレイピング"""
        all_documents = []
        
        for category in self.categories:
            self.logger.info(f"Fetching papers from category: {category}")
            papers = self._fetch_papers_by_category(category)
            documents = self._convert_to_documents(papers, category)
            all_documents.extend(documents)
            
            # API制限対応
            time.sleep(self.rate_limit)
        
        # 差分機能が有効な場合
        if self.enable_diff:
            diff_documents = self._calculate_diff(all_documents)
            self._save_diff_results(diff_documents)
            self._save_current_results(all_documents)
            return diff_documents
        else:
            return all_documents
    
    def _fetch_papers_by_category(self, category: str) -> List[dict]:
        """指定されたカテゴリの論文を取得"""
        params = {
            'search_query': f'cat:{category}',
            'start': 0,
            'max_results': self.max_results,
            'sortBy': self.sort_by,
            'sortOrder': self.sort_order
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # XMLレスポンスを解析
            root = ET.fromstring(response.text)
            papers = []
            
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                abstract_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
                link_elem = entry.find("{http://www.w3.org/2005/Atom}id")
                
                if title_elem is not None and abstract_elem is not None and link_elem is not None:
                    paper = {
                        'title': title_elem.text.strip(),
                        'abstract': abstract_elem.text.strip(),
                        'link': link_elem.text.strip()
                    }
                    papers.append(paper)
            
            self.logger.info(f"Fetched {len(papers)} papers from {category}")
            return papers
            
        except Exception as e:
            self.logger.error(f"Failed to fetch papers from {category}: {e}")
            return []
    
    def _convert_to_documents(self, papers: List[dict], category: str) -> List[Document]:
        """論文データをDocumentオブジェクトに変換"""
        documents = []
        
        for paper in papers:
            doc = self._create_document(
                name=paper['title'],
                url=paper['link'],
                category=category,
                abstract=paper['abstract'],
                content=paper['abstract'],  # Use abstract as content for summarization
                search_url=f"{self.base_url}?search_query=cat:{category}"
            )
            documents.append(doc)
        
        return documents
    
    def _calculate_diff(self, current_documents: List[Document]) -> List[Document]:
        """前回の結果との差分を計算"""
        previous_documents = self._load_previous_results()
        
        if not previous_documents:
            self.logger.info("No previous results found. Returning all documents as new.")
            return current_documents
        
        # 前回の結果のリンクセットを作成
        previous_links = {doc.url for doc in previous_documents}
        
        # 新しい論文のみを抽出
        diff_documents = [doc for doc in current_documents if doc.url not in previous_links]
        
        self.logger.info(f"Found {len(diff_documents)} new papers out of {len(current_documents)} total papers")
        return diff_documents
    
    def _load_previous_results(self) -> List[Document]:
        """前回の結果を読み込み"""
        if not os.path.exists(self.previous_results_file):
            return []
        
        try:
            with open(self.previous_results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            for item in data:
                doc = Document(
                    name=item['name'],
                    url=item['url'],
                    source=item['source'],
                    source_type=DataSourceType(item['source_type']),
                    category=item.get('category'),
                    abstract=item.get('abstract'),
                    scraped_at=datetime.fromisoformat(item['scraped_at']),
                    hash=item['hash']
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Failed to load previous results: {e}")
            return []
    
    def _save_current_results(self, documents: List[Document]):
        """現在の結果を保存"""
        os.makedirs(os.path.dirname(self.previous_results_file), exist_ok=True)
        
        data = [doc.to_dict() for doc in documents]
        
        with open(self.previous_results_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=str)
    
    def _save_diff_results(self, diff_documents: List[Document]):
        """差分結果を保存"""
        os.makedirs(os.path.dirname(self.diff_results_file), exist_ok=True)
        
        data = [doc.to_dict() for doc in diff_documents]
        
        with open(self.diff_results_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=str)
        
        self.logger.info(f"Saved {len(diff_documents)} new papers to {self.diff_results_file}")
