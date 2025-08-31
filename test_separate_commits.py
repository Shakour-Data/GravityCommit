#!/usr/bin/env python3
"""
Test script to verify separate commits functionality
"""

import os
import tempfile
import shutil
from pathlib import Path
from autocommit.git_operations import GitOperations
from autocommit.commit_generator import CommitGenerator

def test_separate_commits():
    """Test that each changed file gets committed separately"""

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

        # Create test files
        (test_dir / "file1.py").write_text("print('Hello from file1')")
        (test_dir / "file2.py").write_text("print('Hello from file2')")
        (test_dir / "file3.txt").write_text("This is a text file")

        # Modify existing file
        readme = test_dir / "README.md"
        readme.write_text(readme.read_text() + "\n\n## Changes\n- Added test files")

        print("Created test files:")
        print("- file1.py (new)")
        print("- file2.py (new)")
        print("- file3.txt (new)")
        print("- README.md (modified)")

        # Initialize our classes
        git_ops = GitOperations(str(test_dir))
        commit_gen = CommitGenerator(str(test_dir))

        # Get status of changes
        status = git_ops.check_status()
        changed_files = status['unstaged'] + status['untracked']

        print(f"\nFound {len(changed_files)} changed files:")
        for file in changed_files:
            print(f"- {file}")

        # Commit each file separately
        committed_count = 0
        for file_path in changed_files:
            # Determine change type
            if file_path in status['untracked']:
                change_type = 'added'
            elif file_path in status['unstaged']:
                change_type = 'modified'
            else:
                change_type = 'modified'  # fallback

            # Generate commit message
            message = commit_gen.generate_single_file_commit(file_path, change_type)
            print(f"\nCommitting {file_path} with message: '{message}'")

            # Commit the file
            if git_ops.commit_single_file(file_path, message):
                print(f"✓ Successfully committed {file_path}")
                committed_count += 1
            else:
                print(f"✗ Failed to commit {file_path}")

        print(f"\nCommitted {committed_count} files successfully")

        # Show commit history
        print("\n=== COMMIT HISTORY ===")
        result = os.popen("git log --oneline").read()
        print(result)

        # Verify separate commits
        commit_count = len(result.strip().split('\n')) - 1  # Subtract initial commit
        print(f"\nTotal commits created: {commit_count}")
        print(f"Files committed separately: {committed_count}")

        if commit_count == committed_count:
            print("✓ SUCCESS: Each file was committed separately!")
        else:
            print("✗ WARNING: Commit count doesn't match file count")

if __name__ == "__main__":
    test_separate_commits()
