import psutil
import os
from pathlib import Path
from typing import List

class ProjectMonitor:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.editor_processes = [
            'code', 'vscode', 'atom', 'sublime_text', 'vim', 'nvim',
            'emacs', 'nano', 'gedit', 'kate', 'notepad++', 'pycharm',
            'intellij', 'eclipse', 'visualstudio'
        ]

    def is_project_open(self) -> bool:
        """Check if the project is currently open in an editor"""
        try:
            processes = self.get_editor_processes()
            for proc in processes:
                try:
                    # Check if the process has the project path in its command line
                    cmdline = proc.cmdline()
                    if any(str(self.project_path) in arg for arg in cmdline):
                        return True
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
            return False
        except Exception as e:
            print(f"Error checking project status: {e}")
            return False

    def get_editor_processes(self) -> List[psutil.Process]:
        """Get list of running editor processes"""
        editors = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if self._is_editor_process(proc):
                        editors.append(proc)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        except Exception as e:
            print(f"Error getting editor processes: {e}")
        return editors

    def _is_editor_process(self, proc: psutil.Process) -> bool:
        """Check if a process is an editor"""
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            cmdline = proc.info['cmdline'] if proc.info['cmdline'] else []

            # Check process name
            for editor in self.editor_processes:
                if editor in name:
                    return True

            # Check command line for editor names
            cmdline_str = ' '.join(cmdline).lower()
            for editor in self.editor_processes:
                if editor in cmdline_str:
                    return True

            return False
        except Exception:
            return False
