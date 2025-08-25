"""
LocalLLM API Client for InfoGetter
=================================

Client for connecting to LocalLLM API server to summarize FPGA scraping results.
Provides Japanese translation and email-ready summaries.

Usage:
    from src.utils.llm_api_client import LocalLLMAPIClient
    
    client = LocalLLMAPIClient()
    summary = client.summarize_scraping_results(results_dict)
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import yaml

class LocalLLMAPIClient:
    """
    Client for connecting to LocalLLM API server
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize LocalLLM API client
        
        Args:
            config: Configuration dictionary containing API settings
        """
        self.config = config or {}
        self.api_base_url = self.config.get('api_base_url', 'http://localhost:8000')
        self.timeout = self.config.get('timeout', 300)  # 5 minutes for LLM processing
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def check_server_health(self) -> bool:
        """
        Check if LocalLLM API server is running
        
        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/health",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"LocalLLM server health check failed: {e}")
            return False
    
    def summarize_json(self, data: Dict, summary_config: Dict = None) -> Dict:
        """
        Send JSON data to LocalLLM for summarization
        
        Args:
            data: JSON data to summarize
            summary_config: Summary configuration options
            
        Returns:
            Dict: Summarization result from LocalLLM
        """
        if not self.check_server_health():
            raise ConnectionError("LocalLLM API server is not available")
        
        # Default summary configuration
        default_config = {
            'language': 'japanese',
            'summary_type': 'detailed',
            'max_length': 500,
            'include_translation': True
        }
        
        if summary_config:
            default_config.update(summary_config)
        
        # Prepare API request payload
        payload = {
            'data': data,
            'config': default_config
        }
        
        try:
            self.logger.info("Sending data to LocalLLM API for summarization")
            response = requests.post(
                f"{self.api_base_url}/api/v1/summarize",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info("Successfully received summary from LocalLLM")
                return result
            else:
                error_msg = f"LocalLLM API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "LocalLLM API request timeout"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)
        except Exception as e:
            self.logger.error(f"Error calling LocalLLM API: {e}")
            raise


class InfoGetterSummarizer:
    """
    Main summarization class for InfoGetter project
    Integrates with LocalLLM API for intelligent document analysis
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the summarizer
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.llm_client = LocalLLMAPIClient(self.config.get('llm_api', {}))
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'settings.yaml'
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config from {config_path}: {e}")
            return {}
    
    def format_scraping_results(self, results: Dict) -> str:
        """
        Format scraping results into text suitable for LLM processing
        
        Args:
            results: Scraping results dictionary
            
        Returns:
            str: Formatted text for LLM input
        """
        formatted_text = []
        
        # Add scan information
        scan_info = results.get('scan_info', {})
        formatted_text.append(f"Scan Date: {scan_info.get('timestamp', 'Unknown')}")
        formatted_text.append(f"Total Sources: {scan_info.get('total_sources', 0)}")
        formatted_text.append(f"Total Documents: {scan_info.get('total_documents', 0)}")
        formatted_text.append("\n" + "="*50 + "\n")
        
        # Add source-specific information
        sources = results.get('sources', {})
        for source_name, source_data in sources.items():
            formatted_text.append(f"Source: {source_name.upper()}")
            formatted_text.append(f"Document Count: {source_data.get('document_count', 0)}")
            formatted_text.append(f"Search URL: {source_data.get('search_url', 'N/A')}")
            formatted_text.append("\nDocuments:")
            
            documents = source_data.get('documents', [])
            for i, doc in enumerate(documents, 1):
                formatted_text.append(f"{i}. {doc.get('name', 'Unknown')}")
                formatted_text.append(f"   URL: {doc.get('url', 'N/A')}")
                formatted_text.append(f"   Category: {doc.get('category', 'N/A')}")
                if doc.get('abstract'):
                    formatted_text.append(f"   Abstract: {doc.get('abstract')}")
                formatted_text.append("")
            
            formatted_text.append("-" * 30 + "\n")
        
        return "\n".join(formatted_text)
    
    def summarize_scraping_results(self, results: Dict, 
                                 summary_type: str = 'detailed') -> Dict:
        """
        Summarize scraping results using LocalLLM
        
        Args:
            results: Scraping results dictionary
            summary_type: Type of summary ('concise', 'detailed', 'academic')
            
        Returns:
            Dict: Summary results including Japanese translation
        """
        try:
            # Format results for LLM processing
            formatted_input = self.format_scraping_results(results)
            
            # Prepare summary configuration
            summary_config = {
                'language': 'japanese',
                'summary_type': summary_type,
                'max_length': 800,
                'include_translation': True,
                'focus_areas': [
                    'key_findings',
                    'document_categories',
                    'source_comparison',
                    'technical_insights'
                ]
            }
            
            # Send to LocalLLM for processing
            llm_input = {
                'text': formatted_input,
                'metadata': {
                    'type': 'fpga_scraping_results',
                    'timestamp': datetime.now().isoformat(),
                    'source_count': len(results.get('sources', {})),
                    'total_documents': results.get('scan_info', {}).get('total_documents', 0)
                }
            }
            
            summary_result = self.llm_client.summarize_json(llm_input, summary_config)
            
            # Process and enhance the result
            enhanced_result = self._enhance_summary_result(summary_result, results)
            
            self.logger.info("Successfully generated LLM summary of scraping results")
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Error in summarize_scraping_results: {e}")
            # Return fallback summary
            return self._generate_fallback_summary(results)
    
    def _enhance_summary_result(self, llm_result: Dict, original_results: Dict) -> Dict:
        """
        Enhance LLM summary result with additional metadata
        
        Args:
            llm_result: Result from LocalLLM API
            original_results: Original scraping results
            
        Returns:
            Dict: Enhanced summary result
        """
        enhanced = {
            'summary': llm_result.get('summary', ''),
            'japanese_summary': llm_result.get('japanese_translation', ''),
            'key_insights': llm_result.get('key_insights', []),
            'statistics': {
                'processing_time': llm_result.get('processing_time', 0),
                'total_sources': len(original_results.get('sources', {})),
                'total_documents': original_results.get('scan_info', {}).get('total_documents', 0),
                'generation_timestamp': datetime.now().isoformat()
            },
            'source_analysis': self._analyze_sources(original_results),
            'llm_metadata': llm_result.get('metadata', {})
        }
        
        return enhanced
    
    def _analyze_sources(self, results: Dict) -> Dict:
        """
        Analyze source-specific statistics
        
        Args:
            results: Scraping results dictionary
            
        Returns:
            Dict: Source analysis
        """
        sources = results.get('sources', {})
        analysis = {}
        
        for source_name, source_data in sources.items():
            documents = source_data.get('documents', [])
            categories = [doc.get('category', 'Unknown') for doc in documents]
            
            analysis[source_name] = {
                'document_count': len(documents),
                'categories': list(set(categories)),
                'category_distribution': {cat: categories.count(cat) for cat in set(categories)},
                'has_abstracts': sum(1 for doc in documents if doc.get('abstract'))
            }
        
        return analysis
    
    def _generate_fallback_summary(self, results: Dict) -> Dict:
        """
        Generate a basic summary when LLM is not available
        
        Args:
            results: Scraping results dictionary
            
        Returns:
            Dict: Fallback summary
        """
        sources = results.get('sources', {})
        total_docs = results.get('scan_info', {}).get('total_documents', 0)
        
        summary_lines = [
            f"FPGA文書スクレイピング結果サマリー",
            f"取得日時: {results.get('scan_info', {}).get('timestamp', '不明')}",
            f"総文書数: {total_docs}件",
            f"ソース数: {len(sources)}個",
            ""
        ]
        
        for source_name, source_data in sources.items():
            summary_lines.append(f"【{source_name.upper()}】")
            summary_lines.append(f"  文書数: {source_data.get('document_count', 0)}件")
            
            documents = source_data.get('documents', [])
            categories = [doc.get('category', 'Unknown') for doc in documents]
            unique_categories = list(set(categories))
            
            if unique_categories:
                summary_lines.append(f"  カテゴリ: {', '.join(unique_categories)}")
            summary_lines.append("")
        
        return {
            'summary': 'LLM summary not available - using fallback',
            'japanese_summary': '\n'.join(summary_lines),
            'key_insights': ['LLM処理が利用できませんでした'],
            'statistics': {
                'total_sources': len(sources),
                'total_documents': total_docs,
                'generation_timestamp': datetime.now().isoformat(),
                'fallback_used': True
            },
            'source_analysis': self._analyze_sources(results)
        }
    
    def generate_email_summary(self, summary_result: Dict) -> str:
        """
        Generate email-friendly summary text
        
        Args:
            summary_result: Enhanced summary result
            
        Returns:
            str: Email-formatted summary
        """
        lines = [
            "🤖 FPGA文書収集結果 - AI要約レポート",
            "=" * 50,
            ""
        ]
        
        # Add Japanese summary
        japanese_summary = summary_result.get('japanese_summary', '')
        if japanese_summary:
            lines.append("📋 要約:")
            lines.append(japanese_summary)
            lines.append("")
        
        # Add key insights
        insights = summary_result.get('key_insights', [])
        if insights:
            lines.append("💡 主要な知見:")
            for insight in insights:
                lines.append(f"  • {insight}")
            lines.append("")
        
        # Add statistics
        stats = summary_result.get('statistics', {})
        lines.append("📊 統計情報:")
        lines.append(f"  総ソース数: {stats.get('total_sources', 0)}")
        lines.append(f"  総文書数: {stats.get('total_documents', 0)}")
        if stats.get('processing_time'):
            lines.append(f"  AI処理時間: {stats.get('processing_time'):.2f}秒")
        lines.append("")
        
        # Add source analysis
        source_analysis = summary_result.get('source_analysis', {})
        if source_analysis:
            lines.append("🔍 ソース別詳細:")
            for source, analysis in source_analysis.items():
                lines.append(f"  【{source.upper()}】")
                lines.append(f"    文書数: {analysis.get('document_count', 0)}")
                categories = analysis.get('categories', [])
                if categories:
                    lines.append(f"    カテゴリ: {', '.join(categories)}")
            lines.append("")
        
        lines.append(f"生成日時: {stats.get('generation_timestamp', '')}")
        lines.append("Powered by LocalLLM + InfoGetter")
        
        return "\n".join(lines)
