from pathlib import Path
from typing import Dict, Any
import git
from git import Repo
import datetime

class Statistics:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.repo = None
        self._init_repo()

    def _init_repo(self):
        try:
            self.repo = Repo(self.project_path)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Directory {self.project_path} is not a git repository")

    def get_commit_count(self) -> int:
        """Return total number of commits in the repository"""
        if not self.repo:
            return 0
        return sum(1 for _ in self.repo.iter_commits())

    def get_commit_stats(self) -> Dict[str, Any]:
        """Return statistics about commits such as counts by author and date"""
        if not self.repo:
            return {}

        stats = {
            'total_commits': 0,
            'commits_by_author': {},
            'commits_by_date': {},
        }

        for commit in self.repo.iter_commits():
            stats['total_commits'] += 1
            author = commit.author.name
            date_str = datetime.datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d')

            stats['commits_by_author'][author] = stats['commits_by_author'].get(author, 0) + 1
            stats['commits_by_date'][date_str] = stats['commits_by_date'].get(date_str, 0) + 1

        return stats

    def get_progress_report(self) -> Dict[str, Any]:
        """Generate a simple progress report based on commit messages"""
        if not self.repo:
            return {}

        progress = {
            'start': 0,
            'progress': 0,
            'milestone': 0,
            'complete': 0,
            'fix': 0,
            'refactor': 0,
            'docs': 0,
            'test': 0,
            'deploy': 0,
            'review': 0,
            'feat': 0,
        }

        for commit in self.repo.iter_commits():
            message = commit.message.lower()
            for key in progress.keys():
                if key in message:
                    progress[key] += 1

        return progress
