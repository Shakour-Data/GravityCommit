import os
import json
from pathlib import Path

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
