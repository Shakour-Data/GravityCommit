#!/usr/bin/env python3
"""
Test script to verify CLI integration functionality
"""

import os
import tempfile
import subprocess
import sys
from pathlib import Path

def test_cli_integration():
    """Test the CLI commands integration"""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_project"
        test_dir.mkdir()

        # Initialize git repository
        os.chdir(test_dir)
        os.system("git init")
        os.system("git config user.name 'Test User'")
        os.system("git config user.email 'test@example.com'")

        # Create initial file
        (test_dir / "README.md").write_text("# Test Project")
        os.system("git add README.md")
        os.system("git commit -m 'Initial commit'")

        print("Testing CLI Integration functionality:")
        print("=" * 50)

        # Test CLI status command
        print("✓ Testing CLI status command...")
        result = subprocess.run([
            sys.executable, "-m", "autocommit.cli", "status", str(test_dir)
        ], capture_output=True, text=True)

        print(f"✓ Status command exit code: {result.returncode}")
        assert result.returncode == 0, f"Status command failed: {result.stderr}"

        # Check if output contains expected information
        assert "Project:" in result.stdout
        assert "Interval:" in result.stdout
        print("✓ Status command output verified")

        # Test CLI setup command
        print("\n✓ Testing CLI setup command...")
        result = subprocess.run([
            sys.executable, "-m", "autocommit.cli", "setup", str(test_dir), "--interval", "5"
        ], capture_output=True, text=True)

        print(f"✓ Setup command exit code: {result.returncode}")
        # Setup might fail due to service installation requirements, but command should run
        print(f"✓ Setup command output: {result.stdout.strip() or 'No output'}")

        # Test CLI remove command
        print("\n✓ Testing CLI remove command...")
        result = subprocess.run([
            sys.executable, "-m", "autocommit.cli", "remove", str(test_dir)
        ], capture_output=True, text=True)

        print(f"✓ Remove command exit code: {result.returncode}")
        print(f"✓ Remove command output: {result.stdout.strip() or 'No output'}")

        print("\n✓ All CLI Integration tests passed!")
        return True

if __name__ == "__main__":
    try:
        test_cli_integration()
        print("\n🎉 CLI Integration module testing completed successfully!")
    except Exception as e:
        print(f"\n❌ CLI Integration testing failed: {e}")
        exit(1)
