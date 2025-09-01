#!/usr/bin/env python3
"""
Test script to verify statistics functionality
"""

import os
import tempfile
import shutil
from pathlib import Path
from autocommit.statistics import Statistics

def test_statistics():
    """Test the Statistics class functionality"""

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

        # Create more commits with different types
        (test_dir / "feature.py").write_text("print('New feature')")
        os.system("git add feature.py")
        os.system("git commit -m 'feat: add new feature'")

        (test_dir / "fix.py").write_text("print('Bug fix')")
        os.system("git add fix.py")
        os.system("git commit -m 'fix: resolve bug'")

        (test_dir / "test_file.py").write_text("print('Test file')")
        os.system("git add test_file.py")
        os.system("git commit -m 'test: add unit tests'")

        (test_dir / "refactor.py").write_text("print('Refactored code')")
        os.system("git add refactor.py")
        os.system("git commit -m 'refactor: improve code structure'")

        print("Testing Statistics functionality:")
        print("=" * 50)

        # Initialize Statistics
        stats = Statistics(str(test_dir))

        # Test commit count
        commit_count = stats.get_commit_count()
        print(f"✓ Total commits: {commit_count}")
        assert commit_count == 5, f"Expected 5 commits, got {commit_count}"

        # Test commit statistics
        commit_stats = stats.get_commit_stats()
        print(f"✓ Commits by author: {commit_stats['commits_by_author']}")
        print(f"✓ Total commits from stats: {commit_stats['total_commits']}")

        assert commit_stats['total_commits'] == 5
        assert 'Test User' in commit_stats['commits_by_author']
        assert commit_stats['commits_by_author']['Test User'] == 5

        # Test progress report
        progress = stats.get_progress_report()
        print(f"✓ Progress report: {progress}")

        # Should detect feat, fix, test, refactor
        assert progress['feat'] >= 1, "Should detect feat commit"
        assert progress['fix'] >= 1, "Should detect fix commit"
        assert progress['test'] >= 1, "Should detect test commit"
        assert progress['refactor'] >= 1, "Should detect refactor commit"

        print("\n✓ All Statistics tests passed!")
        return True

if __name__ == "__main__":
    try:
        test_statistics()
        print("\n🎉 Statistics module testing completed successfully!")
    except Exception as e:
        print(f"\n❌ Statistics testing failed: {e}")
        exit(1)
