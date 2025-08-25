#!/usr/bin/env python3
"""
LocalLLM Integration for InfoGetter
===================================

🚨 CRITICAL REQUIREMENT: MUST USE LocalLLM from https://github.com/MameMame777/LocalLLM
⚠️  DO NOT CHANGE TO OTHER LLM LIBRARIES WITHOUT CLIENT APPROVAL

Integrates LocalLLM summarization functionality with InfoGetter scraping results.
Uses the specified LocalLLM package for Japanese translation and summarization.

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
    """LocalLLM integration for summarizing InfoGetter results using specified LocalLLM package"""
    
    def __init__(self):
        """Initialize LLM Summarizer with LocalLLM package from GitHub requirement"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Check if LocalLLM (from GitHub requirement) is available and working
        if not self._check_and_import_localllm():
            self.logger.warning(
                "🔄 LocalLLM (GitHub: MameMame777/LocalLLM) not available or has dependency issues. "
                "Installing and configuring required LocalLLM package..."
            )
            # Attempt to install the required LocalLLM package
            if not self._install_localllm():
                self.logger.warning("🔄 Using fallback summarization until LocalLLM is properly installed.")
                self.localllm_available = False
            else:
                self.localllm_available = True
        else:
            self.localllm_available = True
            
        self.logger.info("✅ LLMSummarizer initialized with LocalLLM package requirement")
    
    def _install_localllm(self) -> bool:
        """Install the required LocalLLM package from GitHub"""
        try:
            import subprocess
            import sys
            
            self.logger.info("📦 Installing LocalLLM from https://github.com/MameMame777/LocalLLM...")
            
            # Install directly from GitHub repository
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "git+https://github.com/MameMame777/LocalLLM.git"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ LocalLLM package installed successfully")
                return self._check_and_import_localllm()
            else:
                self.logger.error(f"❌ Failed to install LocalLLM: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error installing LocalLLM package: {e}")
            return False
    
    def _check_and_import_localllm(self) -> bool:
        """Check if LocalLLM package (from GitHub requirement) is available"""
        try:
            # Import the required LocalLLM package
            import localllm
            
            self.logger.info("✅ LocalLLM package (GitHub: MameMame777/LocalLLM) is available")
            self.localllm = localllm
            return True
            
        except ImportError as e:
            self.logger.error(f"❌ Failed to import LocalLLM package: {e}")
            self.logger.error("❌ Required package: https://github.com/MameMame777/LocalLLM")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error checking LocalLLM availability: {e}")
            return False
    
    def summarize_json_results(
        self, 
        json_file_path_or_data: Union[str, Path, Dict[str, Any]],
        language: str = "ja",
        summary_type: str = "detailed",
        max_length: int = 2000
    ) -> Dict[str, Any]:
        """
        Summarize InfoGetter JSON results using required LocalLLM package
        
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
                json_file_path = Path(json_file_path_or_data)
                self.logger.info(f"📄 Loading results from: {json_file_path}")
                
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    results_data = json.load(f)
            else:
                json_file_path = None
                results_data = json_file_path_or_data
                self.logger.info("📄 Using provided dictionary data")
            
            # Log data source
            if json_file_path:
                self.logger.info(f"📄 Loading results from: {json_file_path}")
            else:
                self.logger.info("📄 Using provided dictionary data")
            
            # Prepare summary configuration
            self.logger.info(f"🤖 Generating {language} summary...")
            
            # Convert to LocalLLM format
            llm_data = self._convert_infogetter_to_llm_format(results_data)
            
            # Generate summary using LocalLLM or fallback
            if self.localllm_available:
                summary_result = self._generate_localllm_summary(llm_data, language, summary_type, max_length)
                generation_method = "localllm"
                llm_error_detected = False
                llm_error_message = "LocalLLM processing successful"
            else:
                self.logger.info("🔄 Using fallback summarization (LocalLLM not available)")
                summary_result = self._create_fallback_summary(llm_data, language)
                generation_method = "fallback"
                llm_error_detected = True
                llm_error_message = "LocalLLM libraries not available - CRITICAL: Do not send email"
            
            # Check if summary contains error indicators (additional safety)
            error_indicators = ["LocalLLM処理エラー", "簡易要約", "フォールバック", "エラー", "処理エラー"]
            if any(indicator in summary_result for indicator in error_indicators):
                llm_error_detected = True
                llm_error_message = "LLM processing error detected - CRITICAL: Do not send email"
            
            # CRITICAL: Mark processing as FAILED if LLM error detected
            processing_status = "Failed" if llm_error_detected else "Success"
            
            # Prepare output with STRICT LLM error detection for email safety
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
                    "generation_method": generation_method,
                    "email_safe": not llm_error_detected  # Explicit email safety flag
                },
                "processing_status": processing_status,
                "summary": summary_result,
                "original_data_summary": self._create_data_summary(results_data)
            }
            
            self.logger.info("✅ Summary generation completed successfully")
            return output_data
            
        except Exception as e:
            self.logger.error(f"❌ Summary generation failed: {e}")
            # Return safe error response
            return {
                "summary_info": {
                    "timestamp": datetime.now().isoformat(),
                    "llm_error_detected": True,
                    "llm_error_message": f"Summary generation failed: {str(e)}",
                    "generation_method": "error",
                    "email_safe": False
                },
                "processing_status": "Failed",
                "summary": f"LocalLLM処理エラー: {str(e)}",
                "original_data_summary": "処理エラーのため利用できません"
            }
    
    def _generate_localllm_summary(
        self, 
        llm_data: Dict[str, Any], 
        language: str, 
        summary_type: str, 
        max_length: int
    ) -> str:
        """
        Generate summary using the required LocalLLM package
        
        Args:
            llm_data: Converted LLM format data
            language: Target language
            summary_type: Summary type
            max_length: Maximum length
            
        Returns:
            Generated summary string
        """
        try:
            # Use the required LocalLLM package for summarization
            self.logger.info("🤖 Using LocalLLM package for summary generation")
            
            # Create summary prompt based on data
            content_parts = []
            content_parts.append("# FPGA IP Document Scraping Results Summary")
            
            scan_info = llm_data.get("scan_info", {})
            content_parts.append(f"**Scan Date**: {scan_info.get('timestamp', 'Unknown')}")
            content_parts.append(f"**Total Sources**: {scan_info.get('total_sources', 0)}")
            content_parts.append(f"**Total Documents**: {scan_info.get('total_documents', 0)}")
            content_parts.append("")
            
            # Add source details
            sources = llm_data.get("sources", {})
            for source_name, source_data in sources.items():
                content_parts.append(f"## {source_name.upper()} Documents")
                content_parts.append(f"**Document Count**: {source_data.get('document_count', 0)}")
                
                documents = source_data.get('documents', [])
                for i, doc in enumerate(documents[:3]):  # Limit to first 3 for prompt
                    content_parts.append(f"### Document {i+1}: {doc.get('name', 'Untitled')}")
                    content_parts.append(f"- **Category**: {doc.get('category', 'Unknown')}")
                    content_parts.append(f"- **File Type**: {doc.get('file_type', 'Unknown')}")
                    if doc.get('abstract'):
                        content_parts.append(f"- **Abstract**: {doc['abstract'][:200]}...")
                    content_parts.append("")
                
                if len(documents) > 3:
                    content_parts.append(f"... and {len(documents) - 3} more documents")
                content_parts.append("")
            
            prompt_content = "\n".join(content_parts)
            
            # Configure LocalLLM parameters based on language and type
            if language == "ja":
                system_prompt = f"""あなたはFPGA技術の専門家です。以下のスクレイピング結果を日本語で{summary_type}に要約してください。
                
要約の要件:
- 最大{max_length}文字以内
- 技術的に正確で読みやすい内容
- 各ソースの重要な情報を含める
- マークダウン形式で出力"""
            else:
                system_prompt = f"""You are an FPGA technology expert. Please provide a {summary_type} summary of the following scraping results in English.
                
Summary requirements:
- Maximum {max_length} characters
- Technically accurate and readable
- Include important information from each source
- Output in markdown format"""
            
            # Use LocalLLM package for generation
            summary_result = self.localllm.generate_summary(
                content=prompt_content,
                system_prompt=system_prompt,
                max_length=max_length,
                language=language
            )
            
            self.logger.info("✅ LocalLLM summary generated successfully")
            return summary_result
            
        except Exception as e:
            self.logger.error(f"❌ LocalLLM summary generation failed: {e}")
            raise
    
    def _convert_infogetter_to_llm_format(self, infogetter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert InfoGetter JSON format to LocalLLM compatible format
        
        Args:
            infogetter_data: InfoGetter results data
            
        Returns:
            LocalLLM compatible data structure
        """
        try:
            return infogetter_data  # InfoGetter format is already compatible
            
        except Exception as e:
            self.logger.error(f"❌ Format conversion failed: {e}")
            return infogetter_data
    
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
            if language == "ja":
                summary_parts = ["# FPGA IP文書収集結果（簡易要約）"]
                summary_parts.append("") 
                summary_parts.append("⚠️ LocalLLM処理エラーのため、簡易要約を表示しています。")
                summary_parts.append("")
            else:
                summary_parts = ["# FPGA IP Document Collection Results (Simple Summary)"]
                summary_parts.append("")
                summary_parts.append("⚠️ LocalLLM processing error - showing simple summary.")
                summary_parts.append("")
            
            # Add basic scan information
            scan_info = llm_data.get("scan_info", {})
            if language == "ja":
                summary_parts.append(f"**収集日時**: {scan_info.get('timestamp', '不明')}")
                summary_parts.append(f"**総ソース数**: {scan_info.get('total_sources', 0)}")
                summary_parts.append(f"**総文書数**: {scan_info.get('total_documents', 0)}")
            else:
                summary_parts.append(f"**Collection Date**: {scan_info.get('timestamp', 'Unknown')}")
                summary_parts.append(f"**Total Sources**: {scan_info.get('total_sources', 0)}")
                summary_parts.append(f"**Total Documents**: {scan_info.get('total_documents', 0)}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"❌ Fallback summary creation failed: {e}")
            return "LocalLLM処理エラー: フォールバック要約の生成に失敗しました。"
    
    def _create_data_summary(self, results_data: Dict[str, Any]) -> str:
        """Create a simple data summary for reference"""
        try:
            scan_info = results_data.get("scan_info", {})
            sources = results_data.get("sources", {})
            
            summary_lines = []
            summary_lines.append(f"スキャン実行: {scan_info.get('timestamp', '不明')}")
            summary_lines.append(f"ソース数: {len(sources)}")
            summary_lines.append(f"総文書数: {scan_info.get('total_documents', 0)}")
            
            for source_name, source_data in sources.items():
                doc_count = source_data.get('document_count', 0)
                summary_lines.append(f"- {source_name}: {doc_count}件")
            
            return " / ".join(summary_lines)
            
        except Exception as e:
            self.logger.error(f"❌ Data summary creation failed: {e}")
            return "データ概要作成エラー"


def demo_usage():
    """Demonstration of LLMSummarizer usage with required LocalLLM"""
    print("🚀 LLMSummarizer Demo (LocalLLM Required)")
    print("=" * 50)
    
    try:
        # Initialize summarizer
        summarizer = LLMSummarizer()
        
        # Check if results file exists
        results_file = Path("results/fpga_documents.json")
        if not results_file.exists():
            print(f"❌ Results file not found: {results_file}")
            return
        
        # Generate summary using required LocalLLM
        print("🤖 Generating Japanese summary with LocalLLM...")
        summary_data = summarizer.summarize_json_results(
            results_file,
            language="ja",
            summary_type="detailed",
            max_length=2000
        )
        
        print(f"✅ Summary completed!")
        print(f"📊 Status: {summary_data.get('processing_status', 'Unknown')}")
        print(f"🔒 Email Safe: {summary_data.get('summary_info', {}).get('email_safe', False)}")
        print(f"⚙️ Method: {summary_data.get('summary_info', {}).get('generation_method', 'Unknown')}")
        
        # Display first 200 characters of summary
        summary_text = summary_data.get("summary", "")
        if summary_text:
            print(f"\n📝 Summary Preview:")
            print(summary_text[:200] + "..." if len(summary_text) > 200 else summary_text)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    demo_usage()
