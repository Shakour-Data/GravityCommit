import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Optional

class DaemonManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.system = platform.system().lower()
        self.service_name = f"autocommit-{self.project_path.name}"

    def install_service(self) -> bool:
        """Install the service based on the operating system"""
        if self.system == "linux":
            return self._install_linux_service()
        elif self.system == "windows":
            return self._install_windows_service()
        else:
            print(f"Unsupported operating system: {self.system}")
            return False

    def uninstall_service(self) -> bool:
        """Uninstall the service"""
        if self.system == "linux":
            return self._uninstall_linux_service()
        elif self.system == "windows":
            return self._uninstall_windows_service()
        else:
            print(f"Unsupported operating system: {self.system}")
            return False

    def is_running(self) -> bool:
        """Check if the service is running"""
        if self.system == "linux":
            return self._is_linux_service_running()
        elif self.system == "windows":
            return self._is_windows_service_running()
        return False

    def _install_linux_service(self) -> bool:
        """Install systemd service on Linux"""
        try:
            service_content = self._generate_systemd_service()
            service_path = Path("/etc/systemd/system") / f"{self.service_name}.service"

            # Write service file (requires sudo)
            with open(service_path, 'w') as f:
                f.write(service_content)

            # Reload systemd and enable service
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', self.service_name], check=True)
            subprocess.run(['sudo', 'systemctl', 'start', self.service_name], check=True)

            return True
        except Exception as e:
            print(f"Failed to install Linux service: {e}")
            return False

    def _uninstall_linux_service(self) -> bool:
        """Uninstall systemd service on Linux"""
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', self.service_name], check=False)
            subprocess.run(['sudo', 'systemctl', 'disable', self.service_name], check=False)

            service_path = Path("/etc/systemd/system") / f"{self.service_name}.service"
            if service_path.exists():
                service_path.unlink()

            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            return True
        except Exception as e:
            print(f"Failed to uninstall Linux service: {e}")
            return False

    def _is_linux_service_running(self) -> bool:
        """Check if systemd service is running"""
        try:
            result = subprocess.run(['systemctl', 'is-active', self.service_name],
                                  capture_output=True, text=True)
            return result.returncode == 0 and result.stdout.strip() == "active"
        except Exception:
            return False

    def _install_windows_service(self) -> bool:
        """Install Windows service"""
        try:
            # This would require pywin32 or similar
            # For now, return False as it's more complex
            print("Windows service installation not implemented yet")
            return False
        except Exception as e:
            print(f"Failed to install Windows service: {e}")
            return False

    def _uninstall_windows_service(self) -> bool:
        """Uninstall Windows service"""
        try:
            print("Windows service uninstallation not implemented yet")
            return False
        except Exception as e:
            print(f"Failed to uninstall Windows service: {e}")
            return False

    def _is_windows_service_running(self) -> bool:
        """Check if Windows service is running"""
        return False

    def _generate_systemd_service(self) -> str:
        """Generate systemd service file content"""
        python_path = shutil.which('python3') or shutil.which('python')
        if not python_path:
            raise RuntimeError("Python not found in PATH")

        script_path = Path(__file__).parent / "cli.py"

        return f"""[Unit]
Description=AutoCommit Service for {self.project_path.name}
After=network.target

[Service]
Type=simple
User={os.getlogin()}
WorkingDirectory={self.project_path}
ExecStart={python_path} {script_path} daemon {self.project_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
