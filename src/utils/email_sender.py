import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
from typing import List, Dict, Any
import json
from datetime import datetime
import sys
import yaml

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.models.document import Document


class EmailSender:
    """メール送信クラス"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 設定の取得
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)

        # credentialsを外部ファイルから読み込む
        credentials_file = config.get('credentials_file')
        if credentials_file:
            with open(credentials_file, 'r') as file:
                credentials = yaml.safe_load(file).get('email', {})
                self.sender_email = credentials.get('sender')
                self.sender_password = credentials.get('password')
        else:
            self.sender_email = config.get('sender_email')
            self.sender_password = config.get('sender_password')
        
        # recipientsを外部ファイルから読み込む
        recipients_file = config.get('recipients_file')
        if recipients_file:
            try:
                with open(recipients_file, 'r') as file:
                    self.recipients = yaml.safe_load(file).get('recipients', [])
            except Exception as e:
                self.logger.error(f"Failed to load recipients file: {e}")
                self.recipients = []
        else:
            self.recipients = config.get('recipients', [])
        
    def send_notification(self, results: Dict[str, List[Document]], 
                         json_file_path: str = None) -> bool:
        """スクレイピング結果をメールで送信"""
        try:
            # メール内容を作成
            subject = f"FPGA IP Document Scan Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            body = self._create_email_body(results)
            
            # メールを送信
            self._send_email(subject, body, json_file_path)
            self.logger.info(f"Email sent successfully to {len(self.recipients)} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def _create_email_body(self, results: Dict[str, List[Document]]) -> str:
        """メール本文を作成"""
        body = "FPGA IP Document Scan Results\n"
        body += "=" * 50 + "\n\n"
        
        total_documents = 0
        
        for source_name, documents in results.items():
            body += f"Source: {source_name.upper()}\n"
            body += "-" * 30 + "\n"
            
            if not documents:
                body += "No documents found.\n\n"
                continue
            
            total_documents += len(documents)
            
            for doc in documents:
                body += f"• {doc.name}\n"
                body += f"  URL: {doc.url}\n"
                if doc.category:
                    body += f"  Category: {doc.category}\n"
                if doc.fpga_series:
                    body += f"  FPGA Series: {doc.fpga_series}\n"
                if doc.file_type:
                    body += f"  File Type: {doc.file_type}\n"
                if doc.abstract:
                    # アブストラクトが長い場合は短縮
                    abstract_preview = doc.abstract[:200] + "..." if len(doc.abstract) > 200 else doc.abstract
                    body += f"  Abstract: {abstract_preview}\n"
                body += "\n"
        
        body += f"Total Documents Found: {total_documents}\n"
        body += f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return body
    
    def _send_email(self, subject: str, body: str, attachment_path: str = None):
        """メールを送信"""
        if not self.sender_email or not self.sender_password:
            raise ValueError("Email credentials not configured")
        
        if not self.recipients:
            raise ValueError("No recipients configured")
        
        # メッセージを作成
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = subject
        
        # 本文を追加
        msg.attach(MIMEText(body, 'plain'))
        
        # 添付ファイルがある場合は追加
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
        
        # SMTPサーバーに接続してメール送信
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        
        for recipient in self.recipients:
            server.sendmail(self.sender_email, recipient, msg.as_string())
        
        server.quit()
    
    def test_connection(self) -> bool:
        """SMTP接続をテスト"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.quit()
            self.logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            return False
