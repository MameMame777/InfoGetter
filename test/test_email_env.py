#!/usr/bin/env python3
"""
環境変数からメールアドレスとパスワードを取得できているかテストするスクリプト
"""

import os
import sys

# プロジェクトのルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_environment_variables():
    """環境変数のテスト"""
    print("=== 環境変数の確認 ===")
    
    # 現在の環境変数を確認
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"EMAIL_SENDER: {email_sender if email_sender else '未設定'}")
    print(f"EMAIL_PASSWORD: {'***設定済み***' if email_password else '未設定'}")
    
    # 一時的に環境変数を設定
    os.environ['EMAIL_SENDER'] = 'saitakusaita@gmail.com'
    os.environ['EMAIL_PASSWORD'] = 'vaxr rtxp tvpt uqxo'
    
    print("\n=== 環境変数を一時設定後 ===")
    print(f"EMAIL_SENDER: {os.getenv('EMAIL_SENDER')}")
    print(f"EMAIL_PASSWORD: {'***設定済み***' if os.getenv('EMAIL_PASSWORD') else '未設定'}")
    
    return True

def test_email_sender_class():
    """EmailSenderクラスでの環境変数取得テスト"""
    print("\n=== EmailSenderクラスのテスト ===")
    
    try:
        from src.utils.email_sender import EmailSender
        
        # 設定ファイルの値を空にして環境変数から取得させる
        test_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': '',  # 空にして環境変数から取得
            'sender_password': '',  # 空にして環境変数から取得
            'recipients': ['takutakuwith@outlook.jp']
        }
        
        email_sender = EmailSender(test_config)
        
        print(f"設定ファイルから取得:")
        print(f"  sender_email: '{test_config.get('sender_email')}'")
        print(f"  sender_password: '{test_config.get('sender_password')}'")
        
        print(f"\nEmailSenderクラスで実際に使用される値:")
        print(f"  sender_email: {email_sender.sender_email}")
        print(f"  sender_password: {'***設定済み***' if email_sender.sender_password else '未設定'}")
        
        # 接続テストも実行
        print(f"\n=== SMTP接続テスト ===")
        connection_result = email_sender.test_connection()
        print(f"接続テスト結果: {'成功' if connection_result else '失敗'}")
        
        return True
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_config_values():
    """設定ファイルに値がある場合のテスト"""
    print("\n=== 設定ファイルに値がある場合のテスト ===")
    
    try:
        from src.utils.email_sender import EmailSender
        
        # 設定ファイルに値がある場合
        test_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'config_email@example.com',  # 設定ファイルに値あり
            'sender_password': 'config_password',  # 設定ファイルに値あり
            'recipients': ['takutakuwith@outlook.jp']
        }
        
        email_sender = EmailSender(test_config)
        
        print(f"設定ファイルの値:")
        print(f"  sender_email: {test_config.get('sender_email')}")
        print(f"  sender_password: {test_config.get('sender_password')}")
        
        print(f"\nEmailSenderクラスで実際に使用される値:")
        print(f"  sender_email: {email_sender.sender_email}")
        print(f"  sender_password: {'***設定済み***' if email_sender.sender_password else '未設定'}")
        
        return True
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    try:
        test_environment_variables()
        test_email_sender_class()
        test_with_config_values()
        print("\n=== テスト完了 ===")
    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
