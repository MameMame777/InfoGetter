"""
Mistral-7B-Instruct Summarizer for Academic Content

This module provides genuine local LLM functionality using Mistral-7B-Instruct:
- Mistral-7B-Instruct model processing (Llama-2 removed per user request)
- Individual and overall document summarization
- Japanese language summarization
- Long text support with chunking
- Comprehensive processing metrics
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.document import Document


class MistralSummarizer:
    """
    Academic-optimized summarizer using Mistral-7B-Instruct
    
    This class provides genuine local LLM functionality with:
    - Mistral-7B-Instruct model processing
    - Individual paper summarization
    - Overall collection summarization
    - Japanese language output
    - Long text support
    """
    
    def __init__(self):
        """Initialize Mistral summarizer with academic-optimized model"""
        self.logger = logging.getLogger(__name__)
        self.llm = None
        
        # Mistral-7B-Instruct as primary model (Llama-2 removed per user request)
        self.model_path = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        self.is_initialized = False
        
        # Processing metrics
        self.total_processing_time = 0
        self.processed_documents = 0
        
        # Initialize the Mistral model
        try:
            self._initialize_mistral_model()
        except RuntimeError as e:
            self.logger.warning(f"⚠️ Mistral model initialization failed: {e}")
            self.is_initialized = False
    
    def _initialize_mistral_model(self) -> bool:
        """
        Initialize the Mistral-7B-Instruct model using llama-cpp-python
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Try to import llama-cpp-python
            from llama_cpp import Llama
            
            # Check if Mistral model file exists
            if not os.path.exists(self.model_path):
                self.logger.error(f"❌ Mistral model file not found: {self.model_path}")
                self.logger.info("📥 Please download Mistral-7B-Instruct model first")
                return False
            
            # Initialize Mistral model with optimized settings for academic content
            self.logger.info("🧠 Initializing Mistral-7B-Instruct for academic summarization...")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=8192,      # Large context window for academic papers
                n_threads=6,     # Optimized CPU usage
                n_gpu_layers=0,  # CPU-only processing
                verbose=False,   # Reduce output
                n_batch=512,     # Processing batch size
                use_mlock=True   # Memory stability
            )
            
            self.is_initialized = True
            self.logger.info("✅ Mistral-7B-Instruct initialized successfully for academic work")
            return True
            
        except ImportError:
            self.logger.error("❌ llama-cpp-python not installed")
            self.logger.info("💡 Install with: pip install llama-cpp-python")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Mistral model: {e}")
            raise RuntimeError(f"Mistral model initialization failed: {e}")
    
    def _split_text_into_chunks(self, text: str, max_tokens: int = 3000) -> List[str]:
        """
        Split long text into manageable chunks for processing
        
        Args:
            text: Text to split
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks
        """
        # Simple word-based splitting (approximate token estimation)
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Rough estimation: 1 token ≈ 0.75 words
        words_per_chunk = int(max_tokens * 0.75)
        
        for word in words:
            current_chunk.append(word)
            current_size += 1
            
            if current_size >= words_per_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
        
        # Add remaining words
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _summarize_long_text(self, text: str, language: str = "japanese") -> str:
        """
        Summarize long text by processing in chunks and combining results
        
        Args:
            text: Long text to summarize
            language: Target language for summary
            
        Returns:
            Combined summary of all chunks
        """
        try:
            # Check if text is short enough for direct processing
            word_count = len(text.split())
            if word_count <= 2000:  # Direct processing for shorter texts
                return self._generate_mistral_summary(text, language)
            
            self.logger.info(f"📄 Processing long text ({word_count} words) in chunks...")
            
            # Split into chunks
            chunks = self._split_text_into_chunks(text, max_tokens=3000)
            chunk_summaries = []
            
            for i, chunk in enumerate(chunks):
                self.logger.info(f"🔄 Processing chunk {i+1}/{len(chunks)}...")
                
                # Create chunk-specific prompt
                chunk_prompt = f"""
以下は長い文書の一部（{i+1}/{len(chunks)}）です。この部分を簡潔に要約してください：

{chunk}

要約："""
                
                chunk_summary = self._generate_mistral_summary(chunk_prompt, language)
                chunk_summaries.append(f"部分{i+1}: {chunk_summary}")
                
                # Brief pause between chunks to prevent overload
                time.sleep(0.5)
            
            # Combine all chunk summaries
            combined_text = "\n\n".join(chunk_summaries)
            
            # Generate final comprehensive summary
            final_prompt = f"""
以下は文書の各部分の要約です。これらを統合して、全体的で一貫性のある包括的な要約を作成してください：

{combined_text}

統合された最終要約："""
            
            final_summary = self._generate_mistral_summary(final_prompt, language)
            
            self.logger.info(f"✅ Long text summarization completed ({len(chunks)} chunks processed)")
            return final_summary
            
        except Exception as e:
            self.logger.error(f"❌ Long text summarization failed: {e}")
            return f"❌ Long text processing error: {str(e)}"
    
    def _clean_content_for_summarization(self, content: str) -> Optional[str]:
        """
        Clean content by removing template artifacts and formatting issues
        
        Args:
            content: Raw content that may contain template artifacts
            
        Returns:
            Cleaned content suitable for summarization, or None if content is insufficient
        """
        # Check if content is too minimal to summarize
        if not content or content == "No content" or len(content.strip()) < 50:
            return None
            
        # Remove common template artifacts
        lines = content.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            'Research Content:',
            'Summary Guidelines:',
            '- Research purpose and background',
            '- Main methods and approaches',
            '- Key findings and results',
            '- Significance and impact',
            'Japanese Summary:',
            'Research Topic:',
            'Methods and Approaches:',
            'Key Findings and Results:',
            'There is a research paper with the following content:'
        ]
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and template artifacts
            if not line or any(pattern in line for pattern in skip_patterns):
                continue
            # Skip lines that look like JSON structure
            if line.startswith('{') or line.startswith('"') or '": ' in line:
                continue
            # Skip lines with datetime objects or HttpUrl
            if 'datetime.datetime' in line or 'HttpUrl' in line or '<DataSourceType.' in line:
                continue
            
            cleaned_lines.append(line)
        
        # Rejoin and limit length
        cleaned_content = '\n'.join(cleaned_lines)
        
        # If content is still too short after cleaning, return None
        if len(cleaned_content.strip()) < 100:
            return None
        
        # If content is still too long, take first portion
        if len(cleaned_content) > 5000:
            cleaned_content = cleaned_content[:5000] + "..."
            
        return cleaned_content
    
    def _clean_mistral_output(self, output: str) -> str:
        """
        Clean Mistral output to remove unwanted formatting artifacts
        
        Args:
            output: Raw output from Mistral
            
        Returns:
            Cleaned output suitable for display
        """
        if not output:
            return output
            
        # Split into lines for processing
        lines = output.split('\n')
        cleaned_lines = []
        consecutive_dashes = 0
        
        for line in lines:
            # Count consecutive lines with many dashes
            if len([c for c in line if c == '-']) > 20:
                consecutive_dashes += 1
                # Skip lines with excessive dashes (likely formatting artifacts)
                if consecutive_dashes > 1:
                    continue
            else:
                consecutive_dashes = 0
                
            # Remove lines that are mostly dashes
            dash_ratio = len([c for c in line if c == '-']) / max(len(line), 1)
            if dash_ratio > 0.8 and len(line) > 10:
                continue
                
            # Remove excessive whitespace and normalize
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        # Rejoin and clean up
        cleaned_output = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in cleaned_output:
            cleaned_output = cleaned_output.replace('\n\n\n', '\n\n')
            
        return cleaned_output.strip()
    
    def _generate_mistral_summary(self, content: str, language: str = "japanese") -> str:
        """
        Generate summary using Mistral-7B-Instruct model
        
        Args:
            content: Text content to summarize
            language: Target language for summary
            
        Returns:
            Generated summary
        """
        if not self.is_initialized:
            return "❌ Mistral model not initialized"
        
        try:
            # Clean content to remove template artifacts
            cleaned_content = self._clean_content_for_summarization(content)
            
            # Skip summarization if content is insufficient
            if cleaned_content is None:
                self.logger.warning("🚫 Skipping summarization - insufficient content after cleaning")
                return "❌ 要約をスキップしました：コンテンツが不十分または403エラーのため利用できません。"
            
            # Create academic-focused prompt for Mistral
            if language.lower() == "japanese":
                prompt = f"""
あなたは学術論文の専門家です。以下の研究論文を日本語で要約してください：

研究内容:
{cleaned_content}

要約の指針：
- 研究の目的と背景
- 主な手法とアプローチ  
- 重要な発見と結果
- 研究の意義と影響

日本語要約："""
            else:
                prompt = f"""
You are an academic expert. Please summarize the following research paper:

Content:
{cleaned_content}

Summary guidelines:
- Research purpose and background
- Main methods and approaches
- Key findings and results
- Research significance and impact

Summary:"""
            
            # Generate summary with Mistral
            start_time = time.time()
            response = self.llm(
                prompt,
                max_tokens=3072,     # Further increased token limit for complete summaries
                temperature=0.3,     # Low temperature for consistent academic output
                top_p=0.9,          # Focused but creative responses
                repeat_penalty=1.1,  # Avoid repetition
                stop=[],             # Remove all stop conditions to allow complete generation
                echo=False
            )
            
            processing_time = time.time() - start_time
            summary = response['choices'][0]['text'].strip()
            
            # Clean the output to remove unwanted formatting artifacts
            summary = self._clean_mistral_output(summary)
            
            self.logger.info(f"🧠 Mistral processing time: {processing_time:.1f}s")
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Mistral generation failed: {e}")
            return f"❌ Mistral processing error: {str(e)}"
    
    def summarize_documents(self, documents: List[Document], language: str = "japanese") -> Dict[str, Any]:
        """
        Summarize collection of documents using Mistral
        
        Args:
            documents: List of Document objects to summarize
            language: Target language for summary
            
        Returns:
            Dict containing summary and metadata
        """
        start_time = time.time()
        
        if not documents:
            return {
                'processing_status': 'Failed',
                'summary': 'No documents provided for summarization',
                'summary_info': {
                    'error': 'Empty document list',
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        # Check if Mistral is available
        if not self.is_initialized:
            self.logger.warning("⚠️ Mistral not available, attempting to initialize...")
            try:
                self._initialize_mistral_model()
            except:
                return {
                    'processing_status': 'Failed',
                    'summary': 'Mistral model not available',
                    'summary_info': {
                        'error': 'Model initialization failed',
                        'timestamp': datetime.now().isoformat()
                    }
                }
        
        try:
            # Prepare combined text for overall summary
            combined_text = ""
            sources = set()
            total_content_length = 0
            
            for doc in documents:
                # Safe attribute access for different document types
                if hasattr(doc, 'title'):
                    title_attr = getattr(doc, 'title')
                    # Check if title is callable (method) or string
                    if callable(title_attr):
                        try:
                            title = title_attr()  # Call the method
                        except:
                            title = str(doc)[:100] + "..."
                    else:
                        title = str(title_attr)  # Convert to string
                elif isinstance(doc, dict):
                    title = doc.get('title', 'Unknown Title')
                else:
                    title = str(doc)[:100] + "..."
                
                if hasattr(doc, 'content'):
                    content = doc.content
                elif isinstance(doc, dict):
                    content = doc.get('content', str(doc))
                else:
                    content = str(doc)
                
                if hasattr(doc, 'source'):
                    source = doc.source
                elif isinstance(doc, dict):
                    source = doc.get('source', 'Unknown')
                else:
                    source = 'Unknown'
                
                doc_content = f"Title: {title}\nContent: {content}\n\n"
                combined_text += doc_content
                total_content_length += len(str(content))
                sources.add(source)
            
            # Check if content is too long and use appropriate processing method
            total_words = len(combined_text.split())
            self.logger.info(f"📊 Processing {len(documents)} documents ({total_words} total words)")
            
            # Use long text processing for large content
            if total_words > 2000:
                self.logger.info("📄 Using long text processing due to large content size")
                overall_summary = self._summarize_long_text(combined_text, language)
            else:
                overall_summary = self._generate_mistral_summary(combined_text, language)
            
            processing_time = time.time() - start_time
            
            # Create summary result
            result = {
                'processing_status': 'Success',
                'summary': overall_summary,
                'summary_info': {
                    'timestamp': datetime.now().isoformat(),
                    'language': language,
                    'processing_time_seconds': round(processing_time, 2),
                    'original_document_count': len(documents),
                    'original_sources': list(sources),
                    'model_info': {
                        'model_name': 'Mistral-7B-Instruct-v0.2',
                        'model_type': 'Academic Local LLM',
                        'model_path': self.model_path,
                        'backend': 'llama-cpp-python',
                        'is_genuine_llm': True,
                        'context_window': 8192,
                        'processing_time': round(processing_time, 2),
                        'tokens_generated': len(overall_summary.split()),  # Approximate token count
                        'context_length': len(combined_text)
                    },
                    'summary_length': len(overall_summary),
                    'processing_method': 'mistral-academic'
                }
            }
            
            self.logger.info(f"✅ Mistral overall summary completed in {processing_time:.1f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Mistral summarization failed: {e}")
            return {
                'processing_status': 'Failed',
                'summary': f'Mistral processing error: {str(e)}',
                'summary_info': {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'processing_time_seconds': time.time() - start_time
                }
            }
    
    def summarize_individual_papers(self, documents: List[Document], language: str = "japanese") -> Dict[str, Any]:
        """
        Summarize each document individually using Mistral
        
        Args:
            documents: List of Document objects to summarize individually
            language: Target language for summaries
            
        Returns:
            Dict containing individual summaries and metadata
        """
        if not documents:
            return {
                'processing_status': 'Failed',
                'individual_summaries': [],
                'summary_info': {'error': 'No documents provided'}
            }
        
        if not self.is_initialized:
            self.logger.warning("⚠️ Mistral not available for individual summarization")
            return {
                'processing_status': 'Failed',
                'individual_summaries': [],
                'summary_info': {'error': 'Mistral model not initialized'}
            }
        
        individual_summaries = []
        total_start_time = time.time()
        
        self.logger.info(f"🧠 Starting individual Mistral summarization for {len(documents)} papers...")
        
        for i, doc in enumerate(documents):
            try:
                start_time = time.time()
                
                # Safe attribute access for individual document processing
                if hasattr(doc, 'title'):
                    title_attr = getattr(doc, 'title')
                    # Check if title is callable (method) or string
                    if callable(title_attr):
                        try:
                            title = title_attr()  # Call the method
                        except:
                            title = str(doc)[:100] + "..."
                    else:
                        title = str(title_attr)  # Convert to string
                elif isinstance(doc, dict):
                    title = doc.get('title', 'Unknown Title')
                else:
                    title = str(doc)[:100] + "..."
                
                if hasattr(doc, 'content'):
                    content = doc.content
                elif isinstance(doc, dict):
                    content = doc.get('content', str(doc))
                else:
                    content = str(doc)
                
                paper_text = f"Title: {title}\nContent: {content}"
                
                # Check if individual document is long and use appropriate processing
                doc_word_count = len(str(content).split())
                self.logger.info(f"🔄 Processing document {i+1}/{len(documents)}: {title} ({doc_word_count} words)")
                
                if doc_word_count > 2000:
                    self.logger.info(f"📄 Document {i+1} is long, using chunk processing")
                    individual_summary = self._summarize_long_text(str(content), language)
                else:
                    individual_summary = self._generate_mistral_summary(paper_text, language)
                
                processing_time = time.time() - start_time
                
                # Safe attribute access for summary data
                url = getattr(doc, 'url', '') if hasattr(doc, 'url') else (doc.get('url', '') if isinstance(doc, dict) else '')
                # Convert HttpUrl to string for JSON serialization
                url = str(url) if url else ''
                source = getattr(doc, 'source', 'Unknown') if hasattr(doc, 'source') else (doc.get('source', 'Unknown') if isinstance(doc, dict) else 'Unknown')
                category = getattr(doc, 'category', 'Unknown') if hasattr(doc, 'category') else (doc.get('category', 'Unknown') if isinstance(doc, dict) else 'Unknown')
                
                summary_data = {
                    'paper_index': i + 1,
                    'title': title,
                    'url': url,
                    'source': source,
                    'category': category,
                    'japanese_summary': individual_summary,
                    'processing_time': round(processing_time, 2),
                    'summary_length': len(individual_summary),
                    'model_used': 'Mistral-7B-Instruct-v0.2',
                    'processing_method': 'mistral-individual'
                }
                
                individual_summaries.append(summary_data)
                self.logger.info(f"✅ Individual summary {i+1} completed in {processing_time:.1f}s")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to summarize document {i+1}: {e}")
                
                # Safe error summary creation
                error_title = title if 'title' in locals() else 'Unknown Title'
                
                error_summary = {
                    'paper_index': i + 1,
                    'title': error_title,
                    'error': str(e),
                    'japanese_summary': f"❌ 要約生成エラー: {str(e)}",
                    'processing_time': 0,
                    'model_used': 'Mistral-7B-Instruct-v0.2'
                }
                individual_summaries.append(error_summary)
        
        total_processing_time = time.time() - total_start_time
        
        # Save individual summaries to file
        try:
            output_path = "results/individual_summaries_mistral.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(individual_summaries, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Individual summaries saved to {output_path}")
            
            return {
                'processing_status': 'Success',
                'individual_summaries': individual_summaries,
                'summary_info': {
                    'total_papers': len(documents),
                    'successful_summaries': len([s for s in individual_summaries if 'error' not in s]),
                    'failed_summaries': len([s for s in individual_summaries if 'error' in s]),
                    'total_processing_time': round(total_processing_time, 2),
                    'output_file': output_path,
                    'timestamp': datetime.now().isoformat(),
                    'model_used': 'Mistral-7B-Instruct-v0.2'
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save individual summaries: {e}")
            return {
                'processing_status': 'Failed',
                'individual_summaries': individual_summaries,
                'summary_info': {'error': f'Save failed: {str(e)}'}
            }
    
    def summarize_json_results(self, json_file_path: str, language: str = "japanese") -> Dict[str, Any]:
        """
        Summarize results from JSON file using Mistral
        
        Args:
            json_file_path: Path to the JSON file containing documents
            language: Target language for summarization
            
        Returns:
            Dict containing academic summarization results
        """
        try:
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract documents from JSON structure 
            all_documents = []
            
            # Handle the correct JSON structure with 'sources' key
            sources_data = data.get('sources', {})
            for source_name, source_info in sources_data.items():
                if isinstance(source_info, dict) and 'documents' in source_info:
                    documents_list = source_info['documents']
                    if isinstance(documents_list, list):
                        for doc_data in documents_list:
                            if isinstance(doc_data, dict):
                                # Create Document-like object
                                mock_doc = type('Document', (), {
                                    'title': doc_data.get('name', doc_data.get('title', 'Unknown Title')),
                                    'content': doc_data.get('abstract', doc_data.get('content', 'No content available')),
                                    'source': doc_data.get('source', source_name),
                                    'url': doc_data.get('url', ''),
                                    'category': doc_data.get('category', 'Unknown')
                                })()
                                all_documents.append(mock_doc)
            
            if not all_documents:
                return {
                    'processing_status': 'Failed',
                    'summary': 'No documents found in JSON file',
                    'summary_info': {
                        'error': 'Empty document list',
                        'timestamp': datetime.now().isoformat()
                    }
                }
            
            self.logger.info(f"🧠 Mistral processing {len(all_documents)} documents from JSON")
            
            # Generate overall academic summary
            overall_result = self.summarize_documents(all_documents, language)
            
            # Also generate individual academic summaries
            try:
                self.summarize_individual_papers(all_documents, language)
                self.logger.info("✅ Individual academic summaries also generated")
            except Exception as e:
                self.logger.warning(f"⚠️ Individual academic summary generation failed: {e}")
            
            return overall_result
            
        except Exception as e:
            self.logger.error(f"❌ Mistral processing failed for {json_file_path}: {e}")
            return {
                'processing_status': 'Failed',
                'summary': f'Mistral error: {str(e)}',
                'summary_info': {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            }


# For backwards compatibility
RealLlamaSummarizer = MistralSummarizer
LocalLLMSummarizer = MistralSummarizer
