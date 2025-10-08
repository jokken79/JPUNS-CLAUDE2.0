"""
Notification Service for UNS-ClaudeJP 2.0
Handles Email, LINE, and WhatsApp notifications
"""
import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Centralized notification service"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
        self.line_channel_token = settings.LINE_CHANNEL_ACCESS_TOKEN
    
    def send_email(
        self, 
        to: str, 
        subject: str, 
        body: str, 
        attachments: Optional[List[str]] = None,
        is_html: bool = True
    ) -> bool:
        """
        Send email via SMTP
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (HTML or plain text)
            attachments: List of file paths to attach
            is_html: Whether body is HTML
            
        Returns:
            bool: True if sent successfully
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from
            msg['To'] = to
            msg['Subject'] = subject
            
            # Attach body
            body_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, body_type, 'utf-8'))
            
            # Attach files if any
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={Path(file_path).name}'
                            )
                            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False
    
    def send_line_notification(self, user_id: str, message: str) -> bool:
        """
        Send LINE notification
        
        Args:
            user_id: LINE user ID
            message: Message text
            
        Returns:
            bool: True if sent successfully
        """
        if not self.line_channel_token or self.line_channel_token == 'YOUR_LINE_TOKEN':
            logger.warning("LINE token not configured")
            return False
        
        try:
            url = "https://api.line.me/v2/bot/message/push"
            headers = {
                "Authorization": f"Bearer {self.line_channel_token}",
                "Content-Type": "application/json"
            }
            data = {
                "to": user_id,
                "messages": [{"type": "text", "text": message}]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"LINE notification sent to {user_id}")
                return True
            else:
                logger.error(f"LINE API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send LINE notification: {e}")
            return False
    
    def notify_yukyu_approval(
        self, 
        employee_email: str, 
        employee_name: str, 
        status: str,
        yukyu_date: str,
        line_user_id: Optional[str] = None
    ) -> bool:
        """
        Notify employee about yukyu (paid leave) approval
        
        Args:
            employee_email: Employee email
            employee_name: Employee name
            status: Approval status (承認/却下)
            yukyu_date: Date of yukyu
            line_user_id: Optional LINE user ID
            
        Returns:
            bool: True if at least one notification sent
        """
        subject = f"有給申請が{status}されました"
        
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2 style="color: #1D4ED8;">有給申請の通知</h2>
            <p>{employee_name}さん、</p>
            <p>あなたの有給申請が<strong>{status}</strong>されました。</p>
            <div style="background: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>申請日:</strong> {yukyu_date}</p>
                <p><strong>ステータス:</strong> {status}</p>
            </div>
            <p>ご確認ください。</p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #E5E7EB;">
            <p style="color: #6B7280; font-size: 12px;">
                このメールは自動送信されています。<br>
                UNS-Kikaku Personnel System
            </p>
        </body>
        </html>
        """
        
        email_sent = self.send_email(employee_email, subject, body)
        
        # Also send LINE notification if available
        line_sent = False
        if line_user_id:
            line_message = f"{employee_name}さん\n有給申請が{status}されました。\n日付: {yukyu_date}"
            line_sent = self.send_line_notification(line_user_id, line_message)
        
        return email_sent or line_sent
    
    def notify_taisha_approval(
        self,
        employee_email: str,
        employee_name: str,
        status: str,
        taisha_date: str,
        line_user_id: Optional[str] = None
    ) -> bool:
        """Notify employee about taisha (resignation) approval"""
        subject = f"退社報告が{status}されました"
        
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2 style="color: #1D4ED8;">退社報告の通知</h2>
            <p>{employee_name}さん、</p>
            <p>あなたの退社報告が<strong>{status}</strong>されました。</p>
            <div style="background: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>退社予定日:</strong> {taisha_date}</p>
                <p><strong>ステータス:</strong> {status}</p>
            </div>
            <p>ご確認ください。</p>
        </body>
        </html>
        """
        
        email_sent = self.send_email(employee_email, subject, body)
        
        if line_user_id:
            line_message = f"{employee_name}さん\n退社報告が{status}されました。\n退社予定日: {taisha_date}"
            self.send_line_notification(line_user_id, line_message)
        
        return email_sent
    
    def notify_payslip_ready(
        self,
        employee_email: str,
        employee_name: str,
        year: int,
        month: int,
        payslip_path: Optional[str] = None,
        line_user_id: Optional[str] = None
    ) -> bool:
        """Notify employee that payslip is ready"""
        subject = f"{year}年{month}月の給与明細書"
        
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2 style="color: #1D4ED8;">給与明細書のお知らせ</h2>
            <p>{employee_name}さん、</p>
            <p>{year}年{month}月の給与明細書が発行されました。</p>
            <p>システムにログインしてご確認ください。</p>
            <a href="{settings.FRONTEND_URL}/payroll" 
               style="display: inline-block; background: #1D4ED8; color: white; 
                      padding: 12px 24px; text-decoration: none; border-radius: 8px; margin: 20px 0;">
                給与明細書を確認
            </a>
        </body>
        </html>
        """
        
        attachments = [payslip_path] if payslip_path else None
        email_sent = self.send_email(employee_email, subject, body, attachments)
        
        if line_user_id:
            line_message = f"{employee_name}さん\n{year}年{month}月の給与明細書が発行されました。"
            self.send_line_notification(line_user_id, line_message)
        
        return email_sent
    
    def notify_admin_new_request(
        self,
        admin_email: str,
        request_type: str,
        employee_name: str,
        request_details: str
    ) -> bool:
        """Notify admin about new employee request"""
        subject = f"新しい{request_type}申請"
        
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2 style="color: #DC2626;">新しい申請があります</h2>
            <p>管理者様、</p>
            <p><strong>{employee_name}</strong>さんから新しい{request_type}申請がありました。</p>
            <div style="background: #FEF2F2; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>申請内容:</strong></p>
                <p>{request_details}</p>
            </div>
            <a href="{settings.FRONTEND_URL}/admin/requests" 
               style="display: inline-block; background: #DC2626; color: white; 
                      padding: 12px 24px; text-decoration: none; border-radius: 8px;">
                申請を確認
            </a>
        </body>
        </html>
        """
        
        return self.send_email(admin_email, subject, body)


# Global instance
notification_service = NotificationService()
