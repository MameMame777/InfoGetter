#!/usr/bin/env python3
"""環境変数とメール認証情報のテスト"""

import os
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.email_sender import EmailSender

def test_environment_variables():
    """環境変数の確認"""
    print("=== 環境変数の確認 ===")
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"EMAIL_SENDER: {email_sender}")
    print(f"EMAIL_PASSWORD: {'*' * len(email_password) if email_password else 'None'}")
    print(f"EMAIL_PASSWORD length: {len(email_password) if email_password else 0}")
    
    if not email_sender:
        print("❌ EMAIL_SENDER環境変数が設定されていません")
    else:
        print("✅ EMAIL_SENDER環境変数が設定されています")
    
    if not email_password:
        print("❌ EMAIL_PASSWORD環境変数が設定されていません")
    else:
        print("✅ EMAIL_PASSWORD環境変数が設定されています")
        # アプリパスワードは通常16文字
        if len(email_password) == 16:
            print("✅ パスワードの長さがアプリパスワードの標準的な長さ（16文字）です")
        else:
            print(f"⚠️  パスワードの長さが{len(email_password)}文字です。Gmailアプリパスワードは通常16文字です。")

def test_email_sender_config():
    """EmailSenderの設定テスト"""
    print("\n=== EmailSenderの設定テスト ===")
    
    # 空の設定で初期化（環境変数から取得するため）
    config = {
        'recipients': ['test@example.com']  # テスト用
    }
    
    email_sender = EmailSender(config)
    
    print(f"sender_email: {email_sender.sender_email}")
    print(f"sender_password: {'*' * len(email_sender.sender_password) if email_sender.sender_password else 'None'}")
    print(f"smtp_server: {email_sender.smtp_server}")
    print(f"smtp_port: {email_sender.smtp_port}")
    
    # メールプロバイダーの検出
    if email_sender.sender_email:
        if '@gmail.com' in email_sender.sender_email.lower():
            print("📧 Gmail アカウントが検出されました")
        elif any(domain in email_sender.sender_email.lower() for domain in ['@outlook.com', '@hotmail.com', '@live.com']):
            print("📧 Outlook/Hotmail/Live アカウントが検出されました")
        else:
            print("📧 その他のメールプロバイダーです")
    
    if email_sender.sender_email and email_sender.sender_password:
        print("✅ メール認証情報が正しく設定されています")
        
        # SMTP接続テスト
        print("\n=== SMTP接続テスト ===")
        if email_sender.test_connection():
            print("✅ SMTP接続に成功しました")
        else:
            print("❌ SMTP接続に失敗しました")
    else:
        print("❌ メール認証情報が不完全です")

if __name__ == "__main__":
    test_environment_variables()
    test_email_sender_config()
