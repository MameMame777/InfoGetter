#!/usr/bin/env python3
"""
Lo        # Check if LocalLLM is available and working
        if not self._check_and_import_localllm():
            self.logger.warning(
                "🔄 LocalLLM not available or has dependency issues. "
                "Using fallback summarization for all operations."
            )
            # Set to fallback mode instead of raising error
            self.localllm_available = False
        else:
            self.localllm_available = True
            
        self.logger.info("✅ LLMSummarizer initialized with robust fallback support")ntegration for InfoGetter
===================================

Integrates LocalLLM summarization functionality with InfoGetter scraping results.
Uses direct pip-installed LocalLLM package for Japanese translation and summarization.

Usage:
    from src.utils.llm_summarizer import LLMSummarizer
    
    summarizer = LLMSummarizer()
    summary = summarizer.summarize_json_results("results/fpga_documents.json")
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMSummarizer:
    """LocalLLM integration for summarizing InfoGetter results using pip-installed package"""
    
    def __init__(self):
        """Initialize LLM Summarizer with robust fallback support"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Check if LocalLLM is available and working
        if not self._check_and_import_localllm():
            self.logger.warning(
                "🔄 LocalLLM not available or has dependency issues. "
                "Using fallback summarization for all operations."
            )
            # Set to fallback mode instead of raising error
            self.localllm_available = False
        else:
            self.localllm_available = True
            
        self.logger.info("✅ LLMSummarizer initialized with robust fallback support")
    
    def _check_and_import_localllm(self) -> bool:
        """Check if LocalLLM library is available and working"""
        try:
            # Import the correct LocalLLM package from https://github.com/MameMame777/LocalLLM
            from localllm.api.quick_api import summarize_json
            self.logger.info("✅ LocalLLM package is available")
            
            # Store the summarize function for later use
            self._localllm_summarize_json = summarize_json
            
            return True
            
        except ImportError as e:
            self.logger.error(f"❌ LocalLLM package not available: {e}")
            self.logger.error("Please install LocalLLM from: https://github.com/MameMame777/LocalLLM")
            return False
        except Exception as e:
            self.logger.error(f"❌ LocalLLM import error: {e}")
            return False
    
    def summarize_json_results(
        self, 
        json_file_path_or_data: Union[str, Path, Dict[str, Any]],
        language: str = "ja",
        summary_type: str = "detailed",
        max_length: int = 2000
    ) -> Dict[str, Any]:
        """
        Summarize InfoGetter JSON results using pip-installed LocalLLM
        
        Args:
            json_file_path_or_data: Path to InfoGetter results JSON file OR dictionary data
            language: Target language ("ja" for Japanese, "en" for English)
            summary_type: Summary type ("brief", "detailed", "academic")
            max_length: Maximum summary length
            
        Returns:
            Dictionary containing summary results
        """
        try:
            # Handle both file path and direct dictionary input
            if isinstance(json_file_path_or_data, (str, Path)):
                # File path input
                json_path = Path(json_file_path_or_data)
                if not json_path.exists():
                    raise FileNotFoundError(f"Results file not found: {json_path}")
                
                with open(json_path, 'r', encoding='utf-8') as f:
                    results_data = json.load(f)
                json_file_path = json_path
            else:
                # Dictionary input
                results_data = json_file_path_or_data
                json_file_path = None
            
            # Log data source
            if json_file_path:
                self.logger.info(f"📄 Loading results from: {json_file_path}")
            else:
                self.logger.info(f"📄 Processing direct dictionary data with {len(results_data)} keys")
            
            # Convert InfoGetter format to LocalLLM format
            llm_input_data = self._convert_infogetter_to_llm_format(results_data)
            
            # Generate summary using LocalLLM or fallback
            self.logger.info(f"🤖 Generating {language} summary...")
            
            # Check if LocalLLM is available and working
            if (hasattr(self, 'localllm_available') and self.localllm_available and 
                hasattr(self, '_localllm_summarize_json')):
                
                # Try LocalLLM summarization
                try:
                    self.logger.info("🤖 Using LocalLLM for summarization")
                    
                    # Use the stored LocalLLM function directly
                    summary_result = self._localllm_summarize_json(
                        json_input=llm_input_data,
                        language=language,
                        summary_config={
                            "summary_type": summary_type,
                            "max_length": max_length,
                            "individual_processing": True,
                            "include_urls": True,
                            "output_format": "markdown"
                        }
                    )
                    
                    # Check if LocalLLM returned an error and use fallback
                    if (isinstance(summary_result, str) and
                        ("❌" in summary_result or 
                         "エラー" in summary_result or
                         "error" in summary_result.lower())):
                        self.logger.warning("🔄 LocalLLM returned error, using fallback summarization")
                        summary_result = self._create_fallback_summary(llm_input_data, language)
                        
                except Exception as e:
                    self.logger.warning(f"🔄 LocalLLM failed ({e}), using fallback summarization")
                    summary_result = self._create_fallback_summary(llm_input_data, language)
            else:
                # Use fallback directly if LocalLLM not available
                self.logger.info("🔄 Using fallback summarization (LocalLLM not available)")
                summary_result = self._create_fallback_summary(llm_input_data, language)
            
            # Prepare output with STRICT LLM error detection for email safety
            llm_error_detected = True  # Default to error state for safety
            llm_error_message = "Default error state"
            
            # Check if we used fallback due to LLM issues
            if not self.localllm_available:
                llm_error_detected = True
                llm_error_message = "LLM libraries not available - CRITICAL: Do not send email"
            
            # Check if summary contains any error indicators
            error_indicators = ["LocalLLM処理エラー", "簡易要約", "フォールバック", "エラー", "処理エラー"]
            if any(indicator in summary_result for indicator in error_indicators):
                llm_error_detected = True
                llm_error_message = "LLM processing error detected - CRITICAL: Do not send email"
            
            # Only mark as success if LLM actually worked without any fallback
            if self.localllm_available and not any(indicator in summary_result for indicator in error_indicators):
                llm_error_detected = False
                llm_error_message = "LLM processing successful"
            
            # CRITICAL: Mark processing as FAILED if LLM error detected
            processing_status = "Failed" if llm_error_detected else "Success"
            
            output_data = {
                "summary_info": {
                    "timestamp": datetime.now().isoformat(),
                    "source_file": str(json_file_path) if json_file_path else "Direct Data",
                    "language": language,
                    "summary_type": summary_type,
                    "max_length": max_length,
                    "original_document_count": results_data.get("scan_info", {}).get("total_documents", 0),
                    "original_sources": list(results_data.get("sources", {}).keys()),
                    "llm_error_detected": llm_error_detected,
                    "llm_error_message": llm_error_message,
                    "generation_method": "fallback" if llm_error_detected else "llm",
                    "email_safe": not llm_error_detected  # Explicit email safety flag
                },
                "summary": summary_result,
                "original_scan_info": results_data.get("scan_info", {}),
                "processing_status": "Success",
                "llm_status": "Error" if llm_error_detected else "Success"
            }
            
            self.logger.info("✅ Summary generation completed successfully")
            return output_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate summary: {e}")
            return {
                "summary_info": {
                    "timestamp": datetime.now().isoformat(),
                    "source_file": str(json_file_path) if json_file_path else "Direct Data",
                    "error": str(e)
                },
                "summary": f"❌ 要約生成エラー: {e}",
                "processing_status": "Failed"
            }
    
    def _convert_infogetter_to_llm_format(self, infogetter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert InfoGetter JSON format to LocalLLM compatible format
        
        Args:
            infogetter_data: InfoGetter results data
            
        Returns:
            LocalLLM compatible data structure
        """
        try:
            # Extract basic info
            scan_info = infogetter_data.get("scan_info", {})
            sources = infogetter_data.get("sources", {})
            
            # Build summary text
            content_parts = []
            content_parts.append("# FPGA IP Document Scraping Results Summary")
            content_parts.append(f"**Scan Date**: {scan_info.get('timestamp', 'Unknown')}")
            content_parts.append(f"**Total Sources**: {scan_info.get('total_sources', 0)}")
            content_parts.append(f"**Total Documents**: {scan_info.get('total_documents', 0)}")
            content_parts.append("")
            
            # Process each source
            urls = []
            
            for source_name, source_data in sources.items():
                content_parts.append(f"## {source_name.upper()} Documents")
                content_parts.append(f"**Search URL**: {source_data.get('search_url', 'N/A')}")
                content_parts.append(f"**Document Count**: {source_data.get('document_count', 0)}")
                content_parts.append("")
                
                documents = source_data.get("documents", [])
                for i, doc in enumerate(documents[:10]):  # Limit to first 10 documents per source
                    content_parts.append(f"### Document {i+1}: {doc.get('name', 'Untitled')}")
                    content_parts.append(f"- **Category**: {doc.get('category', 'Unknown')}")
                    content_parts.append(f"- **File Type**: {doc.get('file_type', 'Unknown')}")
                    content_parts.append(f"- **Source Type**: {doc.get('source_type', 'Unknown')}")
                    
                    if doc.get('abstract'):
                        content_parts.append(f"- **Abstract**: {doc['abstract'][:200]}...")
                    
                    # Add to URLs list
                    if doc.get('url'):
                        urls.append({
                            "url": doc['url'],
                            "title": doc.get('name', 'Untitled'),
                            "source": source_name,
                            "category": doc.get('category', 'Unknown')
                        })
                    
                    content_parts.append("")
                
                if len(documents) > 10:
                    content_parts.append(f"... and {len(documents) - 10} more documents")
                    content_parts.append("")
            
            # Create LocalLLM compatible format
            llm_data = {
                "title": "FPGA IP Document Collection Summary",
                "content": "\n".join(content_parts),
                "metadata": {
                    "source": "InfoGetter",
                    "scan_timestamp": scan_info.get('timestamp'),
                    "total_documents": scan_info.get('total_documents', 0),
                    "sources": list(sources.keys())
                },
                "urls": urls[:50]  # Limit to 50 URLs to avoid processing overload
            }
            
            return llm_data
            
        except Exception as e:
            self.logger.error(f"Error converting data format: {e}")
            raise
    
    def _create_fallback_summary(self, llm_data: Dict[str, Any], language: str = "ja") -> str:
        """
        Create a simple fallback summary when LocalLLM fails
        
        Args:
            llm_data: Converted LLM format data
            language: Target language
            
        Returns:
            Simple summary string
        """
        try:
            content = llm_data.get("content", "")
            urls = llm_data.get("urls", [])
            
            if language == "ja":
                summary = "📋 **FPGA文書スキャン結果要約**\n\n"
                summary += f"📊 **統計情報**\n"
                
                # Extract document count from content
                lines = content.split('\n')
                doc_count = 0
                sources = []
                
                for line in lines:
                    if "Total Documents" in line:
                        try:
                            doc_count = int(line.split(':')[-1].strip())
                        except:
                            pass
                    elif "## " in line and "Documents" in line:
                        source = line.replace("##", "").replace("Documents", "").strip()
                        sources.append(source)
                
                summary += f"- 総文書数: {doc_count}件\n"
                summary += f"- 情報源: {', '.join(sources)}\n\n"
                
                summary += "🔍 **検索結果**\n"
                summary += "FPGA、DSP、IP Coreに関連する技術文書を収集しました。\n\n"
                
                if urls:
                    summary += "📄 **主要文書**\n"
                    for i, url_info in enumerate(urls[:5], 1):
                        title = url_info.get("title", "Unknown")
                        category = url_info.get("category", "Unknown")
                        summary += f"{i}. {title} ({category})\n"
                
                summary += f"\n⏰ **生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                summary += "🤖 **注記**: LocalLLM処理エラーのため、簡易要約を表示しています。"
                
            else:  # English
                summary = "📋 **FPGA Document Scan Summary**\n\n"
                summary += f"📊 **Statistics**: {doc_count} documents found\n"
                summary += f"🔍 **Content**: Technical documents related to FPGA, DSP, and IP Cores\n"
                summary += f"⏰ **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                summary += "🤖 **Note**: Fallback summary due to LocalLLM processing error."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Fallback summary failed: {e}")
            return f"❌ 要約生成に失敗しました (エラー: {e})"
    
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
                output_path = Path("results") / f"llm_summary_{timestamp}.json"
            else:
                output_path = Path(output_path)
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON with proper formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Summary saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save summary: {e}")
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
            original_scan_info = summary_data.get("original_scan_info", {})
            
            markdown_parts = [
                "# 📊 FPGA IP Document Summary Report",
                "",
                f"**Generated**: {summary_info.get('timestamp', 'Unknown')}",
                f"**Language**: {summary_info.get('language', 'Unknown')}",
                f"**Summary Type**: {summary_info.get('summary_type', 'Unknown')}",
                f"**Original Documents**: {summary_info.get('original_document_count', 0)}",
                f"**Sources**: {', '.join(summary_info.get('original_sources', []))}",
                "",
                "## 🎯 Summary",
                "",
                summary_text,
                "",
                "## 📈 Original Scan Information",
                "",
                f"- **Scan Timestamp**: {original_scan_info.get('timestamp', 'Unknown')}",
                f"- **Total Sources**: {original_scan_info.get('total_sources', 0)}",
                f"- **Total Documents**: {original_scan_info.get('total_documents', 0)}",
                "",
                "---",
                "*Generated by InfoGetter with LocalLLM integration*"
            ]
            
            return "\n".join(markdown_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to generate markdown report: {e}")
            return f"❌ Error generating report: {e}"


def demo_usage():
    """Demonstration of LLMSummarizer usage"""
    print("🚀 LLMSummarizer Demo")
    print("=" * 50)
    
    try:
        # Initialize summarizer
        summarizer = LLMSummarizer()
        
        # Check if results file exists
        results_file = Path("results/fpga_documents.json")
        if not results_file.exists():
            print(f"❌ Results file not found: {results_file}")
            print("Please run InfoGetter first to generate results.")
            return
        
        # Generate summary
        print("🤖 Generating Japanese summary...")
        summary_data = summarizer.summarize_json_results(
            results_file,
            language="ja",
            summary_type="detailed",
            max_length=2000
        )
        
        # Save results
        output_path = summarizer.save_summary(summary_data)
        
        # Generate markdown report
        markdown_report = summarizer.generate_markdown_report(summary_data)
        markdown_path = output_path.with_suffix('.md')
        
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        print(f"✅ Summary completed successfully!")
        print(f"📄 JSON Summary: {output_path}")
        print(f"📝 Markdown Report: {markdown_path}")
        print(f"📊 Status: {summary_data.get('processing_status', 'Unknown')}")
        
        # Display first 200 characters of summary
        summary_text = summary_data.get("summary", "")
        if summary_text:
            print(f"\n📋 Summary Preview:")
            print(summary_text[:200] + "..." if len(summary_text) > 200 else summary_text)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    demo_usage()
