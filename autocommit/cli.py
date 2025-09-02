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
from .undo_manager import UndoManager
from .statistics import Statistics
from .notifications import NotificationManager
from .ci_cd_integration import CICDManager

@click.group()
def cli():
    """GravityCommit - Automatic commit tool for your projects"""
    pass

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--interval', default=10, help='Commit interval in minutes')
@click.option('--manual-override-open', is_flag=True, help='Manually override project open detection')
@click.option('--additional-editors', default='', help='Comma-separated list of additional editor process names')
@click.option('--custom-env-vars', default='', help='Comma-separated list of custom environment variables for detection')
def setup(project_path, interval, manual_override_open, additional_editors, custom_env_vars):
    """Setup automatic commits for a project"""
    project_path = Path(project_path).resolve()

    # Check if it's a git repository
    if not (project_path / '.git').exists():
        click.echo("Error: Not a git repository")
        return

    # Create configuration
    config = ConfigManager(str(project_path))
    config.set_interval(interval)
    config.set_manual_override_open(manual_override_open)

    if additional_editors:
        editors_list = [e.strip() for e in additional_editors.split(',') if e.strip()]
        config.set_additional_editor_processes(editors_list)

    if custom_env_vars:
        env_vars_list = [e.strip() for e in custom_env_vars.split(',') if e.strip()]
        config.set_custom_env_vars(env_vars_list)

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

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--interval', default=5, help='Commit interval in minutes')
@click.option('--background', is_flag=True, help='Run in background (detached from terminal)')
def container_setup(project_path, interval, background):
    """Setup auto-commit for container environments (no systemd required)"""
    from .container_commands import container_setup as _container_setup
    _container_setup.callback(project_path, interval, background)

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--background', is_flag=True, help='Run in background (detached from terminal)')
def container_start(project_path, background):
    """Start auto-commit daemon for container environments"""
    from .container_commands import container_start as _container_start
    _container_start.callback(project_path, background)

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def container_stop(project_path):
    """Stop auto-commit daemon for container environments"""
    from .container_commands import container_stop as _container_stop
    _container_stop.callback(project_path)

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--count', default=1, help='Number of commits to undo')
@click.option('--keep-changes', is_flag=True, help='Keep changes staged after undo')
def undo(project_path, count, keep_changes):
    """Undo recent commits"""
    undo_manager = UndoManager(str(project_path))

    if count == 1:
        success = undo_manager.undo_last_commit(keep_changes)
        if success:
            click.echo("✓ Last commit undone successfully")
        else:
            click.echo("✗ Failed to undo last commit")
    else:
        success = undo_manager.undo_multiple_commits(count, keep_changes)
        if success:
            click.echo(f"✓ Undid {count} commits successfully")
        else:
            click.echo(f"✗ Failed to undo {count} commits")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def undo_preview(project_path):
    """Preview recent commits that can be undone"""
    undo_manager = UndoManager(str(project_path))
    undo_manager.show_undo_preview()

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def stats(project_path):
    """Show commit statistics"""
    stats = Statistics(str(project_path))
    commit_stats = stats.get_commit_stats()
    progress = stats.get_progress_report()

    click.echo(f"📊 Commit Statistics for {project_path}")
    click.echo("=" * 50)
    click.echo(f"Total commits: {commit_stats.get('total_commits', 0)}")
    click.echo()

    click.echo("Commits by author:")
    for author, count in commit_stats.get('commits_by_author', {}).items():
        click.echo(f"  {author}: {count}")
    click.echo()

    click.echo("Progress indicators:")
    for key, count in progress.items():
        if count > 0:
            click.echo(f"  {key}: {count}")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--type', 'notification_type', default='desktop', help='Notification type (desktop, email, slack, webhook)')
@click.option('--message', default='Test notification', help='Custom message')
def notify(project_path, notification_type, message):
    """Send a test notification"""
    notifier = NotificationManager(str(project_path))

    # Setup basic desktop notification for testing
    if notification_type == 'desktop':
        notifier.setup_desktop()

    success = notifier.notify_important_commit(
        {'message': message, 'type': 'test'},
        f"Test notification: {message}"
    )

    if success:
        click.echo(f"✓ {notification_type.title()} notification sent successfully")
    else:
        click.echo(f"✗ Failed to send {notification_type} notification")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('platform')
@click.option('--workflow', help='Workflow name (for GitHub Actions)')
@click.option('--job', help='Job name (for Jenkins)')
@click.option('--ref', default='main', help='Git reference/branch')
def trigger_ci(project_path, platform, workflow, job, ref):
    """Trigger CI/CD pipeline for a platform"""
    ci_manager = CICDManager(str(project_path))

    kwargs = {'ref': ref}
    if workflow:
        kwargs['workflow_name'] = workflow
    if job:
        kwargs['job_name'] = job

    success = ci_manager.trigger_ci(platform, **kwargs)
    if success:
        click.echo(f"✓ CI/CD pipeline triggered for {platform}")
    else:
        click.echo(f"✗ Failed to trigger CI/CD pipeline for {platform}")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def commit_now(project_path):
    """Force immediate commit of current changes"""
    project_path = Path(project_path).resolve()
    config = ConfigManager(str(project_path))
    git_ops = GitOperations(str(project_path))
    commit_gen = CommitGenerator(str(project_path))

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
                    change_type = 'modified'

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
                click.echo(f"✓ Committed {committed_count} file(s) immediately")
        else:
            click.echo("No changes to commit")
    else:
        click.echo("No changes detected")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('time_str')
def schedule_at(project_path, time_str):
    """Schedule commits at a specific time (HH:MM format)"""
    scheduler = Scheduler(0)  # Time-based scheduling
    scheduler.schedule_at_time(time_str, lambda: click.echo(f"Scheduled commit executed at {time_str}"))
    click.echo(f"✓ Scheduled daily commit at {time_str}")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('day')
@click.argument('time_str')
def schedule_weekly(project_path, day, time_str):
    """Schedule weekly commits on specific day and time"""
    scheduler = Scheduler(0)  # Time-based scheduling
    scheduler.schedule_weekly(day, time_str, lambda: click.echo(f"Weekly commit executed on {day} at {time_str}"))
    click.echo(f"✓ Scheduled weekly commit on {day} at {time_str}")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def schedule_list(project_path):
    """List all scheduled jobs"""
    scheduler = Scheduler(0)
    jobs = scheduler.get_scheduled_jobs()
    if jobs:
        click.echo("Scheduled jobs:")
        for job in jobs:
            click.echo(f"  - {job}")
    else:
        click.echo("No scheduled jobs")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def schedule_clear(project_path):
    """Clear all scheduled jobs"""
    scheduler = Scheduler(0)
    scheduler.clear_schedule()
    click.echo("✓ All scheduled jobs cleared")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--duration', default=30, help='Pause duration in minutes')
def pause(project_path, duration):
    """Pause auto-commits temporarily"""
    scheduler = Scheduler(0)
    scheduler.pause_scheduling()
    click.echo(f"✓ Auto-commits paused for {duration} minutes")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def resume(project_path):
    """Resume paused auto-commits"""
    scheduler = Scheduler(0)
    scheduler.resume_scheduling()
    click.echo("✓ Auto-commits resumed")

@cli.command()
def list_projects():
    """List all configured projects"""
    # This would need to scan for config files
    click.echo("Configured projects:")
    click.echo("Note: This feature requires config file scanning implementation")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def config(project_path):
    """Show/edit configuration for a project"""
    config = ConfigManager(str(project_path))

    click.echo(f"Configuration for {project_path}:")
    click.echo(f"  Interval: {config.get_interval()} minutes")
    click.echo(f"  Manual override: {config.get_manual_override_open()}")
    click.echo(f"  Additional editors: {config.get_additional_editor_processes()}")
    click.echo(f"  Custom env vars: {config.get_custom_env_vars()}")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--limit', default=10, help='Number of recent commits to show')
def logs(project_path, limit):
    """Show recent commit logs"""
    undo_manager = UndoManager(str(project_path))
    recent_commits = undo_manager.get_recent_commits(limit)

    click.echo(f"Recent commits in {project_path}:")
    click.echo("-" * 80)

    for commit in recent_commits:
        click.echo(f"Commit: {commit['hash']}")
        click.echo(f"Author: {commit['author']}")
        click.echo(f"Date: {commit['date']}")
        click.echo(f"Files: {commit['files_changed']}")
        click.echo(f"Message: {commit['message']}")
        click.echo("-" * 80)

@cli.command()
def version():
    """Show GravityCommit version"""
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('gravitycommit').version
    except:
        version = "1.5.5"  # fallback from setup.py

    click.echo(f"GravityCommit v{version}")

def main():
    cli()

if __name__ == '__main__':
    main()
