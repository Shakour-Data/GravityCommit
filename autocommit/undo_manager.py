from pathlib import Path
from typing import List, Optional
import git
from git import Repo
import click

class UndoManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.repo = None
        self._init_repo()

    def _init_repo(self):
        try:
            self.repo = Repo(self.project_path)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Directory {self.project_path} is not a git repository")

    def get_recent_commits(self, limit: int = 5) -> List[dict]:
        """Get list of recent commits with details"""
        if not self.repo:
            return []

        commits = []
        for commit in list(self.repo.iter_commits())[:limit]:
            commits.append({
                'hash': commit.hexsha[:8],
                'message': commit.message.strip(),
                'author': commit.author.name,
                'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'files_changed': len(list(commit.stats.files.keys()))
            })
        return commits

    def undo_last_commit(self, keep_changes: bool = False) -> bool:
        """Undo the last commit, optionally keeping changes staged"""
        if not self.repo:
            return False

        try:
            if keep_changes:
                # Use git reset --soft HEAD~1 to keep changes staged
                self.repo.git.reset('--soft', 'HEAD~1')
                click.echo("✓ Last commit undone, changes kept staged")
            else:
                # Use git reset --hard HEAD~1 to completely remove changes
                self.repo.git.reset('--hard', 'HEAD~1')
                click.echo("✓ Last commit undone, changes removed")
            return True
        except Exception as e:
            click.echo(f"✗ Failed to undo commit: {e}")
            return False

    def undo_multiple_commits(self, count: int, keep_changes: bool = False) -> bool:
        """Undo multiple recent commits"""
        if not self.repo or count < 1:
            return False

        try:
            target_commit = f'HEAD~{count}'
            if keep_changes:
                self.repo.git.reset('--soft', target_commit)
                click.echo(f"✓ Undid {count} commits, changes kept staged")
            else:
                self.repo.git.reset('--hard', target_commit)
                click.echo(f"✓ Undid {count} commits, changes removed")
            return True
        except Exception as e:
            click.echo(f"✗ Failed to undo {count} commits: {e}")
            return False

    def undo_to_commit(self, commit_hash: str, keep_changes: bool = False) -> bool:
        """Undo commits back to a specific commit hash"""
        if not self.repo:
            return False

        try:
            if keep_changes:
                self.repo.git.reset('--soft', commit_hash)
                click.echo(f"✓ Reset to commit {commit_hash[:8]}, changes kept staged")
            else:
                self.repo.git.reset('--hard', commit_hash)
                click.echo(f"✓ Reset to commit {commit_hash[:8]}, changes removed")
            return True
        except Exception as e:
            click.echo(f"✗ Failed to reset to commit {commit_hash[:8]}: {e}")
            return False

    def show_undo_preview(self, count: int = 1) -> None:
        """Show what would be undone without actually doing it"""
        if not self.repo:
            return

        try:
            # Get the commits that would be undone
            commits = list(self.repo.iter_commits())[:count]

            click.echo(f"\nPreview of undoing {count} commit(s):")
            click.echo("-" * 50)

            for i, commit in enumerate(commits, 1):
                click.echo(f"{i}. {commit.hexsha[:8]} - {commit.message.strip()[:50]}...")
                click.echo(f"   Author: {commit.author.name}")
                click.echo(f"   Date: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M')}")
                click.echo(f"   Files changed: {len(list(commit.stats.files.keys()))}")
                click.echo()

        except Exception as e:
            click.echo(f"✗ Failed to preview undo: {e}")
