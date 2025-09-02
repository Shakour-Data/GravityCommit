import click
from .notifications import NotificationManager
from pathlib import Path

@click.group()
def notify_cli():
    """Notification related commands"""
    pass

@notify_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--smtp-server', required=True, help='SMTP server address')
@click.option('--smtp-port', default=587, help='SMTP server port')
@click.option('--username', required=True, help='SMTP username')
@click.option('--password', required=True, help='SMTP password')
@click.option('--from-email', required=True, help='From email address')
def setup_email(project_path, smtp_server, smtp_port, username, password, from_email):
    """Setup email notifications"""
    notifier = NotificationManager(str(project_path))
    notifier.setup_email(smtp_server, smtp_port, username, password, from_email)
    click.echo("✓ Email notifications configured")

@notify_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--webhook-url', required=True, help='Slack webhook URL')
def setup_slack(project_path, webhook_url):
    """Setup Slack notifications"""
    notifier = NotificationManager(str(project_path))
    notifier.setup_slack(webhook_url)
    click.echo("✓ Slack notifications configured")

@notify_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--webhook-url', required=True, help='Webhook URL')
@click.option('--headers', default='', help='Additional headers (key:value,key:value)')
def setup_webhook(project_path, webhook_url, headers):
    """Setup webhook notifications"""
    headers_dict = {}
    if headers:
        for header in headers.split(','):
            if ':' in header:
                key, value = header.split(':', 1)
                headers_dict[key.strip()] = value.strip()

    notifier = NotificationManager(str(project_path))
    notifier.setup_webhook(webhook_url, headers_dict)
    click.echo("✓ Webhook notifications configured")

@notify_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--type', 'notification_type', default='desktop', help='Notification type (desktop, email, slack, webhook)')
@click.option('--message', default='Test notification', help='Custom message')
def test(project_path, notification_type, message):
    """Test all configured notifications"""
    notifier = NotificationManager(str(project_path))

    if notification_type == 'desktop':
        notifier.setup_desktop()

    success = notifier.notify_important_commit(
        {'message': message, 'type': 'test'},
        f"Test notification: {message}"
    )

    if success:
        click.echo(f"✓ {notification_type.title()} notification sent successfully")
    else:
        click.echo(f"✗ Failed to send {notification_type} notification")
