"""
Markdown Report Generator for Real Llama Summaries
==================================================
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class MarkdownReportGenerator:
    """Real Llama要約結果のMarkdownレポート生成"""
    
    def __init__(self):
        self.output_dir = "results"
        
    def generate_summary_report(self, main_summary_file: str, individual_summaries_file: str = None) -> str:
        """Real Llama要約のMarkdownレポートを生成"""
        
        # Load main summary data
        with open(main_summary_file, 'r', encoding='utf-8') as f:
            main_data = json.load(f)
        
        # Load individual summaries if available
        individual_data = None
        if individual_summaries_file and os.path.exists(individual_summaries_file):
            with open(individual_summaries_file, 'r', encoding='utf-8') as f:
                individual_data = json.load(f)
        
        # Generate markdown content
        markdown_content = self._create_markdown_content(main_data, individual_data)
        
        # Save markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_llama_summary_report_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def _create_markdown_content(self, main_data: Dict[str, Any], individual_data: Dict[str, Any] = None) -> str:
        """Markdownコンテンツを生成"""
        
        # Header
        content = "# 🤖 Real Llama AI 学術論文要約レポート\n\n"
        content += f"**生成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n"
        content += "---\n\n"
        
        # Scan Information
        if 'scan_info' in main_data:
            scan_info = main_data['scan_info']
            content += "## 📊 スキャン情報\n\n"
            content += f"- **実行日時**: {scan_info.get('timestamp', '不明')}\n"
            content += f"- **データソース数**: {scan_info.get('total_sources', 0)}\n"
            content += f"- **総論文数**: {scan_info.get('total_documents', 0)}\n\n"
        
        # Real Llama Summary
        if 'llm_summary' in main_data:
            content += "## 🎯 Real Llama 総合要約\n\n"
            
            # Model Information
            if 'llm_summary_info' in main_data:
                summary_info = main_data['llm_summary_info']
                content += "### 🧠 LLMモデル情報\n\n"
                
                model_info = summary_info.get('model_info', {})
                content += f"- **モデル名**: {model_info.get('model_name', '不明')}\n"
                content += f"- **モデルパス**: `{model_info.get('model_path', '不明')}`\n"
                content += f"- **バックエンド**: {model_info.get('backend', '不明')}\n"
                content += f"- **処理方式**: {summary_info.get('processing_method', '不明')}\n"
                content += f"- **処理時間**: {model_info.get('processing_time', 0):.1f}秒\n"
                content += f"- **生成トークン数**: {model_info.get('tokens_generated', 0)}\n"
                content += f"- **コンテキスト長**: {model_info.get('context_length', 0)}\n\n"
            
            # Summary Content
            content += "### 📄 要約内容\n\n"
            summary_text = main_data['llm_summary']
            content += f"{summary_text}\n\n"
        
        # Individual Summaries
        if individual_data and 'individual_summaries' in individual_data:
            content += "## 📚 個別論文日本語要約 (Real Llama生成)\n\n"
            
            # Processing Statistics
            content += "### 📈 処理統計\n\n"
            content += f"- **処理論文数**: {individual_data.get('total_papers', 0)}\n"
            content += f"- **総処理時間**: {individual_data.get('total_processing_time', 0):.1f}秒\n"
            content += f"- **平均処理時間**: {individual_data.get('average_processing_time', 0):.1f}秒/論文\n\n"
            
            # Individual Papers
            summaries = individual_data['individual_summaries']
            for i, summary in enumerate(summaries):
                content += f"### 📝 論文 {summary.get('paper_index', i+1)}\n\n"
                
                # Paper Information
                content += "#### 📋 論文情報\n\n"
                content += f"- **タイトル**: {summary.get('title', 'タイトル不明')}\n"
                content += f"- **URL**: [{summary.get('url', '')}]({summary.get('url', '')})\n"
                content += f"- **ソース**: {summary.get('source', '不明')}\n"
                content += f"- **カテゴリ**: {summary.get('category', '不明')}\n"
                content += f"- **処理時間**: {summary.get('processing_time', 0):.1f}秒\n"
                content += f"- **要約文字数**: {summary.get('summary_length', 0)}文字\n\n"
                
                # Original Abstract
                original_abstract = summary.get('original_abstract', '')
                if original_abstract:
                    content += "#### 📄 原文概要\n\n"
                    content += f"```\n{original_abstract}\n```\n\n"
                
                # Japanese Summary
                content += "#### 🇯🇵 日本語要約 (Real Llama生成)\n\n"
                japanese_summary = summary.get('japanese_summary', '')
                content += f"{japanese_summary}\n\n"
                
                content += "---\n\n"
        
        # Source Details
        if 'sources' in main_data:
            content += "## 📋 データソース詳細\n\n"
            
            for source_name, source_data in main_data['sources'].items():
                content += f"### 📊 {source_name.upper()}\n\n"
                content += f"- **検索URL**: {source_data.get('search_url', '不明')}\n"
                content += f"- **文書数**: {source_data.get('document_count', 0)}\n\n"
                
                if 'documents' in source_data and len(source_data['documents']) > 0:
                    content += "#### 📄 収集論文一覧\n\n"
                    for i, doc in enumerate(source_data['documents'][:10]):  # Show first 10
                        content += f"{i+1}. **{doc.get('name', 'タイトル不明')}**\n"
                        content += f"   - URL: [{doc.get('url', '')}]({doc.get('url', '')})\n"
                        content += f"   - カテゴリ: {doc.get('category', '不明')}\n\n"
                    
                    if len(source_data['documents']) > 10:
                        content += f"   *(他 {len(source_data['documents']) - 10} 件)*\n\n"
        
        # Footer
        content += "---\n\n"
        content += "## 🔧 技術情報\n\n"
        content += "- **生成システム**: InfoGatherer with Real Llama\n"
        content += "- **LLMエンジン**: llama-cpp-python\n"
        content += "- **処理タイプ**: ローカルLLM (プライバシー保護)\n"
        content += "- **出力形式**: Markdown Report\n\n"
        content += f"*レポート生成時刻: {datetime.now().isoformat()}*\n"
        
        return content
