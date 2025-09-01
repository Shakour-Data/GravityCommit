import psutil
import os
from pathlib import Path
from typing import List
from .config_manager import ConfigManager

class ProjectMonitor:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.config_manager = ConfigManager(project_path)
        self.editor_processes = [
            'code', 'vscode', 'atom', 'sublime_text', 'vim', 'nvim',
            'emacs', 'nano', 'gedit', 'kate', 'notepad++', 'pycharm',
            'intellij', 'eclipse', 'visualstudio', 'cursor', 'zed',
            'webstorm', 'phpstorm', 'rider', 'clion', 'goland',
            'datagrip', 'rubymine', 'appcode', 'xcode', 'androidstudio'
        ]

    def is_project_open(self) -> bool:
        """Check if the project is currently open in an editor"""
        try:
            # Check manual override from config
            if self.config_manager.config.get('manual_override_open', False):
                return True

            # First check for VSCode remote environment indicators
            if self._is_vscode_remote_connected():
                return True

            # Get all supported editors including additional ones
            all_editors = self.get_all_supported_editors()

            # Check if any project files are open by editor processes
            if self._are_project_files_open(all_editors):
                return True

            # Fallback to process-based detection
            processes = self.get_editor_processes()
            for proc in processes:
                try:
                    # Check if the process has the project path in its command line
                    cmdline = proc.cmdline()
                    if any(str(self.project_path) in arg for arg in cmdline):
                        return True

                    # Check if the process working directory is within the project
                    try:
                        cwd = proc.cwd()
                        if cwd and str(self.project_path) in str(cwd):
                            return True
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass

                    # Also check if process name or cmdline matches any editor in all_editors
                    name = proc.name().lower()
                    cmdline_str = ' '.join(cmdline).lower()
                    for editor in all_editors:
                        if editor in name or editor in cmdline_str:
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

    def get_all_supported_editors(self) -> List[str]:
        """Get list of all supported editor process names including additional ones"""
        additional_editors = self.config_manager.config.get('additional_editor_processes', [])
        return self.editor_processes + additional_editors

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

    def _are_project_files_open(self, editors: List[str]) -> bool:
        """Check if any project files are open by editor processes"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    name = proc.info['name'].lower() if proc.info['name'] else ''
                    if any(editor in name for editor in editors):
                        open_files = proc.info.get('open_files', [])
                        if open_files:
                            for file_info in open_files:
                                file_path = file_info.path
                                if str(self.project_path) in file_path:
                                    return True
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        except Exception as e:
            print(f"Error checking open files: {e}")
        return False

    def _is_vscode_remote_connected(self) -> bool:
        """Check if VSCode is connected in a remote environment"""
        import os

        # Check for VSCode remote environment variables
        vscode_indicators = [
            'VSCODE_IPC_HOOK_CLI',
            'TERM_PROGRAM=vscode',
            'CODESPACE_VSCODE_FOLDER'
        ]

        # Add custom environment variables from config
        custom_env_vars = self.config_manager.config.get('custom_env_vars', [])
        all_indicators = vscode_indicators + custom_env_vars

        for indicator in all_indicators:
            if '=' in indicator:
                env_name, expected_value = indicator.split('=', 1)
                if os.getenv(env_name) == expected_value:
                    return True
            else:
                if os.getenv(indicator):
                    return True

        return False
