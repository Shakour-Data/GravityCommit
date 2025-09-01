import os
import json
from pathlib import Path
from typing import List

class ConfigManager:
    CONFIG_FILENAME = ".autocommit"

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.config_path = self.project_path / self.CONFIG_FILENAME
        self.config = {}

    def set_interval(self, interval: int):
        self.config['interval'] = interval
        self._save_config()

    def get_interval(self) -> int:
        if not self.config:
            self._load_config()
        return self.config.get('interval', 10)  # default 10 minutes

    def set_manual_override_open(self, override: bool):
        self.config['manual_override_open'] = override
        self._save_config()

    def get_manual_override_open(self) -> bool:
        if not self.config:
            self._load_config()
        return self.config.get('manual_override_open', False)

    def set_additional_editor_processes(self, editors: List[str]):
        self.config['additional_editor_processes'] = editors
        self._save_config()

    def get_additional_editor_processes(self) -> List[str]:
        if not self.config:
            self._load_config()
        return self.config.get('additional_editor_processes', [])

    def set_custom_env_vars(self, env_vars: List[str]):
        self.config['custom_env_vars'] = env_vars
        self._save_config()

    def get_custom_env_vars(self) -> List[str]:
        if not self.config:
            self._load_config()
        return self.config.get('custom_env_vars', [])

    def remove_config(self):
        if self.config_path.exists():
            self.config_path.unlink()
            self.config = {}

    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
