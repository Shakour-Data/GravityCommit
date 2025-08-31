# TODO: Implement Separate Commits per Changed File

## Overview
Modify the GravityCommit package to create individual commits for each changed file with file-specific commit messages.

## Tasks
- [x] Update GitOperations class to add single file commit method
- [x] Update CommitGenerator class to add single file commit message generation
- [x] Update CLI daemon commit logic to iterate over changed files and commit each separately
- [x] Test the new commit behavior - PASSED ✓

## Files to Modify
- autocommit/git_operations.py
- autocommit/commit_generator.py
- autocommit/cli.py

## Implementation Details
- Add `commit_single_file` method to GitOperations
- Add `generate_single_file_commit` method to CommitGenerator
- Modify `commit_callback` in cli.py to process files individually
