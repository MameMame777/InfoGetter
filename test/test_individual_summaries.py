"""
Individual Paper Summarization Test
===================================
"""

from src.utils.real_llama_summarizer import RealLlamaSummarizer
import json

def test_individual_summaries():
    print("🤖 Testing Real Llama individual paper summarization...")
    
    # Initialize Real Llama
    summarizer = RealLlamaSummarizer()
    
    # Process individual papers
    print("📝 Generating individual Japanese summaries...")
    result = summarizer.summarize_individual_papers('results/fpga_documents.json')
    
    print(f"✅ Processing completed!")
    print(f"📊 Total papers processed: {result['total_papers']}")
    print(f"⏱️ Total processing time: {result['total_processing_time']:.2f} seconds")
    print(f"📈 Average time per paper: {result['average_processing_time']:.2f} seconds")
    
    # Save individual summaries
    with open('results/individual_summaries.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n📄 Individual summaries:")
    print("=" * 80)
    
    for i, summary in enumerate(result['individual_summaries'][:3]):  # Show first 3
        print(f"\n📝 論文 {summary['paper_index']}: {summary['title'][:60]}...")
        print(f"📏 要約文字数: {summary['summary_length']} 文字")
        print(f"⏱️ 処理時間: {summary['processing_time']:.2f} 秒")
        print("=" * 40)
        print(summary['japanese_summary'])
        print("=" * 40)
    
    print(f"\n💾 All summaries saved to: results/individual_summaries.json")

if __name__ == "__main__":
    test_individual_summaries()
