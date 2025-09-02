import click
from autocommit.ci_cd_integration import CICDManager
from pathlib import Path

@click.group()
def ci_cli():
    """CI/CD integration commands"""
    pass

@ci_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--repo-owner', required=True, help='GitHub repository owner')
@click.option('--repo-name', required=True, help='GitHub repository name')
@click.option('--token', required=True, help='GitHub personal access token')
def setup_github(project_path, repo_owner, repo_name, token):
    """Setup GitHub Actions integration"""
    ci_manager = CICDManager(str(project_path))
    ci_manager.add_github_actions(repo_owner, repo_name, token)
    click.echo("✓ GitHub Actions integration configured")

@ci_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--project-id', required=True, help='GitLab project ID')
@click.option('--token', required=True, help='GitLab personal access token')
@click.option('--gitlab-url', default='https://gitlab.com', help='GitLab instance URL')
def setup_gitlab(project_path, project_id, token, gitlab_url):
    """Setup GitLab CI integration"""
    ci_manager = CICDManager(str(project_path))
    ci_manager.add_gitlab_ci(project_id, token, gitlab_url)
    click.echo("✓ GitLab CI integration configured")

@ci_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--jenkins-url', required=True, help='Jenkins server URL')
@click.option('--job-name', required=True, help='Jenkins job name')
@click.option('--username', help='Jenkins username')
@click.option('--token', help='Jenkins API token or password')
def setup_jenkins(project_path, jenkins_url, job_name, username, token):
    """Setup Jenkins integration"""
    ci_manager = CICDManager(str(project_path))
    ci_manager.add_jenkins(jenkins_url, job_name, username, token)
    click.echo("✓ Jenkins integration configured")

@ci_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def list(project_path):
    """List configured CI/CD platforms"""
    ci_manager = CICDManager(str(project_path))
    platforms = ci_manager.get_available_platforms()

    if platforms:
        click.echo("Configured CI/CD platforms:")
        for platform in platforms:
            click.echo(f"  - {platform}")
    else:
        click.echo("No CI/CD platforms configured")
