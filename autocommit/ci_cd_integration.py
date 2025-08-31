import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import logging
from datetime import datetime

class CICDPipeline:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        self.hooks = {
            'pre_commit': [],
            'post_commit': [],
            'on_success': [],
            'on_failure': []
        }

    def add_hook(self, hook_type: str, callback: Callable):
        """Add a hook for a specific event"""
        if hook_type in self.hooks:
            self.hooks[hook_type].append(callback)
            self.logger.info(f"Added {hook_type} hook")
        else:
            self.logger.error(f"Unknown hook type: {hook_type}")

    def trigger_hooks(self, hook_type: str, *args, **kwargs):
        """Trigger all hooks of a specific type"""
        if hook_type in self.hooks:
            for hook in self.hooks[hook_type]:
                try:
                    hook(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Hook execution failed: {e}")

class GitHubActions(CICDPipeline):
    def __init__(self, project_path: str, repo_owner: str, repo_name: str, token: str):
        super().__init__(project_path)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

    def trigger_workflow(self, workflow_name: str, inputs: Dict[str, Any] = None):
        """Trigger a GitHub Actions workflow"""
        url = f"{self.api_base}/actions/workflows/{workflow_name}/dispatches"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'ref': 'main',  # or current branch
            'inputs': inputs or {}
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 204:
                self.logger.info(f"GitHub Actions workflow '{workflow_name}' triggered successfully")
                return True
            else:
                self.logger.error(f"Failed to trigger workflow: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error triggering GitHub Actions workflow: {e}")
            return False

    def get_workflow_status(self, run_id: str):
        """Get the status of a workflow run"""
        url = f"{self.api_base}/actions/runs/{run_id}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get workflow status: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {e}")
            return None

class GitLabCI(CICDPipeline):
    def __init__(self, project_path: str, project_id: str, token: str, gitlab_url: str = "https://gitlab.com"):
        super().__init__(project_path)
        self.project_id = project_id
        self.token = token
        self.gitlab_url = gitlab_url
        self.api_base = f"{gitlab_url}/api/v4/projects/{project_id}"

    def trigger_pipeline(self, ref: str = "main", variables: Dict[str, str] = None):
        """Trigger a GitLab CI pipeline"""
        url = f"{self.api_base}/trigger/pipeline"
        headers = {
            'PRIVATE-TOKEN': self.token,
            'Content-Type': 'application/json'
        }
        data = {
            'ref': ref,
            'variables': variables or {}
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                pipeline_data = response.json()
                self.logger.info(f"GitLab CI pipeline triggered successfully: {pipeline_data.get('id')}")
                return pipeline_data
            else:
                self.logger.error(f"Failed to trigger pipeline: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error triggering GitLab CI pipeline: {e}")
            return None

class JenkinsCI(CICDPipeline):
    def __init__(self, project_path: str, jenkins_url: str, job_name: str, username: str = None, token: str = None):
        super().__init__(project_path)
        self.jenkins_url = jenkins_url.rstrip('/')
        self.job_name = job_name
        self.username = username
        self.token = token

    def trigger_build(self, parameters: Dict[str, Any] = None):
        """Trigger a Jenkins build"""
        url = f"{self.jenkins_url}/job/{self.job_name}/build"
        if parameters:
            url = f"{self.jenkins_url}/job/{self.job_name}/buildWithParameters"

        auth = None
        if self.username and self.token:
            auth = (self.username, self.token)

        try:
            if parameters:
                response = requests.post(url, auth=auth, data=parameters)
            else:
                response = requests.post(url, auth=auth)

            if response.status_code in [200, 201]:
                self.logger.info(f"Jenkins build triggered successfully for job '{self.job_name}'")
                return True
            else:
                self.logger.error(f"Failed to trigger Jenkins build: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error triggering Jenkins build: {e}")
            return False

class CICDManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        self.integrations = {}

    def add_github_actions(self, repo_owner: str, repo_name: str, token: str):
        """Add GitHub Actions integration"""
        self.integrations['github'] = GitHubActions(
            str(self.project_path), repo_owner, repo_name, token
        )
        self.logger.info("GitHub Actions integration added")

    def add_gitlab_ci(self, project_id: str, token: str, gitlab_url: str = "https://gitlab.com"):
        """Add GitLab CI integration"""
        self.integrations['gitlab'] = GitLabCI(
            str(self.project_path), project_id, token, gitlab_url
        )
        self.logger.info("GitLab CI integration added")

    def add_jenkins(self, jenkins_url: str, job_name: str, username: str = None, token: str = None):
        """Add Jenkins integration"""
        self.integrations['jenkins'] = JenkinsCI(
            str(self.project_path), jenkins_url, job_name, username, token
        )
        self.logger.info("Jenkins integration added")

    def trigger_ci(self, platform: str, **kwargs):
        """Trigger CI/CD pipeline for a specific platform"""
        if platform in self.integrations:
            integration = self.integrations[platform]

            if platform == 'github':
                return integration.trigger_workflow(**kwargs)
            elif platform == 'gitlab':
                return integration.trigger_pipeline(**kwargs)
            elif platform == 'jenkins':
                return integration.trigger_build(**kwargs)
        else:
            self.logger.error(f"No integration configured for platform: {platform}")
            return False

    def get_available_platforms(self):
        """Get list of configured CI/CD platforms"""
        return list(self.integrations.keys())

    def setup_pre_commit_hook(self, platform: str, **kwargs):
        """Setup pre-commit hook to trigger CI/CD"""
        if platform in self.integrations:
            def pre_commit_trigger():
                self.logger.info(f"Triggering {platform} CI/CD before commit")
                self.trigger_ci(platform, **kwargs)

            self.integrations[platform].add_hook('pre_commit', pre_commit_trigger)

    def setup_post_commit_hook(self, platform: str, **kwargs):
        """Setup post-commit hook to trigger CI/CD"""
        if platform in self.integrations:
            def post_commit_trigger():
                self.logger.info(f"Triggering {platform} CI/CD after commit")
                self.trigger_ci(platform, **kwargs)

            self.integrations[platform].add_hook('post_commit', post_commit_trigger)
