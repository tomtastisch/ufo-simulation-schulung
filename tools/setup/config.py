from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class BootstrapConfig:
    """Konfiguration für das Projekt-Setup."""

    repo_root: Path = Path.cwd()
    venv_dir: Path = Path(".venv")
    skip_tests: bool = False
    log_path: Path = Path("setup.log")

    @property
    def python_sys(self) -> str:
        """Pfad zum aktuell laufenden System-Python-Interpreter."""
        return sys.executable

    @property
    def venv_python(self) -> str:
        """Pfad zum Python-Interpreter im virtuellen Environment."""
        if platform.system() == "Windows":
            return str(self.venv_dir / "Scripts" / "python.exe")
        return str(self.venv_dir / "bin" / "python")
