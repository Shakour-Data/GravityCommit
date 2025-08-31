import os
from pathlib import Path
from typing import List, Optional, Dict
import git
from git import Repo

class GitOperations:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.repo = None
        self._init_repo()

    def _init_repo(self):
        """Initialize git repository object"""
        try:
            self.repo = Repo(self.project_path)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Directory {self.project_path} is not a git repository")

    def stage_changes(self) -> List[str]:
        """Stage all changes and return list of staged files"""
        if not self.repo:
            return []

        # Add all changes
        self.repo.git.add(A=True)

        # Get staged files
        staged = []
        for item in self.repo.index.diff('HEAD', cached=True):
            staged.append(item.a_path)

        # Also include untracked files that were added
        for item in self.repo.untracked_files:
            if item in self.repo.index.diff('HEAD', cached=True):
                staged.append(item)

        return staged

    def commit(self, message: str) -> bool:
        """Commit staged changes with given message"""
        if not self.repo:
            return False

        try:
            self.repo.index.commit(message)
            return True
        except Exception as e:
            print(f"Commit failed: {e}")
            return False

    def commit_single_file(self, file_path: str, message: str) -> bool:
        """Commit a single file with given message"""
        if not self.repo:
            return False

        try:
            # Stage only the specific file
            self.repo.index.add([file_path])
            # Commit only this file
            self.repo.index.commit(message)
            return True
        except Exception as e:
            print(f"Commit failed for {file_path}: {e}")
            return False

    def check_status(self) -> Dict[str, List[str]]:
        """Check repository status and return changes"""
        if not self.repo:
            return {'staged': [], 'unstaged': [], 'untracked': []}

        status = {
            'staged': [],
            'unstaged': [],
            'untracked': []
        }

        # Get staged changes
        for item in self.repo.index.diff('HEAD', cached=True):
            status['staged'].append(item.a_path)

        # Get unstaged changes
        for item in self.repo.index.diff('HEAD'):
            status['unstaged'].append(item.a_path)

        # Get untracked files
        status['untracked'] = self.repo.untracked_files

        return status

    def has_changes(self) -> bool:
        """Check if there are any changes to commit"""
        status = self.check_status()
        return bool(status['staged'] or status['unstaged'] or status['untracked'])

    def get_staged_files(self) -> List[str]:
        """Get list of currently staged files"""
        if not self.repo:
            return []

        staged = []
        for item in self.repo.index.diff('HEAD', cached=True):
            staged.append(item.a_path)
        return staged
