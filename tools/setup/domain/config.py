# tools/setup/domain/config.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from sys import platform as _platform


class Platform(Enum):
    """Logische Plattformklasse für Venv-Layout (WINDOWS / POSIX)."""

    WINDOWS = "windows"
    POSIX = "posix"


def default_repo_root() -> Path:
    """Liefert die Projektwurzel relativ zu diesem Modul."""
    return Path(__file__).resolve().parents[3]


@dataclass(slots=True)
class BootstrapConfig:
    """
    Zentrale technische Konfiguration für das Setup.

    Beinhaltet:
    - Projektwurzel (repo_root)
    - abgeleitete Pfade/Kommandos (venv_dir, venv_python, log_path, activation_command)

    Projekt- / Step-spezifisches Verhalten (Step-Auswahl, Optionen etc.)
    wird ausschließlich über die pyproject.toml im PyProjectProfile konfiguriert.
    """

    repo_root: Path = field(default_factory=default_repo_root)

    @property
    def platform(self) -> Platform:
        """Ermittelt die logische Plattform (WINDOWS oder POSIX)."""
        normalized = _platform.lower()
        if normalized.startswith(("win", "msys", "cygwin")):
            return Platform.WINDOWS
        return Platform.POSIX

    @property
    def venv_dir(self) -> Path:
        """.venv-Verzeichnis unterhalb der Projektwurzel."""
        return self.repo_root / ".venv"

    @property
    def venv_python(self) -> str:
        """Pfad zur Python-Binary im Virtualenv."""
        rel = (
            "Scripts/python.exe"
            if self.platform is Platform.WINDOWS
            else "bin/python"
        )
        return str(self.venv_dir / rel)

    @property
    def log_path(self) -> Path:
        """Pfad zur Setup-Logdatei."""
        return self.repo_root / "setup.log"

    @property
    def activation_command(self) -> str:
        """Shell-Befehl zur Aktivierung der virtuellen Umgebung."""
        if self.platform is Platform.WINDOWS:
            return r".\.venv\Scripts\Activate.ps1"
        return "source .venv/bin/activate"
