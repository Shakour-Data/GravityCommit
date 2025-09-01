#!/usr/bin/env python3
"""
Test script to verify undo manager functionality
"""

import os
import tempfile
import shutil
from pathlib import Path
from autocommit.undo_manager import UndoManager

def test_undo_manager():
    """Test the UndoManager class functionality"""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_project"
        test_dir.mkdir()

        # Initialize git repository
        os.chdir(test_dir)
        os.system("git init")
        os.system("git config user.name 'Test User'")
        os.system("git config user.email 'test@example.com'")

        # Create initial commit
        (test_dir / "README.md").write_text("# Test Project")
        os.system("git add README.md")
        os.system("git commit -m 'Initial commit'")

        # Create more commits
        (test_dir / "file1.py").write_text("print('File 1')")
        os.system("git add file1.py")
        os.system("git commit -m 'Add file1'")

        (test_dir / "file2.py").write_text("print('File 2')")
        os.system("git add file2.py")
        os.system("git commit -m 'Add file2'")

        (test_dir / "file3.py").write_text("print('File 3')")
        os.system("git add file3.py")
        os.system("git commit -m 'Add file3'")

        print("Testing UndoManager functionality:")
        print("=" * 50)

        # Initialize UndoManager
        undo_mgr = UndoManager(str(test_dir))

        # Test getting recent commits
        recent_commits = undo_mgr.get_recent_commits(3)
        print(f"✓ Recent commits count: {len(recent_commits)}")
        assert len(recent_commits) == 3, f"Expected 3 commits, got {len(recent_commits)}"

        print("✓ Recent commits:")
        for i, commit in enumerate(recent_commits, 1):
            print(f"  {i}. {commit['hash']} - {commit['message']}")

        # Test undo preview
        print("\n✓ Undo preview (last 2 commits):")
        undo_mgr.show_undo_preview(2)

        # Test undo last commit (keeping changes)
        print("\n✓ Testing undo last commit (keeping changes)...")
        success = undo_mgr.undo_last_commit(keep_changes=True)
        assert success, "Undo last commit should succeed"
        print("✓ Undo last commit successful")

        # Verify the commit was undone
        result = os.popen("git log --oneline -n 3").read().strip().split('\n')
        print(f"✓ Commits after undo: {len(result)}")
        assert len(result) == 3, f"Expected 3 commits after undo, got {len(result)}"

        # Test undo multiple commits
        print("\n✓ Testing undo multiple commits...")
        success = undo_mgr.undo_multiple_commits(2, keep_changes=False)
        assert success, "Undo multiple commits should succeed"
        print("✓ Undo multiple commits successful")

        # Verify commits were removed
        result = os.popen("git log --oneline").read().strip().split('\n')
        print(f"✓ Commits after multiple undo: {len(result)}")
        assert len(result) == 1, f"Expected 1 commit after multiple undo, got {len(result)}"

        print("\n✓ All UndoManager tests passed!")
        return True

if __name__ == "__main__":
    try:
        test_undo_manager()
        print("\n🎉 UndoManager module testing completed successfully!")
    except Exception as e:
        print(f"\n❌ UndoManager testing failed: {e}")
        exit(1)
