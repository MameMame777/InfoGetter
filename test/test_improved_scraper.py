#!/usr/bin/env python3
"""
改善されたXilinxスクレイパーのテストスクリプト
"""

import os
import sys
import json
from datetime import datetime

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import InfoGatherer


def test_improved_xilinx_scraper():
    """改善されたXilinxスクレイパーをテスト"""
    print("=" * 60)
    print("改善されたXilinxスクレイパーのテスト")
    print("=" * 60)
    
    try:
        # InfoGathererを初期化
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        gatherer = InfoGatherer(config_path)
        
        # Xilinxスクレイピング実行
        print("\n🔍 Xilinxスクレイピングを開始...")
        results = gatherer.run_scraping(sources=['xilinx'])
        
        # 結果を分析
        xilinx_results = results.get('xilinx', [])
        print(f"\n📊 結果分析:")
        print(f"  取得ドキュメント数: {len(xilinx_results)}")
        
        if xilinx_results:
            # 重複チェック
            urls = [doc.url for doc in xilinx_results]
            unique_urls = set(urls)
            duplicate_count = len(urls) - len(unique_urls)
            
            print(f"  ユニークURL数: {len(unique_urls)}")
            print(f"  重複数: {duplicate_count}")
            print(f"  重複率: {duplicate_count / len(urls) * 100:.1f}%")
            
            # カテゴリ別集計
            categories = {}
            fpga_series = {}
            
            for doc in xilinx_results:
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
            if xilinx_results:
                search_url = xilinx_results[0].search_url
                print(f"\n🔗 使用された検索URL:")
                print(f"  {search_url}")
                
                # DSPクエリが含まれているか確認
                if 'query=DSP' in search_url:
                    print("  ✅ DSPクエリが正しく設定されています")
                else:
                    print("  ❌ DSPクエリが設定されていません")
            
            # サンプルドキュメントの表示
            print(f"\n📝 サンプルドキュメント (最初の3件):")
            for i, doc in enumerate(xilinx_results[:3]):
                print(f"  {i+1}. {doc.name}")
                print(f"     URL: {doc.url}")
                print(f"     カテゴリ: {doc.category}")
                print(f"     FPGAシリーズ: {doc.fpga_series}")
                print(f"     ファイルタイプ: {doc.file_type}")
                print()
        
        # 結果をJSONファイルに保存
        results_file = os.path.join(project_root, 'results', 'test_improved_results.json')
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        # 結果をシリアライズ可能な形式に変換
        serializable_results = {
            'timestamp': datetime.now().isoformat(),
            'xilinx': [
                {
                    'name': doc.name,
                    'url': str(doc.url),
                    'category': doc.category,
                    'fpga_series': doc.fpga_series,
                    'file_type': doc.file_type,
                    'search_url': str(doc.search_url) if doc.search_url else None
                }
                for doc in xilinx_results
            ]
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 結果をファイルに保存しました: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_improved_xilinx_scraper()
    
    if success:
        print("\n🎉 テスト完了！")
    else:
        print("\n💥 テスト失敗")
        sys.exit(1)