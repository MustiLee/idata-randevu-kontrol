import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class Notifier:
    """Handles notifications via Telegram and Email."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.telegram_enabled = config.get('telegram', {}).get('enabled', False)
        self.email_enabled = config.get('email', {}).get('enabled', False)
        
        if self.telegram_enabled:
            self.telegram_bot_token = config['telegram']['bot_token']
            self.telegram_chat_id = config['telegram'].get('chat_id', 0)
        
        if self.email_enabled:
            self.email_config = config['email']
    
    def send_notification(self, subject: str, message: str) -> bool:
        """
        Send notification via all enabled channels.
        
        Args:
            subject: Notification subject
            message: Notification message
            
        Returns:
            True if at least one notification was sent successfully
        """
        success = False
        
        if self.telegram_enabled:
            if self._send_telegram(subject, message):
                success = True
        
        if self.email_enabled:
            if self._send_email(subject, message):
                success = True
        
        return success
    
    def _send_telegram(self, subject: str, message: str) -> bool:
        """
        Send notification via Telegram.
        
        Args:
            subject: Notification subject
            message: Notification message
            
        Returns:
            True if sent successfully
        """
        try:
            # Format message with subject
            full_message = f"🔔 *{subject}*\n\n{message}"
            
            # Try to send to multiple users first
            try:
                from ..bot.bot_handler import send_message_to_all_users
                
                # Build database URL if available
                database_url = None
                if hasattr(self, 'config') and self.config.get('database', {}).get('enabled'):
                    db_config = self.config['database']
                    if db_config['url']:
                        database_url = db_config['url']
                    else:
                        database_url = (
                            f"postgresql://{db_config['user']}:{db_config['password']}"
                            f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
                        )
                
                result = asyncio.run(send_message_to_all_users(
                    self.telegram_bot_token,
                    full_message,
                    database_url=database_url,
                    users_file="users.json"
                ))
                if result > 0:
                    logger.info(f"Telegram notification sent to {result} users")
                    return True
            except Exception as e:
                logger.debug(f"Failed to send to multiple users: {e}")
            
            # Fallback to single chat ID for backward compatibility
            if hasattr(self, 'telegram_chat_id') and self.telegram_chat_id:
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                payload = {
                    'chat_id': self.telegram_chat_id,
                    'text': full_message,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                
                logger.info("Telegram notification sent to single chat ID")
                return True
            
            logger.warning("No Telegram recipients configured")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def _send_email(self, subject: str, message: str) -> bool:
        """
        Send notification via Email.
        
        Args:
            subject: Email subject
            message: Email message
            
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            
            # Create HTML content
            html_content = f"""
            <html>
                <body>
                    <h2>{subject}</h2>
                    <p>{message.replace(chr(10), '<br>')}</p>
                    <hr>
                    <p><small>This notification was sent by IDATA Appointment Checker</small></p>
                </body>
            </html>
            """
            
            # Attach parts
            text_part = MIMEText(message, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                server.send_message(msg)
            
            logger.info("Email notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def send_appointment_available_notification(self, details: str):
        """
        Send notification for available appointments.
        
        Args:
            details: Details about available appointments
        """
        subject = "✅ Italy Visa Appointments Available!"
        message = f"Great news! Italy visa appointments are now available.\n\n{details}\n\nAct quickly as appointments may fill up fast!"
        
        self.send_notification(subject, message)
    
    def send_error_notification(self, error: str):
        """
        Send notification for errors.
        
        Args:
            error: Error message
        """
        subject = "❌ IDATA Appointment Checker Error"
        message = f"An error occurred while checking appointments:\n\n{error}\n\nPlease check the logs for more details."
        
        self.send_notification(subject, message)
    
    def send_status_notification(self, status: str):
        """
        Send general status notification.
        
        Args:
            status: Status message
        """
        subject = "ℹ️ IDATA Appointment Checker Status"
        
        # For Telegram, we'll send the status message directly since it already contains formatting
        if self.telegram_enabled:
            try:
                # Try to send to multiple users first
                try:
                    from ..bot.bot_handler import send_message_to_all_users
                    
                    # Build database URL if available
                    database_url = None
                    if hasattr(self, 'config') and self.config.get('database', {}).get('enabled'):
                        db_config = self.config['database']
                        if db_config['url']:
                            database_url = db_config['url']
                        else:
                            database_url = (
                                f"postgresql://{db_config['user']}:{db_config['password']}"
                                f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
                            )
                    
                    result = asyncio.run(send_message_to_all_users(
                        self.telegram_bot_token,
                        status,
                        database_url=database_url,
                        users_file="users.json"
                    ))
                    if result > 0:
                        logger.info(f"Telegram status notification sent to {result} users")
                    else:
                        raise Exception("No users to send to")
                except Exception as e:
                    logger.debug(f"Failed to send to multiple users: {e}")
                    
                    # Fallback to single chat ID
                    if hasattr(self, 'telegram_chat_id') and self.telegram_chat_id:
                        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                        payload = {
                            'chat_id': self.telegram_chat_id,
                            'text': status,
                            'parse_mode': 'Markdown'
                        }
                        
                        response = requests.post(url, json=payload, timeout=10)
                        response.raise_for_status()
                        
                        logger.info("Telegram status notification sent to single chat ID")
                    else:
                        logger.warning("No Telegram recipients configured for status notification")
                        
            except Exception as e:
                logger.error(f"Failed to send Telegram status notification: {e}")
        
        # For email, use the standard method
        if self.email_enabled:
            self._send_email(subject, status)