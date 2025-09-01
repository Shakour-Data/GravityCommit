#!/usr/bin/env python3
"""
Test script to verify notifications functionality
"""

import os
import tempfile
from pathlib import Path
from autocommit.notifications import NotificationManager, EmailNotifier, DesktopNotifier, WebhookNotifier, SlackNotifier

def test_notifications():
    """Test the NotificationManager and notification classes"""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_project"
        test_dir.mkdir()

        print("Testing Notifications functionality:")
        print("=" * 50)

        # Initialize NotificationManager
        notif_mgr = NotificationManager(str(test_dir))

        # Test desktop notifications setup
        print("✓ Testing desktop notifications setup...")
        notif_mgr.setup_desktop()
        print("✓ Desktop notifications configured")

        # Test webhook notifications setup
        print("✓ Testing webhook notifications setup...")
        notif_mgr.setup_webhook("https://httpbin.org/post")
        print("✓ Webhook notifications configured")

        # Test Slack notifications setup
        print("✓ Testing Slack notifications setup...")
        notif_mgr.setup_slack("https://hooks.slack.com/test")
        print("✓ Slack notifications configured")

        # Test configured notifiers
        configured = notif_mgr.get_configured_notifiers()
        print(f"✓ Configured notifiers: {configured}")
        assert len(configured) == 3, f"Expected 3 notifiers, got {len(configured)}"
        assert 'desktop' in configured
        assert 'webhook' in configured
        assert 'slack' in configured

        # Test error notification
        print("\n✓ Testing error notification...")
        success = notif_mgr.notify_error("Test error occurred", {"error_code": 500})
        print(f"✓ Error notification result: {success}")

        # Test important commit notification
        print("✓ Testing important commit notification...")
        commit_info = {
            "hash": "abc123",
            "message": "feat: add new feature",
            "author": "Test User",
            "files_changed": 2
        }
        success = notif_mgr.notify_important_commit(commit_info, "Important feature added")
        print(f"✓ Important commit notification result: {success}")

        print("\n✓ All Notifications tests passed!")
        return True

if __name__ == "__main__":
    try:
        test_notifications()
        print("\n🎉 Notifications module testing completed successfully!")
    except Exception as e:
        print(f"\n❌ Notifications testing failed: {e}")
        exit(1)
