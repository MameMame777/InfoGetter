#!/usr/bin/env python3
"""
Test Mistral model functionality directly
"""

import os

def test_mistral_model():
    """Test Mistral model loading and basic generation"""
    try:
        from llama_cpp import Llama
        
        model_path = 'models/mistral-7b-instruct-v0.2.Q4_K_M.gguf'
        
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return False
        
        print(f"✅ Model file exists: {model_path}")
        print("🧠 Testing Mistral model initialization...")
        
        # Initialize with minimal settings
        llm = Llama(
            model_path=model_path,
            n_ctx=1024,
            n_threads=4,
            verbose=False
        )
        
        print("✅ Mistral model loaded successfully!")
        
        # Test simple generation
        test_prompt = "Hello, this is a test. Please respond in Japanese:"
        response = llm(test_prompt, max_tokens=50, temperature=0.3, stream=False)
        generated_text = str(response['choices'][0]['text']).strip()
        
        print(f"Test response: {generated_text}")
        
        # Test Japanese academic summarization
        academic_prompt = """
あなたは学術論文の専門家です。以下の研究論文を日本語で要約してください：

研究内容:
This paper presents a novel FPGA-based implementation for digital signal processing applications.

日本語要約："""
        
        response = llm(academic_prompt, max_tokens=200, temperature=0.3, stream=False)
        academic_summary = str(response['choices'][0]['text']).strip()
        
        print(f"Academic test summary: {academic_summary}")
        
        return True
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        print("📦 Please install llama-cpp-python")
        return False
    except Exception as e:
        print(f"❌ Error testing Mistral model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mistral_model()
    print(f"\nMistral test result: {'SUCCESS' if success else 'FAILED'}")
