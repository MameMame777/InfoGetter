#!/usr/bin/env python3
"""
ログファイル管理コマンドラインツール
"""

import os
import sys
import argparse
from datetime import datetime

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from utils.log_manager import clear_log_file, get_log_size, rotate_log_if_large


def main():
    """コマンドライン引数を解析してログ管理を実行"""
    parser = argparse.ArgumentParser(description='ログファイル管理ツール')
    parser.add_argument('--clear', action='store_true', help='ログファイルをクリア')
    parser.add_argument('--size', action='store_true', help='ログファイルサイズを表示')
    parser.add_argument('--rotate', action='store_true', help='大きなログファイルをローテーション')
    parser.add_argument('--max-size', type=float, default=10.0, help='ローテーション閾値 (MB)')
    parser.add_argument('--log-path', type=str, help='ログファイルパス（デフォルト: logs/scraper.log）')
    
    args = parser.parse_args()
    
    # デフォルトのログパスを設定
    if args.log_path:
        log_path = args.log_path
    else:
        log_path = os.path.join(project_root, 'logs', 'scraper.log')
    
    print(f"📁 ログファイル: {log_path}")
    
    if args.size or (not args.clear and not args.rotate):
        # サイズを表示（デフォルト動作）
        size_bytes, size_mb = get_log_size(log_path)
        if size_bytes > 0:
            print(f"📏 ログファイルサイズ: {size_bytes:,} bytes ({size_mb:.2f} MB)")
            
            # ファイルの最終更新時刻を表示
            if os.path.exists(log_path):
                mtime = os.path.getmtime(log_path)
                last_modified = datetime.fromtimestamp(mtime)
                print(f"🕒 最終更新: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("📝 ログファイルは存在しないか空です")
    
    if args.clear:
        print("🗂️ ログファイルをクリア中...")
        if clear_log_file(log_path):
            print("✅ ログファイルがクリアされました")
        else:
            print("❌ ログファイルのクリアに失敗しました")
    
    if args.rotate:
        print(f"🔄 ログローテーションをチェック中（閾値: {args.max_size} MB）...")
        if rotate_log_if_large(log_path, args.max_size):
            print("✅ ログファイルがローテーションされました")
        else:
            size_bytes, size_mb = get_log_size(log_path)
            print(f"ℹ️ ローテーション不要（現在: {size_mb:.2f} MB < {args.max_size} MB）")


if __name__ == "__main__":
    main()