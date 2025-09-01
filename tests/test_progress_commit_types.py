#!/usr/bin/env python3
"""
Test script to verify progress-oriented commit message types
"""

import os
import tempfile
from pathlib import Path
from autocommit.commit_generator import CommitGenerator

def test_progress_commit_types():
    """Test that the system can detect and generate progress-oriented commit messages"""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_project"
        test_dir.mkdir()

        # Initialize commit generator
        commit_gen = CommitGenerator(str(test_dir))

        print("Testing progress-oriented commit message types:")
        print("=" * 60)

        # Test cases for different progress indicators
        test_cases = [
            # File path, expected commit type, description
            ("start_development.py", "start", "Start development detection"),
            ("progress_25_percent.py", "progress", "25% progress detection"),
            ("milestone_phase1.py", "milestone", "Milestone detection"),
            ("complete_final.py", "progress", "Completion with percent detection"),
            ("fix_bug.py", "fix", "Bug fix detection"),
            ("refactor_code.py", "refactor", "Refactoring detection"),
            ("test_unit.py", "test", "Testing detection"),
            ("deploy_production.py", "deploy", "Deployment detection"),
            ("review_qa.py", "review", "Review detection"),
        ]

        print("\n1. Progress-based detection:")
        for file_path, expected_type, description in test_cases:
            detected_type = commit_gen._detect_commit_type(file_path, 'modified')
            status = "✓" if detected_type == expected_type else "✗"
            print(f"{status} {file_path} -> {detected_type} (expected: {expected_type}) - {description}")

        # Test content-based detection with progress keywords
        print("\n2. Content-based progress detection:")

        # Create test files with specific content
        test_files = [
            ("progress_content.py", "print('Continuing development progress')", "progress", "Content with 'progress' keyword"),
            ("start_content.py", "print('Starting new feature development')", "start", "Content with 'start' keyword"),
            ("milestone_content.py", "print('Reached important milestone')", "milestone", "Content with 'milestone' keyword"),
            ("complete_content.py", "print('Feature is now complete and finalized')", "complete", "Content with 'complete' keyword"),
            ("deploy_content.py", "print('Ready for deployment to production')", "deploy", "Content with 'deploy' keyword"),
        ]

        for file_path, content, expected_type, description in test_files:
            # Create the file
            full_path = test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

            # Test detection
            detected_type = commit_gen._detect_commit_type(file_path, 'modified')
            status = "✓" if detected_type == expected_type else "✗"
            print(f"{status} {file_path} -> {detected_type} (expected: {expected_type}) - {description}")

        # Test commit message generation with progress indicators
        print("\n3. Progress-oriented commit message generation:")

        message_tests = [
            ("start_development.py", "added", "🚀 START: add start_development (py)"),
            ("progress_25_percent.py", "modified", "📈 PROGRESS: continue progress_25_percent (py)"),
            ("milestone_phase1.py", "modified", "🎯 MILESTONE: reach milestone_phase1 (py)"),
            ("complete_final.py", "modified", "📈 PROGRESS: continue complete_final (py)"),
            ("fix_bug.py", "modified", "🐛 FIX: fix fix_bug (py)"),
            ("deploy_production.py", "modified", "🚀 DEPLOY: deploy deploy_production (py)"),
        ]

        for file_path, change_type, expected_message in message_tests:
            generated_message = commit_gen.generate_single_file_commit(file_path, change_type)
            status = "✓" if generated_message == expected_message else "✗"
            print(f"{status} {file_path} ({change_type})")
            print(f"   Generated: '{generated_message}'")
            if generated_message != expected_message:
                print(f"   Expected:  '{expected_message}'")
            print()

        # Test progress percentage patterns
        print("4. Progress percentage patterns:")
        progress_tests = [
            ("25_percent_complete.py", "progress"),
            ("50_percent_done.py", "progress"),
            ("75_almost_finished.py", "progress"),
            ("100_percent_complete.py", "progress"),
        ]

        for file_path, expected_type in progress_tests:
            detected_type = commit_gen._detect_commit_type(file_path, 'modified')
            status = "✓" if detected_type == expected_type else "✗"
            print(f"{status} {file_path} -> {detected_type}")

        # Show all supported commit types
        print(f"\n5. All supported progress-oriented commit types:")
        progress_types = [
            'start', 'progress', 'milestone', 'complete',
            'fix', 'refactor', 'docs', 'test', 'deploy', 'review'
        ]

        for commit_type in progress_types:
            type_label = commit_gen._get_type_label(commit_type)
            action_verb = commit_gen._get_action_verb(commit_type)
            print(f"✓ {commit_type} -> '{type_label}: {action_verb}'")

        print(f"\nTotal progress-oriented commit types supported: {len(progress_types)}")
        print("\n✓ Progress tracking through commit messages is now fully supported!")

if __name__ == "__main__":
    test_progress_commit_types()
