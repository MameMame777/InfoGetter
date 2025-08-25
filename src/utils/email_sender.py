import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import sys
import yaml
import textwrap

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.models.document import Document
from src.utils.markdown_generator import MarkdownReportGenerator


class EmailSender:
    """メール送信クラス"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.markdown_generator = MarkdownReportGenerator()  # Markdown生成器を追加
        
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
                         json_file_path: str = None, llm_summary: Dict = None) -> bool:
        """スクレイピング結果をメールで送信（Markdownレポート添付）"""
        try:
            # メール内容を作成
            subject = f"FPGA IP Document Scan Results with Real Llama - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            body = self._create_email_body(results, llm_summary)
            
            # Markdownレポートを生成
            markdown_attachment = None
            if json_file_path and os.path.exists(json_file_path):
                try:
                    self.logger.info("📝 Generating Markdown report for email attachment...")
                    
                    # 個別要約ファイルのパス
                    individual_summaries_file = "results/individual_summaries.json"
                    
                    # Markdownレポートを生成
                    markdown_attachment = self.markdown_generator.generate_summary_report(
                        json_file_path, 
                        individual_summaries_file if os.path.exists(individual_summaries_file) else None
                    )
                    
                    self.logger.info(f"✅ Markdown report generated: {markdown_attachment}")
                    
                except Exception as md_e:
                    self.logger.warning(f"⚠️ Failed to generate Markdown report: {md_e}")
                    markdown_attachment = None
            
            # メールを送信（Markdownレポートを添付）
            self._send_email(subject, body, markdown_attachment)
            self.logger.info(f"Email sent successfully to {len(self.recipients)} recipients")
            
            if markdown_attachment:
                self.logger.info(f"📎 Attached Markdown report: {os.path.basename(markdown_attachment)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def _create_email_body(self, results: Dict[str, List[Document]], llm_summary: Dict = None) -> str:
        """メール本文を作成（Real Llama要約対応）"""
        body = "🤖 FPGA IP Document Scan Results with Real Llama AI Summary\n"
        body += "=" * 70 + "\n\n"
        
        # Real Llama要約があれば追加（優先表示）
        if llm_summary and llm_summary.get('processing_status') == 'Success':
            body += "🎯 Real Llama AI要約レポート\n"
            body += "-" * 50 + "\n"
            
            # 要約の基本情報
            summary_info = llm_summary.get('summary_info', {})
            if summary_info:
                body += f"📅 生成日時: {summary_info.get('timestamp', '不明')}\n"
                body += f"🌐 言語: {summary_info.get('language', '不明')}\n"
                body += f"🤖 処理方式: {summary_info.get('processing_method', '不明')}\n"
                body += f"📊 元文書数: {summary_info.get('original_document_count', 0)}件\n"
                body += f"🔍 対象ソース: {', '.join(summary_info.get('original_sources', []))}\n"
                
                # モデル情報
                model_info = summary_info.get('model_info', {})
                if model_info:
                    body += f"🧠 LLMモデル: {model_info.get('model_name', 'unknown')}\n"
                    body += f"⚡ バックエンド: {model_info.get('backend', 'unknown')}\n"
                    body += f"⏱️ 処理時間: {model_info.get('processing_time', 0):.1f}秒\n"
                    body += f"📏 生成トークン数: {model_info.get('tokens_generated', 0)}\n"
                body += "\n"
            
            # Real Llama生成要約本文
            ai_summary = llm_summary.get('summary', '')
            if ai_summary:
                body += "📄 Real Llama要約内容:\n"
                body += "-" * 30 + "\n"
                body += ai_summary + "\n\n"
            
            # 個別論文要約があれば追加
            individual_summaries_file = "results/individual_summaries.json"
            if os.path.exists(individual_summaries_file):
                try:
                    with open(individual_summaries_file, 'r', encoding='utf-8') as f:
                        individual_data = json.load(f)
                    
                    if 'individual_summaries' in individual_data:
                        summaries = individual_data['individual_summaries']
                        body += "📚 個別論文日本語要約 (Real Llama生成)\n"
                        body += "=" * 50 + "\n\n"
                        
                        for i, summary in enumerate(summaries[:5]):  # 最初の5件のみ表示
                            body += f"📝 論文 {summary.get('paper_index', i+1)}: \n"
                            title = summary.get('title', 'タイトル不明')
                            if len(title) > 60:
                                title = title[:60] + "..."
                            body += f"タイトル: {title}\n"
                            body += f"カテゴリ: {summary.get('category', '不明')}\n"
                            body += f"処理時間: {summary.get('processing_time', 0):.1f}秒\n"
                            body += f"要約文字数: {summary.get('summary_length', 0)}文字\n"
                            body += "-" * 40 + "\n"
                            
                            japanese_summary = summary.get('japanese_summary', '')
                            if len(japanese_summary) > 300:
                                japanese_summary = japanese_summary[:300] + "..."
                            body += japanese_summary + "\n"
                            body += "-" * 40 + "\n\n"
                        
                        if len(summaries) > 5:
                            body += f"※ 全{len(summaries)}件中、最初の5件を表示\n"
                            body += "完全版は添付のJSONファイルをご確認ください。\n\n"
                
                except Exception as e:
                    self.logger.warning(f"Failed to load individual summaries: {e}")
            
            body += "=" * 70 + "\n\n"
        
        elif llm_summary and llm_summary.get('processing_status') == 'Failed':
            body += "⚠️ Real Llama要約生成に失敗しました\n"
            error_msg = llm_summary.get('summary_info', {}).get('error', '不明なエラー')
            body += f"エラー: {error_msg}\n\n"
            body += "=" * 70 + "\n\n"
        
        # 従来の要約情報を追加
        body += "📊 スキャン結果詳細\n"
        body += "=" * 40 + "\n\n"
        
        total_documents = 0
        
        for source_name, documents in results.items():
            body += f"📋 Source: {source_name.upper()}\n"
            body += "-" * 30 + "\n"
            
            if not documents:
                body += "No documents found.\n\n"
                continue
            
            total_documents += len(documents)
            body += f"📄 Found {len(documents)} documents:\n\n"
            
            for i, doc in enumerate(documents, 1):
                body += f"【{i}】 {doc.name}\n"
                body += f"    🔗 URL: {doc.url}\n"
                if doc.category:
                    body += f"    📂 Category: {doc.category}\n"
                if doc.fpga_series:
                    body += f"    🔧 FPGA Series: {doc.fpga_series}\n"
                if doc.file_type:
                    body += f"    📎 File Type: {doc.file_type}\n"
                if hasattr(doc, 'source_type'):
                    body += f"    📡 Source Type: {doc.source_type}\n"
                if doc.abstract:
                    # アブストラクトを適切に整形して表示
                    abstract_lines = doc.abstract.replace('\n', ' ').strip()
                    if len(abstract_lines) > 300:
                        abstract_preview = abstract_lines[:300] + "..."
                    else:
                        abstract_preview = abstract_lines
                    body += f"    📝 Abstract:\n"
                    # 75文字で改行してインデント
                    wrapped_abstract = textwrap.fill(abstract_preview, width=75, 
                                                   initial_indent="        ", 
                                                   subsequent_indent="        ")
                    body += wrapped_abstract + "\n"
                body += "\n"
            
            body += f"📊 {source_name.upper()} Summary: {len(documents)} documents\n\n"
        
        body += f"Total Documents Found: {total_documents}\n"
        body += f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return body
    
    def _send_email(self, subject: str, body: str, attachment_path: Optional[str] = None):
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
