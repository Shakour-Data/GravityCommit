#!/usr/bin/env python3
"""
Test script to verify CI/CD integration functionality
"""

import os
import tempfile
from pathlib import Path
from autocommit.ci_cd_integration import CICDManager, GitHubActions, GitLabCI, JenkinsCI

def test_ci_cd_integration():
    """Test the CI/CD integration functionality"""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_project"
        test_dir.mkdir()

        print("Testing CI/CD Integration functionality:")
        print("=" * 50)

        # Initialize CI/CD Manager
        cicd_mgr = CICDManager(str(test_dir))

        # Test adding integrations (without actual credentials)
        print("✓ Testing integration setup...")

        # Test GitHub Actions setup
        cicd_mgr.add_github_actions("test-owner", "test-repo", "fake-token")
        print("✓ GitHub Actions integration added")

        # Test GitLab CI setup
        cicd_mgr.add_gitlab_ci("12345", "fake-token")
        print("✓ GitLab CI integration added")

        # Test Jenkins setup
        cicd_mgr.add_jenkins("http://localhost:8080", "test-job")
        print("✓ Jenkins integration added")

        # Test available platforms
        platforms = cicd_mgr.get_available_platforms()
        print(f"✓ Available platforms: {platforms}")
        assert len(platforms) == 3, f"Expected 3 platforms, got {len(platforms)}"
        assert 'github' in platforms
        assert 'gitlab' in platforms
        assert 'jenkins' in platforms

        # Test hook system
        print("\n✓ Testing hook system...")

        hook_executed = {'count': 0}

        def test_hook():
            hook_executed['count'] += 1
            print("✓ Hook executed")

        # Add hooks
        cicd_mgr.integrations['github'].add_hook('pre_commit', test_hook)
        cicd_mgr.integrations['github'].add_hook('post_commit', test_hook)

        # Trigger hooks
        cicd_mgr.integrations['github'].trigger_hooks('pre_commit')
        cicd_mgr.integrations['github'].trigger_hooks('post_commit')

        assert hook_executed['count'] == 2, f"Expected 2 hook executions, got {hook_executed['count']}"

        print("\n✓ All CI/CD Integration tests passed!")
        return True

if __name__ == "__main__":
    try:
        test_ci_cd_integration()
        print("\n🎉 CI/CD Integration module testing completed successfully!")
    except Exception as e:
        print(f"\n❌ CI/CD Integration testing failed: {e}")
        exit(1)
