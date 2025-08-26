"""
Test Academic LocalLLM System
===========================
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.academic_localllm import AcademicLocalLLM

def test_academic_localllm():
    """Test the Academic LocalLLM system"""
    print("🧪 Testing Academic LocalLLM System...")
    
    try:
        # Initialize Academic LocalLLM
        print("\n1. Initializing Academic LocalLLM...")
        academic_llm = AcademicLocalLLM()
        
        # Check if it's available
        print(f"   Available: {academic_llm.is_available()}")
        
        # Get model info
        model_info = academic_llm.get_model_info()
        print(f"   Model Info: {json.dumps(model_info, indent=2, ensure_ascii=False)}")
        
        # Create test paper data
        print("\n2. Creating test academic paper data...")
        test_papers = [
            {
                "title": "Deep Learning Accelerators on FPGA: A Novel Architecture for High-Performance Computing",
                "abstract": "This paper presents a novel FPGA-based architecture for deep learning acceleration. We propose an innovative approach that combines parallel processing with optimized memory hierarchy to achieve significant performance improvements.",
                "content": "Our methodology involves implementing custom processing units on FPGA fabric with specialized memory controllers. Experimental results show 5x speedup compared to traditional CPU implementations.",
                "authors": ["Tanaka, H.", "Yamada, K.", "Suzuki, M."]
            },
            {
                "title": "Quantum-Enhanced Machine Learning for Cryptographic Security",
                "abstract": "We introduce a quantum-enhanced machine learning framework for advanced cryptographic applications. The proposed system leverages quantum computing principles to enhance security analysis.",
                "content": "The framework incorporates quantum algorithms for pattern recognition and cryptographic key analysis. Performance evaluation demonstrates superior security detection capabilities.",
                "authors": ["Smith, J.", "Johnson, A."]
            }
        ]
        
        print(f"   Test papers: {len(test_papers)} academic papers")
        
        # Test summarization
        print("\n3. Testing academic paper summarization...")
        result = academic_llm.summarize_academic_papers(test_papers)
        
        print(f"\n✅ Academic LocalLLM Test Results:")
        print(f"   Processing Method: {result.get('processing_method')}")
        print(f"   Paper Count: {result.get('paper_count')}")
        print(f"   Language: {result.get('language')}")
        print(f"   Model Info: {result.get('model_info')}")
        
        print(f"\n📄 Generated Summary:")
        print("=" * 60)
        summary = result.get('summary', '')
        print(summary)
        print("=" * 60)
        
        print(f"\n🔬 Technical Highlights:")
        for highlight in result.get('technical_highlights', []):
            print(f"   • {highlight}")
        
        print(f"\n💡 Innovation Analysis:")
        for innovation in result.get('innovation_analysis', []):
            print(f"   • {innovation}")
        
        print(f"\n📊 Summary Statistics:")
        print(f"   • Summary length: {len(summary)} characters")
        print(f"   • Contains Japanese: {'は' in summary or 'の' in summary}")
        print(f"   • Technical focus: {'技術' in summary or 'technical' in summary.lower()}")
        
        print("\n✅ Academic LocalLLM test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Academic LocalLLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_academic_localllm()
    exit(0 if success else 1)
