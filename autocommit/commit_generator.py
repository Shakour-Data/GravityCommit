import os
from pathlib import Path
from typing import List, Dict

class CommitGenerator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def generate_commit(self, changes: Dict[str, List[str]]) -> str:
        """
        Generate a professional commit message based on changes
        """
        if not changes:
            return "No changes detected"

        message_parts = []

        # Analyze changes by type
        if 'added' in changes and changes['added']:
            message_parts.append(self._generate_add_message(changes['added']))

        if 'modified' in changes and changes['modified']:
            message_parts.append(self._generate_modify_message(changes['modified']))

        if 'deleted' in changes and changes['deleted']:
            message_parts.append(self._generate_delete_message(changes['deleted']))

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
