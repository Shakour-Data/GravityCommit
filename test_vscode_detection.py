#!/usr/bin/env python3
"""
Test script to verify VSCode detection
"""

import os
import sys
sys.path.insert(0, '.')

from autocommit.project_monitor import ProjectMonitor

def test_vscode_detection():
    print("Testing VSCode detection...")

    # Check environment variables
    vscode_env_vars = [
        'VSCODE_IPC_HOOK_CLI',
        'TERM_PROGRAM',
        'CODESPACE_VSCODE_FOLDER'
    ]

    print("\nEnvironment variables:")
    for var in vscode_env_vars:
        value = os.getenv(var)
        print(f"{var}: {value}")

    # Test the detection method
    monitor = ProjectMonitor('/tmp/test_project')
    is_connected = monitor._is_vscode_remote_connected()
    print(f"\nVSCode remote connected: {is_connected}")

    # Test overall project open status
    is_open = monitor.is_project_open()
    print(f"Project open: {is_open}")

if __name__ == '__main__':
    test_vscode_detection()
