from __future__ import annotations

"""Schritte für Python-Version, virtuelle Umgebung und pip-Konfiguration."""

import platform as _platform
import subprocess
import sys
from pathlib import Path
from typing import Tuple

from tools.setup.config import BootstrapConfig, PlatformInfo
from tools.ui import SetupConsole


def get_platform_info(config: BootstrapConfig) -> PlatformInfo:
    """Ermittelt Interpreter-Pfad und Aktivierungsbefehl für das venv."""
    system = _platform.system()
    if system == "Windows":
        bin_dir = config.venv_dir / PlatformInfo.VENV_BIN_DIR_WINDOWS
        python_venv = str(bin_dir / "python.exe")
        activate_cmd = f"{config.venv_dir}\\Scripts\\activate"
    else:
        bin_dir = config.venv_dir / PlatformInfo.VENV_BIN_DIR_UNIX
        python_venv = str(bin_dir / "python")
        activate_cmd = f"source {config.venv_dir}/bin/activate"

    return PlatformInfo(system=system, python_venv=python_venv, activate_cmd=activate_cmd)


def check_python_version(min_version: Tuple[int, int] | None) -> bool:
    """Prüft, ob die aktuelle Python-Version zur Vorgabe passt."""
    if min_version is None:
        SetupConsole.info("Keine minimale Python-Version in pyproject.toml angegeben.")
        return True

    current = sys.version_info
    required_str = f"{min_version[0]}.{min_version[1]}"
    SetupConsole.info(f"Python-Anforderung aus pyproject.toml: >= {required_str}")
    if (current.major, current.minor) < min_version:
        SetupConsole.error(
            f"Aktuelle Python-Version {current.major}.{current.minor} ist zu niedrig.",
        )
        return False

    SetupConsole.success("Python-Version erfüllt die Vorgabe.")
    return True


def create_virtualenv(config: BootstrapConfig) -> bool:
    """Erstellt ein neues virtuelles Environment."""
    if config.venv_dir.exists():
        SetupConsole.info(f"Virtuelle Umgebung existiert bereits: {config.venv_dir}")
        return True

    SetupConsole.info(f"Erzeuge virtuelles Environment unter {config.venv_dir} ...")
    try:
        subprocess.run(
            [config.python_sys, "-m", "venv", str(config.venv_dir)],
            check=True,
        )
        SetupConsole.success("Virtuelle Umgebung erfolgreich erstellt.")
        return True
    except subprocess.CalledProcessError as exc:
        SetupConsole.error(f"Erstellen des virtuellen Environments fehlgeschlagen: {exc}")
        return False


def update_pip(platform_info: PlatformInfo) -> bool:
    """Aktualisiert pip im virtuellen Environment."""
    SetupConsole.info("Aktualisiere pip im virtuellen Environment ...")
    try:
        subprocess.run(
            [platform_info.python_venv, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
        )
        SetupConsole.success("pip wurde aktualisiert.")
        return True
    except subprocess.CalledProcessError as exc:
        SetupConsole.error(f"pip-Update fehlgeschlagen: {exc}")
        return False


def configure_pip_index(platform_info: PlatformInfo) -> bool:
    """Setzt den Standard-PyPI-Index. Fehler sind nicht fatal."""
    SetupConsole.fix("Konfiguriere pip Index (https://pypi.org/simple) ...")
    try:
        subprocess.run(
            [
                platform_info.python_venv,
                "-m",
                "pip",
                "config",
                "set",
                "global.index-url",
                "https://pypi.org/simple",
            ],
            check=False,
            capture_output=True,
        )
        SetupConsole.success("PyPI Index konfiguriert.")
    except Exception as exc:  # noqa: BLE001
        SetupConsole.warning(f"Konnte pip Index nicht konfigurieren: {exc}")
    return True


def check_pyqt5_macos(platform_info: PlatformInfo) -> bool:
    """Führt einen einfachen PyQt5-Importtest unter macOS durch."""
    if platform_info.system != "Darwin":
        return True

    SetupConsole.info("🍎 Prüfe macOS PyQt5-Kompatibilität ...")
    try:
        subprocess.run(
            [
                platform_info.python_venv,
                "-c",
                "import PyQt5; from PyQt5.QtWidgets import QApplication; print('OK')",
            ],
            check=True,
            capture_output=True,
        )
        SetupConsole.success("PyQt5 scheint unter macOS funktionsfähig zu sein.")
        return True
    except subprocess.CalledProcessError as exc:
        SetupConsole.warning(f"PyQt5-Test unter macOS fehlgeschlagen: {exc}")
        return False
