#!/usr/bin/env python3
"""
LocalLLM Integration for InfoGetter
===================================

Integrates LocalLLM summarization functionality with InfoGetter scraping results.
Uses LocalLLM package from https://github.com/MameMame777/LocalLLM for Japanese translation and summarization.

Usage:
    from src.utils.llm_summarizer import LLMSummarizer
    
    summarizer = LLMSummarizer()
    summary = summarizer.summarize_json_results("results/fpga_documents.json")
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMSummarizer:
    """LocalLLM integration for summarizing InfoGetter results using LocalLLM package"""
    
    def __init__(self):
        """Initialize LLM Summarizer with proper LocalLLM integration"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Fix LocalLLM internal import issues
        self._fix_localllm_path()
        
        # Check if LocalLLM is available and working
        if not self._check_and_import_localllm():
            raise RuntimeError("LocalLLM is not available or has critical errors. Cannot proceed without it.")
        
        self.localllm_available = True
        self.logger.info("✅ LLMSummarizer initialized with LocalLLM successfully")
    
    def _fix_localllm_path(self):
        """Fix LocalLLM internal path issues"""
        try:
            import localllm
            localllm_dir = os.path.dirname(localllm.__file__)
            if localllm_dir not in sys.path:
                sys.path.insert(0, localllm_dir)
                self.logger.info(f"✅ Fixed LocalLLM path: {localllm_dir}")
        except Exception as e:
            self.logger.error(f"❌ Failed to fix LocalLLM path: {e}")
    
    def _check_and_import_localllm(self) -> bool:
        """Check if LocalLLM library is available and working"""
        try:
            # Import the correct LocalLLM package from https://github.com/MameMame777/LocalLLM
            from localllm.api.quick_api import summarize_json
            
            # Test with a simple document to verify it works
            test_data = {"title": "Test", "content": "Test content for FPGA development."}
            result = summarize_json(test_data, language='ja')
            
            if isinstance(result, str) and not result.startswith('❌'):
                self.logger.info("✅ LocalLLM is working correctly")
                self._summarize_json_func = summarize_json
                return True
            else:
                self.logger.error(f"❌ LocalLLM test failed: {result}")
                raise RuntimeError(f"LocalLLM test failed: {result}")
                
        except ImportError as e:
            self.logger.error(f"❌ LocalLLM library not found: {e}")
            self.logger.error("Please install LocalLLM from: https://github.com/MameMame777/LocalLLM")
            raise ImportError(f"LocalLLM library not found: {e}")
        except Exception as e:
            self.logger.error(f"❌ LocalLLM initialization error: {e}")
            raise RuntimeError(f"LocalLLM initialization error: {e}")
    
    def summarize_json_results(
        self, 
        json_file_path_or_data: Union[str, Path, Dict[str, Any]],
        language: str = "ja",
        summary_type: str = "detailed",
        max_length: int = 2000
    ) -> Dict[str, Any]:
        """
        Summarize InfoGetter JSON results using LocalLLM
        
        Args:
            json_file_path_or_data: Path to InfoGetter results JSON file OR dictionary data
            language: Target language ("ja" for Japanese, "en" for English)
            summary_type: Summary type ("brief", "detailed", "academic")
            max_length: Maximum summary length
            
        Returns:
            Dictionary containing summary results
        """
        try:
            # Load data
            if isinstance(json_file_path_or_data, (str, Path)):
                json_file_path = Path(json_file_path_or_data)
                self.logger.info(f"📄 Loading results from: {json_file_path}")
                
                if not json_file_path.exists():
                    raise FileNotFoundError(f"JSON file not found: {json_file_path}")
                
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    results_data = json.load(f)
            else:
                results_data = json_file_path_or_data
                json_file_path = None
            
            # Convert to LocalLLM format
            llm_data = self._convert_infogetter_to_llm_format(results_data)
            
            self.logger.info(f"🤖 Generating {language} summary using LocalLLM...")
            
            # Use LocalLLM for summarization
            summary_result = self._summarize_json_func(llm_data, language=language)
            
            if not isinstance(summary_result, str) or summary_result.startswith('❌'):
                raise RuntimeError(f"LocalLLM summarization failed: {summary_result}")
            
            self.logger.info("✅ LocalLLM summary generation completed successfully")
            
            # Prepare output with successful LLM processing
            output_data = {
                "summary_info": {
                    "timestamp": datetime.now().isoformat(),
                    "source_file": str(json_file_path) if json_file_path else "Direct Data",
                    "language": language,
                    "summary_type": summary_type,
                    "max_length": max_length,
                    "original_document_count": results_data.get("scan_info", {}).get("total_documents", 0),
                    "original_sources": list(results_data.get("sources", {}).keys()),
                    "llm_error_detected": False,  # LocalLLM worked successfully
                    "llm_error_message": "LocalLLM processing successful",
                    "generation_method": "localllm",
                    "email_safe": True  # Safe for email sending
                },
                "summary": summary_result,
                "processing_status": "Success",
                "source_data": results_data
            }
            
            return output_data
            
        except Exception as e:
            self.logger.error(f"❌ LocalLLM summarization failed: {e}")
            raise RuntimeError(f"LocalLLM summarization failed: {e}")
    
    def _convert_infogetter_to_llm_format(self, infogetter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert InfoGetter JSON format to LocalLLM compatible format
        
        Args:
            infogetter_data: InfoGetter results data
            
        Returns:
            LocalLLM compatible data structure
        """
        try:
            scan_info = infogetter_data.get("scan_info", {})
            sources_data = infogetter_data.get("sources", {})
            
            # Create comprehensive content for LocalLLM
            content_parts = []
            content_parts.append("# FPGA IP Document Scraping Results")
            content_parts.append(f"**Scan Date**: {scan_info.get('timestamp', 'Unknown')}")
            content_parts.append(f"**Total Sources**: {scan_info.get('total_sources', 0)}")
            content_parts.append(f"**Total Documents**: {scan_info.get('total_documents', 0)}")
            content_parts.append("")
            
            # Process each source
            urls = []
            for source_name, source_data in sources_data.items():
                content_parts.append(f"## {source_name.upper()} Documents")
                content_parts.append(f"**Search URL**: {source_data.get('search_url', 'N/A')}")
                content_parts.append(f"**Document Count**: {source_data.get('document_count', 0)}")
                content_parts.append("")
                
                documents = source_data.get('documents', [])
                for i, doc in enumerate(documents[:10]):  # Limit to first 10 for performance
                    content_parts.append(f"### Document {i+1}: {doc.get('name', 'Untitled')}")
                    content_parts.append(f"- **Category**: {doc.get('category', 'Unknown')}")
                    content_parts.append(f"- **File Type**: {doc.get('file_type', 'Unknown')}")
                    content_parts.append(f"- **Source Type**: {doc.get('source_type', 'Unknown')}")
                    
                    if doc.get('abstract'):
                        content_parts.append(f"- **Abstract**: {doc['abstract'][:200]}...")
                    
                    if doc.get('url'):
                        urls.append({
                            'title': doc.get('name', 'Untitled'),
                            'url': doc['url'],
                            'source': source_name
                        })
                    
                    content_parts.append("")
                
                if len(documents) > 10:
                    content_parts.append(f"... and {len(documents) - 10} more documents")
                    content_parts.append("")
            
            # Create LocalLLM format
            llm_data = {
                "title": f"FPGA IP Document Scraping Results ({scan_info.get('total_documents', 0)} documents)",
                "content": "\n".join(content_parts),
                "metadata": {
                    "scan_info": scan_info,
                    "document_urls": urls,
                    "sources": list(sources_data.keys())
                }
            }
            
            return llm_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to convert data format: {e}")
            raise RuntimeError(f"Data conversion failed: {e}")
    
    def save_summary(
        self, 
        summary_data: Dict[str, Any], 
        output_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        Save summary results to file
        
        Args:
            summary_data: Summary data to save
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path(f"results/llm_summary_{timestamp}.json")
            else:
                output_path = Path(output_path)
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Summary saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save summary: {e}")
            raise
    
    def generate_markdown_report(self, summary_data: Dict[str, Any]) -> str:
        """
        Generate a formatted markdown report from summary data
        
        Args:
            summary_data: Summary data dictionary
            
        Returns:
            Formatted markdown string
        """
        try:
            summary_info = summary_data.get("summary_info", {})
            summary_text = summary_data.get("summary", "")
            
            report_parts = []
            report_parts.append("# LocalLLM Summary Report")
            report_parts.append("")
            report_parts.append(f"**Generated**: {summary_info.get('timestamp', 'Unknown')}")
            report_parts.append(f"**Language**: {summary_info.get('language', 'Unknown')}")
            report_parts.append(f"**Source Documents**: {summary_info.get('original_document_count', 0)}")
            report_parts.append(f"**Processing Status**: {summary_data.get('processing_status', 'Unknown')}")
            report_parts.append("")
            report_parts.append("## Summary")
            report_parts.append("")
            report_parts.append(summary_text)
            report_parts.append("")
            
            return "\n".join(report_parts)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate markdown report: {e}")
            raise


def demo_usage():
    """Demonstration of LLMSummarizer usage"""
    print("🚀 LLMSummarizer Demo with LocalLLM")
    print("=" * 50)
    
    try:
        summarizer = LLMSummarizer()
        
        # Test with existing results file
        results_file = "results/fpga_documents.json"
        if os.path.exists(results_file):
            summary = summarizer.summarize_json_results(results_file)
            print("✅ Summary generated successfully!")
            print(f"Summary preview: {summary['summary'][:200]}...")
        else:
            print("❌ No results file found for demo")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    demo_usage()
