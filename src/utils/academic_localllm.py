"""
Academic LocalLLM System - Specialized for Academic Paper Summarization
====================================================================

This system provides Japanese summarization of academic papers using
local LLM models, specifically optimized for technical content.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

# For LLM integration
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    Llama = None

# For Japanese text processing
import unicodedata


class AcademicLocalLLM:
    """
    Academic paper summarization system using local Llama models
    Specialized for Japanese output of technical content
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.logger = logging.getLogger("AcademicLocalLLM")
        self.model = None
        self.model_path = model_path
        self.is_initialized = False
        
        # Academic summarization configuration
        self.config = {
            "max_tokens": 2048,
            "temperature": 0.3,  # Lower temperature for more consistent academic summaries
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "n_ctx": 4096,  # Context window
            "n_threads": 4,
            "verbose": False
        }
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the Llama model for academic summarization"""
        try:
            if not LLAMA_AVAILABLE:
                self.logger.error("❌ llama-cpp-python not available. Install with: pip install llama-cpp-python")
                return
            
            # Find model file
            model_path = self._find_model_file()
            if not model_path:
                self.logger.warning("⚠️ No Llama model found. Academic summarization will use enhanced template mode.")
                return
            
            self.logger.info(f"🚀 Loading Llama model for academic summarization: {model_path}")
            
            # Initialize Llama model with academic-optimized settings
            self.model = Llama(
                model_path=str(model_path),
                n_ctx=self.config["n_ctx"],
                n_threads=self.config["n_threads"],
                verbose=self.config["verbose"]
            )
            
            self.model_path = model_path
            self.is_initialized = True
            self.logger.info("✅ Academic LocalLLM initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Llama model: {e}")
            self.logger.info("📝 Falling back to enhanced academic template mode")
    
    def _find_model_file(self) -> Optional[Path]:
        """Find available Llama model file"""
        # Search paths for model files
        search_paths = [
            "models/llama-2-7b-chat.gguf",
            "models/llama-2-13b-chat.gguf", 
            "models/llama-2-7b.gguf",
            "models/CodeLlama-7b-Instruct.gguf",
            "models/mistral-7b-instruct.gguf",
            "../models/llama-2-7b-chat.gguf",
            "models/*.gguf"
        ]
        
        for pattern in search_paths:
            if "*" in pattern:
                # Glob pattern
                matches = list(Path(".").glob(pattern))
                if matches:
                    return matches[0]
            else:
                path = Path(pattern)
                if path.exists():
                    return path
        
        return None
    
    def summarize_academic_papers(self, papers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize academic papers with focus on technical innovations
        
        Args:
            papers_data: List of paper data dictionaries
            
        Returns:
            Summary result with technical focus
        """
        try:
            self.logger.info(f"📚 Processing {len(papers_data)} academic papers")
            
            # Extract and prepare academic content
            academic_content = self._prepare_academic_content(papers_data)
            
            # Generate technical summary
            if self.is_initialized and self.model:
                summary = self._generate_llm_summary(academic_content)
                processing_method = "llama-academic"
            else:
                summary = self._generate_enhanced_template_summary(academic_content)
                processing_method = "enhanced-template-academic"
            
            # Post-process for academic formatting
            formatted_summary = self._format_academic_summary(summary)
            
            return {
                "summary": formatted_summary,
                "technical_highlights": self._extract_technical_highlights(papers_data),
                "innovation_analysis": self._analyze_innovations(papers_data),
                "processing_method": processing_method,
                "paper_count": len(papers_data),
                "language": "ja",
                "model_info": {
                    "model_path": str(self.model_path) if self.model_path else "template-mode",
                    "llm_active": self.is_initialized,
                    "specialization": "academic-japanese"
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Academic summarization failed: {e}")
            raise RuntimeError(f"Academic summarization error: {e}")
    
    def _prepare_academic_content(self, papers_data: List[Dict[str, Any]]) -> str:
        """Prepare academic content for summarization"""
        content_parts = []
        
        for i, paper in enumerate(papers_data, 1):
            title = paper.get('title', 'タイトル不明')
            abstract = paper.get('abstract', '')
            content = paper.get('content', '')
            authors = paper.get('authors', [])
            
            # Format each paper
            paper_text = f"""
論文 {i}: {title}
著者: {', '.join(authors) if authors else '不明'}
要旨: {abstract}
内容: {content}
---
"""
            content_parts.append(paper_text)
        
        return "\n".join(content_parts)
    
    def _generate_llm_summary(self, content: str) -> str:
        """Generate summary using Llama LLM"""
        # Academic-focused prompt in Japanese
        prompt = f"""以下の学術論文を詳細に要約してください。特に技術的な特徴、新規性、革新性に焦点を当てた日本語での要約を作成してください。

学術論文内容:
{content}

要約の指針:
1. 各論文の主要な技術的貢献を明確に記述
2. 新規性や革新的なアプローチを強調
3. 実用的な応用可能性を言及
4. 技術的な詳細を含む包括的な要約
5. 日本語での自然な表現

詳細要約:"""

        try:
            # Generate with academic-optimized parameters
            response = self.model(
                prompt,
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                top_p=self.config["top_p"],
                repeat_penalty=self.config["repeat_penalty"],
                stop=["---", "\n\n\n"]
            )
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return self._generate_enhanced_template_summary(content)
    
    def _generate_enhanced_template_summary(self, content: str) -> str:
        """Generate enhanced template-based academic summary"""
        self.logger.info("📝 Using enhanced academic template mode")
        
        # Extract key information using pattern matching
        technical_terms = self._extract_technical_terms(content)
        innovations = self._extract_innovation_keywords(content)
        methods = self._extract_methodology_keywords(content)
        
        # Generate structured academic summary
        summary_parts = [
            "## 学術論文要約 - 技術的特徴と新規性分析\n",
            f"**処理論文数**: {content.count('論文')}件\n",
            f"**主要技術分野**: {', '.join(technical_terms[:5])}\n",
            f"**革新的手法**: {', '.join(innovations[:3])}\n",
            f"**研究手法**: {', '.join(methods[:3])}\n\n",
            "### 技術的貢献の詳細分析:\n"
        ]
        
        # Analyze each paper section
        papers = content.split('---')
        for i, paper_section in enumerate(papers, 1):
            if paper_section.strip():
                paper_analysis = self._analyze_paper_section(paper_section)
                summary_parts.append(f"\n**論文{i}の技術的特徴**:\n{paper_analysis}\n")
        
        # Add innovation analysis
        summary_parts.extend([
            "\n### 新規性・革新性の評価:\n",
            self._generate_innovation_assessment(content),
            "\n### 実用化可能性:\n",
            self._generate_practical_assessment(content)
        ])
        
        return "".join(summary_parts)
    
    def _extract_technical_terms(self, content: str) -> List[str]:
        """Extract technical terms from content"""
        # Technical term patterns for various fields
        technical_patterns = [
            r'(?i)\b(?:FPGA|GPU|CPU|AI|ML|deep learning|neural network|algorithm|optimization|performance|efficiency|throughput|latency|bandwidth|acceleration|parallel|distributed|cloud|edge|IoT|blockchain|quantum|security|encryption|compression|processing|computing|architecture|framework|protocol|interface|implementation|methodology|analysis|evaluation|benchmark|comparison|improvement|enhancement|innovation|novel|advanced|state-of-the-art)\b',
            r'(?i)\b(?:機械学習|深層学習|人工知能|ニューラルネットワーク|アルゴリズム|最適化|性能|効率|スループット|レイテンシ|帯域幅|高速化|並列|分散|クラウド|エッジ|暗号化|圧縮|処理|計算|アーキテクチャ|フレームワーク|プロトコル|インターフェース|実装|手法|分析|評価|ベンチマーク|比較|改善|拡張|革新|新規|先進的)\b'
        ]
        
        terms = set()
        for pattern in technical_patterns:
            matches = re.findall(pattern, content)
            terms.update([term.lower() for term in matches])
        
        return sorted(list(terms))[:10]  # Return top 10 terms
    
    def _extract_innovation_keywords(self, content: str) -> List[str]:
        """Extract innovation-related keywords"""
        innovation_patterns = [
            r'(?i)\b(?:novel|new|innovative|breakthrough|advanced|cutting-edge|state-of-the-art|improved|enhanced|optimized|revolutionary|pioneering|groundbreaking)\b',
            r'(?i)\b(?:新規|革新的|先進的|最先端|改良|拡張|最適化|革命的|先駆的|画期的|独創的)\b'
        ]
        
        keywords = set()
        for pattern in innovation_patterns:
            matches = re.findall(pattern, content)
            keywords.update([kw.lower() for kw in matches])
        
        return sorted(list(keywords))[:5]
    
    def _extract_methodology_keywords(self, content: str) -> List[str]:
        """Extract methodology-related keywords"""
        method_patterns = [
            r'(?i)\b(?:method|approach|technique|algorithm|framework|model|system|architecture|design|implementation|evaluation|analysis|experiment|simulation|optimization|training|learning|inference|prediction|classification|clustering|detection|recognition)\b',
            r'(?i)\b(?:手法|アプローチ|技術|アルゴリズム|フレームワーク|モデル|システム|アーキテクチャ|設計|実装|評価|分析|実験|シミュレーション|最適化|学習|推論|予測|分類|クラスタリング|検出|認識)\b'
        ]
        
        methods = set()
        for pattern in method_patterns:
            matches = re.findall(pattern, content)
            methods.update([method.lower() for method in matches])
        
        return sorted(list(methods))[:5]
    
    def _analyze_paper_section(self, paper_section: str) -> str:
        """Analyze individual paper section"""
        lines = paper_section.strip().split('\n')
        title_line = next((line for line in lines if line.startswith('論文')), '')
        abstract_line = next((line for line in lines if line.startswith('要旨:')), '')
        
        # Extract key information
        technical_terms = self._extract_technical_terms(paper_section)[:3]
        innovations = self._extract_innovation_keywords(paper_section)[:2]
        
        analysis = f"- 主要技術: {', '.join(technical_terms) if technical_terms else '一般的な研究'}\n"
        analysis += f"- 革新的要素: {', '.join(innovations) if innovations else '従来手法の改良'}\n"
        
        # Analyze abstract for key contributions
        if abstract_line:
            abstract_text = abstract_line.replace('要旨:', '').strip()
            if len(abstract_text) > 50:
                analysis += f"- 主要貢献: {abstract_text[:100]}...\n"
        
        return analysis
    
    def _generate_innovation_assessment(self, content: str) -> str:
        """Generate innovation assessment"""
        innovation_count = len(self._extract_innovation_keywords(content))
        technical_diversity = len(self._extract_technical_terms(content))
        
        if innovation_count > 5 and technical_diversity > 8:
            return "高度な革新性を含む研究群。複数の技術分野で新規性のあるアプローチが提案されています。"
        elif innovation_count > 2 and technical_diversity > 5:
            return "中程度の革新性を持つ研究群。既存技術の改良と新しいアプローチが組み合わされています。"
        else:
            return "従来研究の改良・拡張が中心。段階的な技術発展が期待されます。"
    
    def _generate_practical_assessment(self, content: str) -> str:
        """Generate practical application assessment"""
        practical_terms = len(re.findall(r'(?i)\b(?:application|implementation|practical|real-world|deployment|system|performance|efficiency|実用|応用|実装|システム|性能|効率)\b', content))
        
        if practical_terms > 10:
            return "実用化可能性が高い研究群。システム実装や性能評価が重視されています。"
        elif practical_terms > 5:
            return "実用化への道筋が示されている研究群。更なる検証が必要です。"
        else:
            return "基礎研究段階の研究群。実用化には追加の開発が必要です。"
    
    def _extract_technical_highlights(self, papers_data: List[Dict[str, Any]]) -> List[str]:
        """Extract technical highlights from papers"""
        highlights = []
        
        for paper in papers_data:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            
            # Look for performance metrics, innovations, etc.
            combined_text = f"{title} {abstract}"
            technical_terms = self._extract_technical_terms(combined_text)[:2]
            
            if technical_terms:
                highlights.append(f"{title}: {', '.join(technical_terms)}")
        
        return highlights[:5]  # Return top 5 highlights
    
    def _analyze_innovations(self, papers_data: List[Dict[str, Any]]) -> List[str]:
        """Analyze innovations across papers"""
        all_innovations = []
        
        for paper in papers_data:
            content = f"{paper.get('title', '')} {paper.get('abstract', '')} {paper.get('content', '')}"
            innovations = self._extract_innovation_keywords(content)
            if innovations:
                all_innovations.extend(innovations)
        
        # Count and return most common innovations
        from collections import Counter
        innovation_counts = Counter(all_innovations)
        return [f"{innovation} ({count}件)" for innovation, count in innovation_counts.most_common(5)]
    
    def _format_academic_summary(self, summary: str) -> str:
        """Format summary for academic presentation"""
        # Clean up and format the summary
        formatted = summary.strip()
        
        # Ensure proper Japanese formatting
        formatted = unicodedata.normalize('NFKC', formatted)
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        formatted += f"\n\n---\n生成日時: {timestamp}\n生成システム: Academic LocalLLM"
        
        return formatted
    
    def is_available(self) -> bool:
        """Check if the academic LLM system is available"""
        return LLAMA_AVAILABLE or True  # Always available in template mode
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "llama_available": LLAMA_AVAILABLE,
            "model_initialized": self.is_initialized,
            "model_path": str(self.model_path) if self.model_path else None,
            "specialization": "academic-japanese-summarization",
            "fallback_mode": "enhanced-template" if not self.is_initialized else None
        }
