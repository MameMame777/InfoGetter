#!/usr/bin/env python3
"""
ログファイル管理ユーティリティ
"""

import os
from datetime import datetime


def clear_log_file(log_path: str = None):
    """ログファイルを初期化（既存のログを削除）"""
    if log_path is None:
        # デフォルトのログファイルパス
        project_root = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(project_root, 'logs', 'scraper.log')
    
    try:
        # ログディレクトリが存在しない場合は作成
        log_dir = os.path.dirname(log_path)
        os.makedirs(log_dir, exist_ok=True)
        
        # 既存のログファイルをバックアップ（オプション）
        if os.path.exists(log_path):
            backup_path = f"{log_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(log_path, backup_path)
            print(f"Previous log backed up to: {backup_path}")
        
        # 新しい空のログファイルを作成
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"# Log initialized at {datetime.now().isoformat()}\n")
        
        print(f"Log file cleared: {log_path}")
        return True
        
    except Exception as e:
        print(f"Warning: Could not clear log file: {e}")
        return False


def get_log_size(log_path: str = None):
    """ログファイルのサイズを取得"""
    if log_path is None:
        project_root = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(project_root, 'logs', 'scraper.log')
    
    try:
        if os.path.exists(log_path):
            size_bytes = os.path.getsize(log_path)
            size_mb = size_bytes / (1024 * 1024)
            return size_bytes, size_mb
        else:
            return 0, 0.0
    except Exception:
        return 0, 0.0


def rotate_log_if_large(log_path: str = None, max_size_mb: float = 10.0):
    """ログファイルが大きくなった場合にローテーション"""
    if log_path is None:
        project_root = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(project_root, 'logs', 'scraper.log')
    
    try:
        size_bytes, size_mb = get_log_size(log_path)
        
        if size_mb > max_size_mb:
            # ローテーション実行
            rotated_path = f"{log_path}.rotated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(log_path, rotated_path)
            
            # 新しいログファイルを作成
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"# Log rotated at {datetime.now().isoformat()}\n")
                f.write(f"# Previous log moved to: {rotated_path}\n")
            
            print(f"Log rotated: {size_mb:.2f}MB -> {rotated_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Warning: Could not rotate log file: {e}")
        return False


if __name__ == "__main__":
    # ログファイルの状態を確認
    project_root = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(project_root, 'logs', 'scraper.log')
    
    size_bytes, size_mb = get_log_size(log_path)
    print(f"Current log size: {size_bytes} bytes ({size_mb:.2f} MB)")
    
    # ログファイルをクリア
    clear_log_file(log_path)