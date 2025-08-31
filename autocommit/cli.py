#!/usr/bin/env python3
"""
Command Line Interface for GravityCommit
"""

import sys
import os
from pathlib import Path
import click
from .config_manager import ConfigManager
from .commit_generator import CommitGenerator
from .git_operations import GitOperations
from .scheduler import Scheduler
from .daemon_manager import DaemonManager
from .project_monitor import ProjectMonitor

@click.group()
def cli():
    """GravityCommit - Automatic commit tool for your projects"""
    pass

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--interval', default=10, help='Commit interval in minutes')
def setup(project_path, interval):
    """Setup automatic commits for a project"""
    project_path = Path(project_path).resolve()

    # Check if it's a git repository
    if not (project_path / '.git').exists():
        click.echo("Error: Not a git repository")
        return

    # Create configuration
    config = ConfigManager(str(project_path))
    config.set_interval(interval)

    # Install service
    daemon = DaemonManager(str(project_path))
    if daemon.install_service():
        click.echo(f"✓ AutoCommit setup complete for {project_path}")
        click.echo(f"✓ Commit interval: {interval} minutes")
        click.echo("✓ Service installed and started")
    else:
        click.echo("✗ Failed to install service")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def remove(project_path):
    """Remove automatic commits from a project"""
    project_path = Path(project_path).resolve()

    # Stop and remove service
    daemon = DaemonManager(str(project_path))
    if daemon.uninstall_service():
        # Remove configuration
        config = ConfigManager(str(project_path))
        config.remove_config()

        click.echo(f"✓ AutoCommit removed from {project_path}")
    else:
        click.echo("✗ Failed to remove service")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def status(project_path):
    """Check the status of AutoCommit for a project"""
    project_path = Path(project_path).resolve()

    config = ConfigManager(str(project_path))
    daemon = DaemonManager(str(project_path))
    monitor = ProjectMonitor(str(project_path))

    click.echo(f"Project: {project_path}")
    click.echo(f"Interval: {config.get_interval()} minutes")
    click.echo(f"Service running: {daemon.is_running()}")
    click.echo(f"Project open: {monitor.is_project_open()}")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def daemon(project_path):
    """Run the daemon process (internal use)"""
    project_path = Path(project_path).resolve()

    config = ConfigManager(str(project_path))
    git_ops = GitOperations(str(project_path))
    commit_gen = CommitGenerator(str(project_path))
    monitor = ProjectMonitor(str(project_path))
    scheduler = Scheduler(config.get_interval())

    def commit_callback():
        if monitor.is_project_open():
            if git_ops.has_changes():
                status = git_ops.check_status()
                changed_files = status['unstaged'] + status['untracked']

                if changed_files:
                    committed_count = 0
                    for file_path in changed_files:
                        # Determine change type
                        if file_path in status['untracked']:
                            change_type = 'added'
                        elif file_path in status['unstaged']:
                            change_type = 'modified'
                        else:
                            change_type = 'modified'  # fallback

                        # Generate commit message for this file
                        message = commit_gen.generate_single_file_commit(file_path, change_type)

                        # Commit this file separately
                        if git_ops.commit_single_file(file_path, message):
                            click.echo(f"✓ Committed {file_path}: {message}")
                            committed_count += 1
                        else:
                            click.echo(f"✗ Failed to commit {file_path}")

                    if committed_count == 0:
                        click.echo("✗ No files were committed")
                    else:
                        click.echo(f"✓ Committed {committed_count} file(s)")
                else:
                    click.echo("No changes to commit")
            else:
                click.echo("No changes detected")
        else:
            click.echo("Project not open, skipping commit")

    click.echo(f"Starting AutoCommit daemon for {project_path}")
    scheduler.start(commit_callback)

    # Keep the daemon running
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("Stopping daemon...")
        scheduler.stop()

def main():
    cli()

if __name__ == '__main__':
    main()
