import click
from autocommit.undo_manager import UndoManager
from pathlib import Path

@click.group()
def undo_cli():
    """Advanced undo commands"""
    pass

@undo_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('commit_hash')
@click.option('--keep-changes', is_flag=True, help='Keep changes staged after undo')
def undo_to(project_path, commit_hash, keep_changes):
    """Undo commits back to a specific commit hash"""
    undo_manager = UndoManager(str(project_path))
    success = undo_manager.undo_to_commit(commit_hash, keep_changes)

    if success:
        click.echo(f"✓ Reset to commit {commit_hash[:8]} successfully")
    else:
        click.echo(f"✗ Failed to reset to commit {commit_hash[:8]}")

@undo_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('files', nargs=-1, required=True)
@click.option('--keep-changes', is_flag=True, help='Keep changes staged after undo')
def undo_selective(project_path, files, keep_changes):
    """Undo changes for specific files"""
    undo_manager = UndoManager(str(project_path))

    # This would require extending the UndoManager with selective undo functionality
    click.echo("Selective undo functionality:")
    click.echo(f"Files to undo: {', '.join(files)}")
    click.echo(f"Keep changes: {keep_changes}")
    click.echo("Note: This feature requires extending UndoManager with selective file undo")
