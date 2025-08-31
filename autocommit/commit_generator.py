import os
from pathlib import Path
from typing import List, Dict, Tuple

class CommitGenerator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

        # Define commit message types with progress indicators
        self.commit_types = {
            'start': ['start', 'begin', 'initiate', 'initialize', 'create'],
            'progress': ['progress', 'continue', 'update', 'work', 'develop', 'implement'],
            'milestone': ['milestone', 'checkpoint', 'phase', 'stage', 'step'],
            'complete': ['complete', 'finish', 'done', 'end', 'final', 'ready'],
            'fix': ['fix', 'bug', 'issue', 'error', 'patch', 'resolve'],
            'refactor': ['refactor', 'restructure', 'cleanup', 'optimize', 'improve'],
            'docs': ['doc', 'readme', 'documentation', 'comment', 'guide'],
            'test': ['test', 'spec', 'unit', 'integration', 'e2e', 'verify'],
            'deploy': ['deploy', 'release', 'publish', 'launch', 'production'],
            'review': ['review', 'feedback', 'qa', 'validate', 'check']
        }

        # Progress percentage patterns
        self.progress_patterns = {
            '25%': ['25', 'quarter', 'first-quarter'],
            '50%': ['50', 'half', 'mid', 'middle'],
            '75%': ['75', 'three-quarter', 'almost-done'],
            '100%': ['100', 'full', 'complete', 'finished', 'done']
        }

    def generate_commit(self, changes: Dict[str, List[str]]) -> str:
        """
        Generate a professional commit message based on changes
        """
        if not changes:
            return "No changes detected"

        # Analyze changes and categorize by commit type
        categorized_changes = self._categorize_changes_by_type(changes)

        message_parts = []
        for commit_type, files in categorized_changes.items():
            if files:
                message_parts.append(self._generate_typed_message(commit_type, files))

        if not message_parts:
            return "Update project files"

        return " | ".join(message_parts)

    def analyze_changes(self, staged_files: List[str]) -> Dict[str, List[str]]:
        """
        Analyze the types of changes in staged files
        """
        changes = {'added': [], 'modified': [], 'deleted': []}

        for file_path in staged_files:
            full_path = self.project_path / file_path
            if full_path.exists():
                # Check if file is tracked
                if self._is_file_tracked(file_path):
                    changes['modified'].append(file_path)
                else:
                    changes['added'].append(file_path)
            else:
                changes['deleted'].append(file_path)

        return changes

    def _is_file_tracked(self, file_path: str) -> bool:
        """Check if file is already tracked by git"""
        # This would need git integration, simplified for now
        return True

    def _generate_add_message(self, files: List[str]) -> str:
        """Generate message for added files"""
        if len(files) == 1:
            return f"Add {self._get_file_description(files[0])}"
        else:
            file_types = self._categorize_files(files)
            if len(file_types) == 1:
                return f"Add {len(files)} {list(file_types.keys())[0]} files"
            else:
                return f"Add {len(files)} new files"

    def _generate_modify_message(self, files: List[str]) -> str:
        """Generate message for modified files"""
        if len(files) == 1:
            return f"Update {self._get_file_description(files[0])}"
        else:
            return f"Update {len(files)} files"

    def _generate_delete_message(self, files: List[str]) -> str:
        """Generate message for deleted files"""
        if len(files) == 1:
            return f"Remove {self._get_file_description(files[0])}"
        else:
            return f"Remove {len(files)} files"

    def _get_file_description(self, file_path: str) -> str:
        """Get a human-readable description of the file"""
        path = Path(file_path)
        if path.suffix:
            return f"{path.stem} ({path.suffix[1:]})"
        else:
            return path.name

    def _categorize_files(self, files: List[str]) -> Dict[str, int]:
        """Categorize files by their extensions"""
        categories = {}
        for file in files:
            ext = Path(file).suffix.lower()
            if ext:
                category = ext[1:]  # remove the dot
            else:
                category = "other"
            categories[category] = categories.get(category, 0) + 1
        return categories

    def generate_single_file_commit(self, file_path: str, change_type: str) -> str:
        """
        Generate a commit message for a single file change
        change_type: 'added', 'modified', or 'deleted'
        """
        file_desc = self._get_file_description(file_path)
        commit_type = self._detect_commit_type(file_path, change_type)

        # Use progress-oriented format with appropriate action verbs
        type_label = self._get_type_label(commit_type)
        action_verb = self._get_action_verb(commit_type)

        # Adjust action verb based on change type for better semantics
        if change_type == 'added':
            if commit_type in ['start', 'progress', 'milestone', 'complete']:
                action_verb = 'add'  # Override for file additions
            else:
                action_verb = 'add'
        elif change_type == 'deleted':
            action_verb = 'remove'
        # For modified, keep the type-specific action verb

        return f"{type_label}: {action_verb} {file_desc}"

    def _categorize_changes_by_type(self, changes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Categorize changes by commit type based on file paths and content
        """
        categorized = {commit_type: [] for commit_type in self.commit_types.keys()}
        categorized['add'] = []  # For pure additions
        categorized['update'] = []  # For pure modifications
        categorized['remove'] = []  # For deletions

        for change_type, files in changes.items():
            for file_path in files:
                commit_type = self._detect_commit_type(file_path, change_type)
                categorized[commit_type].append(file_path)

        return categorized

    def _detect_commit_type(self, file_path: str, change_type: str) -> str:
        """
        Detect the commit type based on file path, name, content patterns, and progress indicators
        """
        path_lower = file_path.lower()
        filename_lower = Path(file_path).name.lower()

        # Check for progress indicators in filename or path
        for progress_label, keywords in self.progress_patterns.items():
            if any(keyword in filename_lower for keyword in keywords) or any(keyword in path_lower for keyword in keywords):
                return 'progress'

        # Check filename patterns first (more specific) - avoid conflicts with progress patterns
        if any(pattern in filename_lower for pattern in ['start', 'begin', 'init']) and 'create' not in filename_lower:
            return 'start'
        if any(pattern in filename_lower for pattern in ['milestone', 'checkpoint', 'phase', 'stage', 'step']):
            return 'milestone'
        if any(pattern in filename_lower for pattern in ['complete', 'finish', 'done', 'end', 'final']) and 'percent' not in filename_lower:
            return 'complete'
        if any(pattern in filename_lower for pattern in ['deploy', 'release', 'publish', 'launch', 'production']):
            return 'deploy'
        if any(pattern in filename_lower for pattern in ['review', 'feedback', 'qa', 'validate', 'check']):
            return 'review'

        # Existing detection logic
        if any(pattern in filename_lower for pattern in ['test', 'spec', '_test', 'test_']):
            return 'test'
        elif any(pattern in filename_lower for pattern in ['readme', 'changelog', 'history']):
            return 'docs'
        elif any(pattern in filename_lower for pattern in ['setup', 'install', 'makefile']):
            return 'chore'
        elif any(pattern in filename_lower for pattern in ['config', 'settings', 'env']):
            return 'chore'
        elif any(pattern in filename_lower for pattern in ['security', 'auth', 'login', 'encrypt']):
            return 'security'
        elif any(pattern in filename_lower for pattern in ['fix', 'bug', 'issue', 'error']):
            return 'fix'
        elif any(pattern in filename_lower for pattern in ['feature', 'feat', 'new']):
            return 'feat'
        elif any(pattern in filename_lower for pattern in ['refactor', 'cleanup']):
            return 'refactor'
        elif any(pattern in filename_lower for pattern in ['style', 'format', 'lint']):
            return 'style'
        elif any(pattern in filename_lower for pattern in ['perf', 'performance', 'speed', 'optimize']):
            return 'perf'
        elif any(pattern in filename_lower for pattern in ['revert', 'rollback']):
            return 'revert'

        # Check directory path patterns
        if any(pattern in path_lower for pattern in ['/test', '/tests', '/spec', '/specs']):
            return 'test'
        elif any(pattern in path_lower for pattern in ['/doc', '/docs', '/documentation']):
            return 'docs'
        elif any(pattern in path_lower for pattern in ['/config', '/configs', '/build']):
            return 'chore'
        elif any(pattern in path_lower for pattern in ['/security', '/auth', '/authentication']):
            return 'security'
        elif any(pattern in path_lower for pattern in ['/feature', '/features', '/new']):
            return 'feat'
        elif any(pattern in path_lower for pattern in ['/fix', '/fixes', '/bug']):
            return 'fix'

        # Check file extension patterns
        file_ext = Path(file_path).suffix.lower()
        if file_ext in ['.md', '.txt', '.rst', '.adoc']:
            return 'docs'
        elif file_ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
            return 'chore'

        # Check file content for keywords (if file exists and is readable)
        try:
            full_path = self.project_path / file_path
            if full_path.exists() and full_path.is_file():
                content = full_path.read_text().lower()

                # Prioritize specific types over progress for content detection
                priority_types = ['complete', 'deploy', 'review', 'start', 'milestone']
                for commit_type in priority_types:
                    if commit_type in self.commit_types and any(pattern in content for pattern in self.commit_types[commit_type]):
                        return commit_type

                # Then check other types
                for commit_type, patterns in self.commit_types.items():
                    if commit_type not in priority_types and any(pattern in content for pattern in patterns):
                        return commit_type
        except:
            pass  # If we can't read the file, continue with fallback

        # Default to basic change types
        if change_type == 'added':
            return 'add'
        elif change_type == 'deleted':
            return 'remove'
        else:
            return 'update'

    def _generate_typed_message(self, commit_type: str, files: List[str]) -> str:
        """
        Generate a commit message for a specific type of changes
        """
        type_label = self._get_type_label(commit_type)

        if len(files) == 1:
            file_desc = self._get_file_description(files[0])
            action = self._get_action_verb(commit_type)
            return f"{type_label}: {action} {file_desc}"
        else:
            count = len(files)
            return f"{type_label}: {self._get_plural_action(commit_type)} {count} files"

    def _get_type_label(self, commit_type: str) -> str:
        """
        Get the progress-oriented commit type label
        """
        type_labels = {
            'start': '🚀 START',
            'progress': '📈 PROGRESS',
            'milestone': '🎯 MILESTONE',
            'complete': '✅ COMPLETE',
            'fix': '🐛 FIX',
            'refactor': '🔄 REFACTOR',
            'docs': '📚 DOCS',
            'test': '🧪 TEST',
            'deploy': '🚀 DEPLOY',
            'review': '👀 REVIEW',
            'add': '➕ ADD',
            'update': '📝 UPDATE',
            'remove': '🗑️ REMOVE'
        }
        return type_labels.get(commit_type, commit_type.upper())

    def _get_action_verb(self, commit_type: str) -> str:
        """
        Get the appropriate action verb for the progress-oriented commit type
        """
        action_verbs = {
            'start': 'begin',
            'progress': 'continue',
            'milestone': 'reach',
            'complete': 'finish',
            'fix': 'fix',
            'refactor': 'refactor',
            'docs': 'update',
            'test': 'add',
            'deploy': 'deploy',
            'review': 'review',
            'add': 'add',
            'update': 'update',
            'remove': 'remove'
        }
        return action_verbs.get(commit_type, 'update')

    def _get_plural_action(self, commit_type: str) -> str:
        """
        Get the plural action for multiple files with progress indicators
        """
        plural_actions = {
            'start': 'begin',
            'progress': 'continue',
            'milestone': 'reach',
            'complete': 'finish',
            'fix': 'fix',
            'refactor': 'refactor',
            'docs': 'update',
            'test': 'add',
            'deploy': 'deploy',
            'review': 'review',
            'add': 'add',
            'update': 'update',
            'remove': 'remove'
        }
        return plural_actions.get(commit_type, 'update')
