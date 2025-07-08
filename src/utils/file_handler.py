import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.models.document import Document


class FileHandler:
    """ファイル操作クラス"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 出力ディレクトリを作成
        self.output_file = config.get('json_file', 'results/fpga_documents.json')
        self.create_backup = config.get('create_backup', True)
        
        # ディレクトリを作成
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
    
    def save_results(self, results: Dict[str, List[Document]]) -> str:
        """結果をJSONファイルに保存"""
        try:
            # 既存ファイルのバックアップ
            if self.create_backup and os.path.exists(self.output_file):
                self._create_backup()
            
            # DocumentオブジェクトをJSONシリアライズ可能な形式に変換
            json_results = self._convert_to_json_format(results)
            
            # ファイルに保存
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Results saved to {self.output_file}")
            return self.output_file
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            raise
    
    def load_previous_results(self) -> Dict[str, List[dict]]:
        """前回の結果をロード"""
        try:
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.warning(f"Failed to load previous results: {e}")
            return {}
    
    def _create_backup(self):
        """既存ファイルのバックアップを作成"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.output_file}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(self.output_file, backup_file)
            self.logger.info(f"Backup created: {backup_file}")
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
    
    def _convert_to_json_format(self, results: Dict[str, List[Document]]) -> dict:
        """DocumentオブジェクトをJSON形式に変換"""
        json_results = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'total_sources': len(results),
                'total_documents': sum(len(docs) for docs in results.values())
            },
            'sources': {}
        }
        
        for source_name, documents in results.items():
            source_info = {}
            
            # 検索URLを追加（最初のドキュメントから取得）
            if documents and documents[0].search_url:
                source_info['search_url'] = documents[0].search_url
            
            source_info['document_count'] = len(documents)
            
            # ドキュメントリストを作成（検索URLを除外）
            documents_list = []
            for doc in documents:
                doc_dict = doc.to_dict()
                doc_dict.pop('search_url', None)  # 各ドキュメントから検索URLを削除
                documents_list.append(doc_dict)
            
            source_info['documents'] = documents_list
            json_results['sources'][source_name] = source_info
        
        return json_results
    
    def get_stats(self, results: Dict[str, List[Document]]) -> dict:
        """統計情報を取得"""
        stats = {
            'total_documents': 0,
            'by_source': {},
            'by_category': {},
            'by_fpga_series': {},
            'by_file_type': {}
        }
        
        for source_name, documents in results.items():
            stats['total_documents'] += len(documents)
            stats['by_source'][source_name] = len(documents)
            
            for doc in documents:
                # カテゴリ別統計
                category = doc.category or 'Unknown'
                stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
                
                # FPGAシリーズ別統計
                fpga_series = doc.fpga_series or 'Unknown'
                stats['by_fpga_series'][fpga_series] = stats['by_fpga_series'].get(fpga_series, 0) + 1
                
                # ファイルタイプ別統計
                file_type = doc.file_type or 'Unknown'
                stats['by_file_type'][file_type] = stats['by_file_type'].get(file_type, 0) + 1
        
        return stats
