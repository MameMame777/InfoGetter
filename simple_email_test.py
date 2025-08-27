#!/usr/bin/env python3
"""
Simple email test with minimal configuration
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

def test_simple_email():
    """Test simple email sending"""
    
    print("📧 Testing simple email sending...")
    
    try:
        # Load credentials
        with open('config/email_credentials.yaml', 'r') as f:
            credentials = yaml.safe_load(f)['email']
        
        with open('config/recipients.yaml', 'r') as f:
            recipients = yaml.safe_load(f)['recipients']
        
        sender_email = credentials['sender']
        sender_password = credentials['password']
        
        print(f"📤 Sender: {sender_email}")
        print(f"📥 Recipients: {recipients}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = "🧪 InfoGetter Email Test - Mistral Academic"
        
        body = """
🧪 これは InfoGetter システムのメール送信テストです

📊 システム情報:
- モデル: Mistral-7B-Instruct-v0.2
- 処理方式: Academic Summarization
- 送信時刻: {}

✅ このメールが届いていれば、メール送信機能は正常に動作しています。

📄 完全な要約レポートは実際のスクレイピング実行時に送信されます。

🔧 InfoGetter with Mistral Academic
        """.format("2025-08-26 08:42")
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print("🚀 Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        print("📨 Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, recipients, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print("📬 Please check your inbox at:", recipients[0])
        print("📧 Also check spam/junk folder if not in inbox")
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_email()
