#!/usr/bin/env python3
"""
FPGAドキュメント収集システム - メイン実行スクリプト
"""

import os
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import InfoGatherer
from utils.log_manager import clear_log_file, get_log_size


def main():
    """メイン関数"""
    print("🚀 FPGAドキュメント収集システムを開始します...")
    
    # ログファイルを初期化
    print("🗂️ ログファイルを初期化中...")
    clear_log_file()
    
    try:
        # 設定ファイルパスを指定
        config_path = os.path.join(project_root, 'config', 'settings.yaml')
        
        # InfoGathererを初期化（内部でも_clear_log_file()が呼ばれます）
        gatherer = InfoGatherer(config_path)
        
        # スクレイピングを実行
        print("📡 スクレイピングを開始します...")
        results = gatherer.run_scraping()
        
        # 結果を表示
        total_documents = sum(len(docs) for docs in results.values())
        print(f"\n✅ スクレイピング完了!")
        print(f"📊 総取得ドキュメント数: {total_documents}")
        
        for source, documents in results.items():
            print(f"  {source}: {len(documents)} 件")
        
        # ログファイルサイズを表示
        log_bytes, log_mb = get_log_size()
        print(f"📝 ログファイルサイズ: {log_mb:.2f} MB")
        
        print("🎉 処理が正常に完了しました!")
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1)