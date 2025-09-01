#!/usr/bin/env python3
"""
Container-specific commands for GravityCommit
"""

import os
import sys
import time
import signal
import subprocess
import tempfile
from pathlib import Path
import click
import psutil

from .config_manager import ConfigManager
from .commit_generator import CommitGenerator
from .git_operations import GitOperations
from .project_monitor import ProjectMonitor
from .scheduler import Scheduler

@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--interval', default=5, help='Commit interval in minutes')
@click.option('--background', is_flag=True, help='Run in background (detached from terminal)')
def container_setup(project_path, interval, background):
    """Setup auto-commit for container environments (no systemd required)"""
    project_path = Path(project_path).resolve()

    # Check if it's a git repository
    if not (project_path / '.git').exists():
        click.echo("Error: Not a git repository")
        return

    # Create configuration with manual override enabled
    config = ConfigManager(str(project_path))
    config.set_interval(interval)
    config.set_manual_override_open(True)  # Always override for containers

    click.echo(f"✓ AutoCommit container setup complete for {project_path}")
    click.echo(f"✓ Commit interval: {interval} minutes")
    click.echo("✓ Manual override enabled (project always considered 'open')")

    if background:
        click.echo("✓ Starting daemon in background...")
        start_container_daemon(str(project_path), background=True)
    else:
        click.echo("✓ To start auto-commit, run:")
        click.echo(f"  autocommit container-start {project_path}")
        click.echo("✓ Or run in background:")
        click.echo(f"  autocommit container-start {project_path} --background")

@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--background', is_flag=True, help='Run in background (detached from terminal)')
def container_start(project_path, background):
    """Start auto-commit daemon for container environments"""
    project_path = Path(project_path).resolve()

    config = ConfigManager(str(project_path))
    if not config.get_manual_override_open():
        click.echo("✗ Project not configured for container mode. Run 'autocommit container-setup' first.")
        return

    click.echo(f"Starting AutoCommit daemon for {project_path} (container mode)")
    start_container_daemon(str(project_path), background=background)

@click.command()
@click.argument('project_path', type=click.Path(exists=True))
def container_stop(project_path):
    """Stop auto-commit daemon for container environments"""
    project_path = Path(project_path).resolve()

    script_name = f"autocommit_{Path(project_path).name}.py"
    script_path = Path(tempfile.gettempdir()) / script_name

    if script_path.exists():
        # Find and kill the process
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python3' and script_name in ' '.join(proc.info['cmdline']):
                        proc.kill()
                        click.echo("✓ Daemon stopped")
                        script_path.unlink()
                        return
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        except Exception as e:
            click.echo(f"Error stopping daemon: {e}")

    click.echo("✗ No running daemon found")

def start_container_daemon(project_path: str, background: bool = False):
    """Start the daemon process for container environments"""
    config = ConfigManager(project_path)
    git_ops = GitOperations(project_path)
    commit_gen = CommitGenerator(project_path)
    monitor = ProjectMonitor(project_path)
    scheduler = Scheduler(config.get_interval())

    def commit_callback():
        try:
            # Always treat as project open due to manual override
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
        except Exception as e:
            click.echo(f"Error during commit: {e}")

    if background:
        # Run in background using nohup
        script_path = Path(tempfile.gettempdir()) / f"autocommit_{Path(project_path).name}.py"

        # Create a temporary script to run the daemon
        script_content = f'''
import sys
import os
import time
import signal
sys.path.insert(0, "{Path(__file__).parent.parent}")

from autocommit.config_manager import ConfigManager
from autocommit.commit_generator import CommitGenerator
from autocommit.git_operations import GitOperations
from autocommit.project_monitor import ProjectMonitor
from autocommit.scheduler import Scheduler

def commit_callback():
    try:
        config = ConfigManager("{project_path}")
        git_ops = GitOperations("{project_path}")
        commit_gen = CommitGenerator("{project_path}")
        monitor = ProjectMonitor("{project_path}")

        # Always treat as project open due to manual override
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
                        print(f"✓ Committed {{file_path}}: {{message}}")
                        committed_count += 1
                    else:
                        print(f"✗ Failed to commit {{file_path}}")

                if committed_count == 0:
                    print("✗ No files were committed")
                else:
                    print(f"✓ Committed {{committed_count}} file(s)")
            else:
                print("No changes to commit")
        else:
            print("No changes detected")
    except Exception as e:
        print(f"Error during commit: {{e}}")

def signal_handler(signum, frame):
    print("Stopping AutoCommit daemon...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

config = ConfigManager("{project_path}")
scheduler = Scheduler(config.get_interval())
scheduler.start(commit_callback)

print(f"AutoCommit daemon started for {project_path}")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping daemon...")
    scheduler.stop()
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        # Start the script in background
        try:
            subprocess.Popen(['python3', str(script_path)],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           preexec_fn=os.setsid)
            click.echo("✓ Daemon started in background")
            click.echo(f"✓ PID file: {script_path}")
        except Exception as e:
            click.echo(f"✗ Failed to start background daemon: {e}")
    else:
        # Run in foreground
        click.echo(f"Starting AutoCommit daemon for {project_path}")
        scheduler.start(commit_callback)

        # Keep the daemon running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("Stopping daemon...")
            scheduler.stop()

if __name__ == '__main__':
    # Allow running commands directly
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'setup':
            container_setup()
        elif command == 'start':
            container_start()
        elif command == 'stop':
            container_stop()
