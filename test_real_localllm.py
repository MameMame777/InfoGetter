#!/usr/bin/env python3
"""
Real LocalLLM Test Script
=========================

このスクリプトは、True LocalLLMの動作をテストします。
フォールバック処理なしの純粋なLocalLLM統合です。
"""

import sys
import os
import logging

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.real_localllm_summarizer import RealLocalLLMSummarizer

def test_real_localllm():
    """Real LocalLLMのテスト"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("RealLocalLLMTest")
    logger.info("🚀 Starting Real LocalLLM Test")
    
    try:
        # Real LocalLLM初期化
        logger.info("Initializing Real LocalLLM Summarizer...")
        summarizer = RealLocalLLMSummarizer()
        
        # 利用可能性確認
        logger.info(f"Real LocalLLM Available: {summarizer.is_available()}")
        
        # テストファイルの確認
        test_files = [
            "arxiv_recent_papers.json",
            "results/fpga_documents.json"
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                logger.info(f"📄 Testing with file: {test_file}")
                
                # Real LocalLLM処理の実行
                result = summarizer.summarize_results(test_file)
                
                # 結果表示
                logger.info("✅ Real LocalLLM processing completed successfully!")
                logger.info(f"Processing Method: {result.get('processing_method', 'Unknown')}")
                logger.info(f"Model Info: {result.get('model_info', {})}")
                logger.info(f"Summary Length: {len(result.get('summary', ''))}")
                logger.info(f"LLM Error Detected: {result.get('llm_error_detected', True)}")
                
                # 要約の一部を表示
                summary = result.get('summary', '')
                if summary:
                    logger.info(f"Summary Preview (first 200 chars): {summary[:200]}...")
                
                break
        else:
            logger.warning("No test files found. Creating a test file...")
            
            # テストデータの作成
            test_data = [
                {
                    "title": "Test FPGA Document",
                    "abstract": "This is a test abstract about FPGA technology for Real LocalLLM testing.",
                    "content": "Test content about Field Programmable Gate Arrays and their applications."
                }
            ]
            
            import json
            test_file = "test_localllm_data.json"
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Created test file: {test_file}")
            
            # テストファイルで処理
            result = summarizer.summarize_results(test_file)
            logger.info("✅ Real LocalLLM test processing completed!")
            logger.info(f"Result: {result}")
            
    except Exception as e:
        logger.error(f"❌ Real LocalLLM Test Failed: {e}")
        logger.error("This error indicates that Real LocalLLM is not properly configured.")
        logger.error("Please ensure:")
        logger.error("1. LocalLLM library is properly installed")
        logger.error("2. llama-cpp-python is installed")
        logger.error("3. A GGUF model file is available in models/ directory")
        raise

if __name__ == "__main__":
    test_real_localllm()
