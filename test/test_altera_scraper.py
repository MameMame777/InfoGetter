#!/usr/bin/env python3
"""
改善されたAlteraスクレイパーのテストスクリプト
"""

import os
import sys
import yaml
import json
from datetime import datetime

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.scrapers.altera_scraper import AlteraScraper


def test_altera_scraper():
    """改善されたAlteraスクレイパーをテスト"""
    print("=" * 60)
    print("改善されたAlteraスクレイパーのテスト")
    print("=" * 60)
    
    try:
        # 設定ファイルを読み込み
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        altera_config = config['data_sources']['altera']
        
        # スクレイパーを初期化
        scraper = AlteraScraper(altera_config)
        
        # URL構築をテスト
        search_url = scraper._build_search_url()
        print(f"🔗 構築されたURL: {search_url}")
        
        # 設定値を確認
        print(f"📊 設定値:")
        print(f"  max_results: {altera_config.get('max_results', 100)}")
        print(f"  scroll_pages: {altera_config.get('scroll_pages', 5)}")
        print(f"  query: {altera_config.get('search_params', {}).get('query', 'Unknown')}")
        
        # URLパラメータをチェック
        if 'q=DSP' in search_url:
            print("  ✅ DSPクエリが正しく設定されています")
        else:
            print("  ❌ DSPクエリが設定されていません")
            
        if 's=Relevancy' in search_url:
            print("  ✅ ソート設定が正しく設定されています")
        else:
            print("  ❌ ソート設定が設定されていません")
        
        # スクレイピング実行
        print("\n🚀 スクレイピング開始...")
        documents = scraper.scrape_documents()
        
        print(f"✅ 取得完了: {len(documents)} 件")
        
        if documents:
            # 重複チェック
            urls = [doc.url for doc in documents]
            unique_urls = set(urls)
            duplicate_count = len(urls) - len(unique_urls)
            
            print(f"📈 重複分析:")
            print(f"  総件数: {len(urls)}")
            print(f"  ユニーク: {len(unique_urls)}")
            print(f"  重複: {duplicate_count}")
            
            if duplicate_count > 0:
                print(f"  重複率: {duplicate_count / len(urls) * 100:.1f}%")
            else:
                print("  重複率: 0% (完璧！)")
            
            # 期待されるドキュメントタイプの確認
            expected_docs = [
                'dsp builder',
                'nios',
                'stratix',
                'user guide',
                'handbook',
                'reference manual',
                'ip core'
            ]
            
            found_expected = {}
            for expected in expected_docs:
                count = sum(1 for doc in documents if expected.lower() in doc.name.lower())
                found_expected[expected] = count
            
            print(f"\n📋 期待されるドキュメントタイプ:")
            for doc_type, count in found_expected.items():
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {doc_type}: {count} 件")
            
            # DSP Builderが含まれているかチェック
            dsp_builder_docs = [doc for doc in documents if 'dsp builder' in doc.name.lower()]
            if dsp_builder_docs:
                print(f"\n🎯 DSP Builder関連ドキュメント: {len(dsp_builder_docs)} 件")
                for doc in dsp_builder_docs[:3]:
                    print(f"  - {doc.name}")
            
            # Nios関連ドキュメントのチェック
            nios_docs = [doc for doc in documents if 'nios' in doc.name.lower()]
            if nios_docs:
                print(f"\n🎯 Nios関連ドキュメント: {len(nios_docs)} 件")
                for doc in nios_docs[:3]:
                    print(f"  - {doc.name}")
            
            # カテゴリ別集計
            categories = {}
            fpga_series = {}
            
            for doc in documents:
                # カテゴリ別集計
                cat = doc.category or 'Unknown'
                categories[cat] = categories.get(cat, 0) + 1
                
                # FPGAシリーズ別集計
                series = doc.fpga_series or 'Unknown'
                fpga_series[series] = fpga_series.get(series, 0) + 1
            
            print(f"\n📈 カテゴリ別集計:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
            
            print(f"\n🔧 FPGAシリーズ別集計:")
            for series, count in sorted(fpga_series.items(), key=lambda x: x[1], reverse=True):
                print(f"  {series}: {count}")
            
            # 検索URLの確認
            search_url_from_doc = documents[0].search_url
            print(f"\n🔗 実際に使用された検索URL:")
            print(f"  {search_url_from_doc}")
            
            # 最初の10件を表示
            print(f"\n📝 サンプル結果 (最初の10件):")
            for i, doc in enumerate(documents[:10]):
                print(f"  {i+1}. {doc.name}")
                print(f"     URL: {doc.url}")
                print(f"     カテゴリ: {doc.category}")
                print(f"     FPGAシリーズ: {doc.fpga_series}")
                print()
            
            # 結果をJSONファイルに保存
            results_file = os.path.join(project_root, 'results', 'altera_test_results.json')
            os.makedirs(os.path.dirname(results_file), exist_ok=True)
            
            # 結果をシリアライズ可能な形式に変換
            serializable_results = {
                'timestamp': datetime.now().isoformat(),
                'search_url': search_url,
                'total_documents': len(documents),
                'unique_documents': len(unique_urls),
                'duplicate_count': duplicate_count,
                'categories': categories,
                'fpga_series': fpga_series,
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
            
            print(f"💾 結果をファイルに保存しました: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_altera_scraper()
    
    if success:
        print("\n🎉 Alteraスクレイパーテスト完了！")
    else:
        print("\n💥 テスト失敗")
        sys.exit(1)