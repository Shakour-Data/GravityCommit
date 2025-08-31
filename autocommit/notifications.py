import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime
import subprocess
import platform

class EmailNotifier:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.logger = logging.getLogger(__name__)

    def send_notification(self, to_email: str, subject: str, message: str, commit_info: Dict[str, Any] = None):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Create HTML message with commit details
            html_content = self._create_html_message(message, commit_info)
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"Email notification sent to {to_email}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False

    def _create_html_message(self, message: str, commit_info: Dict[str, Any] = None) -> str:
        """Create HTML formatted message"""
        html = f"""
        <html>
        <body>
            <h2>GravityCommit Notification</h2>
            <p>{message}</p>
        """

        if commit_info:
            html += """
            <h3>Commit Details:</h3>
            <ul>
            """
            for key, value in commit_info.items():
                html += f"<li><strong>{key}:</strong> {value}</li>"
            html += "</ul>"

        html += """
            <p><small>Sent by GravityCommit at {}</small></p>
        </body>
        </html>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        return html

class DesktopNotifier:
    def __init__(self):
        self.system = platform.system().lower()
        self.logger = logging.getLogger(__name__)

    def send_notification(self, title: str, message: str, commit_info: Dict[str, Any] = None):
        """Send desktop notification"""
        try:
            if self.system == 'linux':
                return self._notify_linux(title, message)
            elif self.system == 'darwin':  # macOS
                return self._notify_macos(title, message)
            elif self.system == 'windows':
                return self._notify_windows(title, message)
            else:
                self.logger.warning(f"Desktop notifications not supported on {self.system}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to send desktop notification: {e}")
            return False

    def _notify_linux(self, title: str, message: str) -> bool:
        """Send notification on Linux using notify-send"""
        try:
            cmd = ['notify-send', title, message]
            subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try with dunst if notify-send is not available
            try:
                cmd = ['dunstify', title, message]
                subprocess.run(cmd, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.warning("notify-send or dunstify not available")
                return False

    def _notify_macos(self, title: str, message: str) -> bool:
        """Send notification on macOS using osascript"""
        try:
            script = f'display notification "{message}" with title "{title}"'
            cmd = ['osascript', '-e', script]
            subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("osascript not available")
            return False

    def _notify_windows(self, title: str, message: str) -> bool:
        """Send notification on Windows using powershell"""
        try:
            script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>{title}</text>
            <text>{message}</text>
        </binding>
    </visual>
</toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("GravityCommit").Show($toast)
            '''
            cmd = ['powershell', '-Command', script]
            subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("PowerShell toast notifications not available")
            return False

class WebhookNotifier:
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {'Content-Type': 'application/json'}
        self.logger = logging.getLogger(__name__)

    def send_notification(self, message: str, commit_info: Dict[str, Any] = None, extra_data: Dict[str, Any] = None):
        """Send webhook notification"""
        try:
            payload = {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'source': 'GravityCommit'
            }

            if commit_info:
                payload['commit_info'] = commit_info

            if extra_data:
                payload.update(extra_data)

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 201, 202]:
                self.logger.info("Webhook notification sent successfully")
                return True
            else:
                self.logger.error(f"Webhook notification failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {e}")
            return False

class SlackNotifier(WebhookNotifier):
    def __init__(self, webhook_url: str):
        super().__init__(webhook_url)

    def send_notification(self, message: str, commit_info: Dict[str, Any] = None, channel: str = None):
        """Send Slack notification"""
        try:
            payload = {
                'text': message,
                'username': 'GravityCommit',
                'icon_emoji': ':robot_face:'
            }

            if channel:
                payload['channel'] = channel

            if commit_info:
                # Create a more detailed Slack message
                blocks = [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': '🚀 GravityCommit Notification'
                        }
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': message
                        }
                    }
                ]

                if commit_info:
                    fields = []
                    for key, value in commit_info.items():
                        fields.append({
                            'type': 'mrkdwn',
                            'text': f'*{key}*\n{value}'
                        })

                    blocks.append({
                        'type': 'section',
                        'fields': fields
                    })

                payload['blocks'] = blocks

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("Slack notification sent successfully")
                return True
            else:
                self.logger.error(f"Slack notification failed: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")
            return False

class NotificationManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        self.notifiers = {
            'email': None,
            'desktop': None,
            'webhook': None,
            'slack': None
        }

    def setup_email(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        """Setup email notifications"""
        self.notifiers['email'] = EmailNotifier(smtp_server, smtp_port, username, password, from_email)
        self.logger.info("Email notifications configured")

    def setup_desktop(self):
        """Setup desktop notifications"""
        self.notifiers['desktop'] = DesktopNotifier()
        self.logger.info("Desktop notifications configured")

    def setup_webhook(self, webhook_url: str, headers: Dict[str, str] = None):
        """Setup webhook notifications"""
        self.notifiers['webhook'] = WebhookNotifier(webhook_url, headers)
        self.logger.info("Webhook notifications configured")

    def setup_slack(self, webhook_url: str):
        """Setup Slack notifications"""
        self.notifiers['slack'] = SlackNotifier(webhook_url)
        self.logger.info("Slack notifications configured")

    def notify_important_commit(self, commit_info: Dict[str, Any], custom_message: str = None):
        """Send notifications for important commits"""
        message = custom_message or f"Important commit detected: {commit_info.get('message', 'N/A')}"

        # Send to all configured notifiers
        success_count = 0
        for notifier_type, notifier in self.notifiers.items():
            if notifier:
                try:
                    if notifier_type == 'email':
                        # Email needs recipient - this would be configured
                        pass  # Skip for now, needs recipient configuration
                    elif notifier_type == 'desktop':
                        success = notifier.send_notification("GravityCommit", message, commit_info)
                    elif notifier_type in ['webhook', 'slack']:
                        success = notifier.send_notification(message, commit_info)
                    else:
                        continue

                    if success:
                        success_count += 1
                        self.logger.info(f"{notifier_type} notification sent successfully")
                    else:
                        self.logger.warning(f"{notifier_type} notification failed")

                except Exception as e:
                    self.logger.error(f"Error sending {notifier_type} notification: {e}")

        return success_count > 0

    def notify_error(self, error_message: str, error_details: Dict[str, Any] = None):
        """Send error notifications"""
        message = f"GravityCommit Error: {error_message}"

        # Send to desktop and configured notifiers
        success_count = 0
        for notifier_type, notifier in self.notifiers.items():
            if notifier and notifier_type in ['desktop', 'webhook', 'slack']:
                try:
                    if notifier_type == 'desktop':
                        success = notifier.send_notification("GravityCommit Error", message, error_details)
                    else:
                        success = notifier.send_notification(message, error_details)

                    if success:
                        success_count += 1

                except Exception as e:
                    self.logger.error(f"Error sending {notifier_type} error notification: {e}")

        return success_count > 0

    def get_configured_notifiers(self) -> List[str]:
        """Get list of configured notification types"""
        return [notifier_type for notifier_type, notifier in self.notifiers.items() if notifier is not None]
