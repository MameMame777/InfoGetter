#!/usr/bin/env python3
"""
Selenium専用統合スクレイパーのテストスクリプト
"""

import os
import sys
import json
from datetime import datetime

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import InfoGatherer
from utils.log_manager import clear_log_file


def test_selenium_only_scrapers():
    """Selenium専用スクレイパーの統合テスト"""
    print("=" * 80)
    print("Selenium専用FPGAスクレイパーの統合テスト")
    print("=" * 80)
    
    # ログファイルを初期化
    print("🗂️ ログファイルを初期化中...")
    clear_log_file()
    
    try:
        # InfoGathererを初期化
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        gatherer = InfoGatherer(config_path)
        
        # 両方のスクレイパーを実行
        print("\n🔍 両方のSeleniumスクレイパーでスクレイピングを開始...")
        print("⏳ ブラウザの起動とページ読み込みを待機中...")
        
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
                
                # 期待されるドキュメントの確認
                expected_docs = {
                    'xilinx': ['system generator', 'fir compiler', 'fft', 'dsp', 'versal', 'zynq'],
                    'altera': ['dsp builder', 'nios', 'stratix', 'variable precision', 'floating point']
                }
                
                source_expected = expected_docs.get(source, [])
                found_expected = {}
                for expected in source_expected:
                    count = sum(1 for doc in documents if expected.lower() in doc.name.lower())
                    found_expected[expected] = count
                
                print(f"  期待されるドキュメント:")
                total_expected = 0
                for doc_type, count in found_expected.items():
                    status = "✅" if count > 0 else "❌"
                    total_expected += count
                    print(f"    {status} {doc_type}: {count} 件")
                
                print(f"  期待されるドキュメント総数: {total_expected} 件")
                
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
        
        # 品質評価
        quality_score = 0
        max_score = 100
        
        # ドキュメント数での評価 (40点満点)
        if total_documents >= 50:
            quality_score += 40
        elif total_documents >= 30:
            quality_score += 30
        elif total_documents >= 10:
            quality_score += 20
        
        # 重複率での評価 (30点満点)
        if total_documents > 0:
            duplicate_rate = (total_documents - len(total_unique_urls)) / total_documents
            if duplicate_rate <= 0.1:  # 10%以下
                quality_score += 30
            elif duplicate_rate <= 0.2:  # 20%以下
                quality_score += 20
            elif duplicate_rate <= 0.3:  # 30%以下
                quality_score += 10
        
        # 期待されるドキュメントの発見率 (30点満点)
        expected_found = 0
        total_expected = 0
        for source, documents in results.items():
            if documents:
                expected_docs = {
                    'xilinx': ['system generator', 'fir compiler', 'fft', 'dsp'],
                    'altera': ['dsp builder', 'nios', 'stratix', 'variable precision']
                }
                source_expected = expected_docs.get(source, [])
                for expected in source_expected:
                    total_expected += 1
                    if any(expected.lower() in doc.name.lower() for doc in documents):
                        expected_found += 1
        
        if total_expected > 0:
            expected_rate = expected_found / total_expected
            quality_score += int(expected_rate * 30)
        
        print(f"\n📈 スクレイピング品質スコア: {quality_score}/{max_score} 点")
        
        if quality_score >= 80:
            print("🎉 優秀: 高品質なスクレイピングが実現されています")
        elif quality_score >= 60:
            print("👍 良好: 良質なスクレイピングが実現されています")
        elif quality_score >= 40:
            print("⚠️  普通: スクレイピング品質に改善の余地があります")
        else:
            print("❌ 要改善: スクレイピング品質が低いです")
        
        # 結果をJSONファイルに保存
        results_file = os.path.join(project_root, 'results', 'selenium_integrated_test_results.json')
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        # 結果をシリアライズ可能な形式に変換
        serializable_results = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': total_documents,
            'total_unique_urls': len(total_unique_urls),
            'quality_score': quality_score,
            'expected_found': expected_found,
            'total_expected': total_expected,
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
    success = test_selenium_only_scrapers()
    
    if success:
        print("\n🎉 Selenium専用統合テスト完了！")
    else:
        print("\n💥 テスト失敗")
        sys.exit(1)