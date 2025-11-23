from __future__ import annotations

"""Konfiguration und Plattforminformationen für das Setup."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(slots=True, frozen=True)
class BootstrapConfig:
    """Unveränderliche Konfiguration für den Bootstrap-Prozess."""

    repo_root: Path = Path.cwd()
    venv_dir: Path = Path(".venv")
    skip_tests: bool = False
    log_path: Path = Path("setup.log")

    @property
    def python_sys(self) -> str:
        """Pfad zum aktuell laufenden Python-Interpreter."""
        return sys.executable


@dataclass(slots=True, frozen=True)
class PlatformInfo:
    """Plattformspezifische Informationen für das Setup."""

    system: str
    python_venv: str
    activate_cmd: str

    VENV_BIN_DIR_UNIX: Final[str] = "bin"
    VENV_BIN_DIR_WINDOWS: Final[str] = "Scripts"
