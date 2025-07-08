#!/usr/bin/env python3
"""
改善されたXilinxとAlteraスクレイパーの統合テストスクリプト
"""

import os
import sys
import json
from datetime import datetime

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import InfoGatherer


def test_improved_scrapers():
    """改善されたスクレイパーの統合テスト"""
    print("=" * 80)
    print("改善されたFPGAスクレイパーの統合テスト")
    print("=" * 80)
    
    try:
        # InfoGathererを初期化
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        gatherer = InfoGatherer(config_path)
        
        # 両方のスクレイパーを実行
        print("\n🔍 両方のスクレイパーでスクレイピングを開始...")
        results = gatherer.run_scraping(sources=['xilinx', 'altera'])
        
        print(f"\n📊 総合結果分析:")
        
        total_documents = 0
        total_unique_urls = set()
        
        for source, documents in results.items():
            print(f"\n🔧 {source.upper()} 結果:")
            print(f"  取得ドキュメント数: {len(documents)}")
            
            if documents:
                # 重複チェック
                urls = [doc.url for doc in documents]
                unique_urls = set(urls)
                duplicate_count = len(urls) - len(unique_urls)
                
                total_documents += len(documents)
                total_unique_urls.update(unique_urls)
                
                print(f"  ユニークURL数: {len(unique_urls)}")
                print(f"  重複数: {duplicate_count}")
                
                if duplicate_count > 0:
                    print(f"  重複率: {duplicate_count / len(urls) * 100:.1f}%")
                else:
                    print("  重複率: 0% (完璧！)")
                
                # カテゴリ別集計
                categories = {}
                fpga_series = {}
                
                for doc in documents:
                    cat = doc.category or 'Unknown'
                    categories[cat] = categories.get(cat, 0) + 1
                    
                    series = doc.fpga_series or 'Unknown'
                    fpga_series[series] = fpga_series.get(series, 0) + 1
                
                print(f"  主要カテゴリ: {dict(list(sorted(categories.items(), key=lambda x: x[1], reverse=True))[:3])}")
                print(f"  主要FPGAシリーズ: {dict(list(sorted(fpga_series.items(), key=lambda x: x[1], reverse=True))[:3])}")
                
                # 検索URLの確認
                search_url = documents[0].search_url
                print(f"  検索URL: {search_url}")
                
                # DSPクエリの確認
                if source == 'xilinx':
                    if 'query=DSP' in search_url:
                        print("  ✅ Xilinx DSPクエリが正しく設定されています")
                    else:
                        print("  ❌ Xilinx DSPクエリが設定されていません")
                elif source == 'altera':
                    if 'q=DSP' in search_url:
                        print("  ✅ Altera DSPクエリが正しく設定されています")
                    else:
                        print("  ❌ Altera DSPクエリが設定されていません")
        
        print(f"\n🎯 総合統計:")
        print(f"  総ドキュメント数: {total_documents}")
        print(f"  ユニークURL数: {len(total_unique_urls)}")
        print(f"  ソース間重複: {total_documents - len(total_unique_urls)}")
        
        # 結果をJSONファイルに保存
        results_file = os.path.join(project_root, 'results', 'integrated_test_results.json')
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        # 結果をシリアライズ可能な形式に変換
        serializable_results = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': total_documents,
            'total_unique_urls': len(total_unique_urls),
            'sources': {}
        }
        
        for source, documents in results.items():
            serializable_results['sources'][source] = {
                'document_count': len(documents),
                'search_url': documents[0].search_url if documents else None,
                'documents': [
                    {
                        'name': doc.name,
                        'url': str(doc.url),
                        'category': doc.category,
                        'fpga_series': doc.fpga_series,
                        'file_type': doc.file_type,
                        'search_url': str(doc.search_url) if doc.search_url else None
                    }
                    for doc in documents
                ]
            }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 統合結果をファイルに保存しました: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_improved_scrapers()
    
    if success:
        print("\n🎉 統合テスト完了！")
    else:
        print("\n💥 テスト失敗")
        sys.exit(1)