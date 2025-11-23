from __future__ import annotations

"""Installation und Verifikation der Projektabhängigkeiten."""

import importlib.metadata as importlib_metadata
import subprocess
import sys
from typing import Mapping

from tools.common import ErrorLog
from tools.setup.config import PlatformInfo
from tools.ui import SetupConsole


def _format_requirement(name: str, spec: str) -> str:
    return f"{name}{spec}" if spec else name


def install_runtime_requirements(
        platform_info: PlatformInfo,
        runtime_requirements: Mapping[str, str],
        log: ErrorLog,
) -> bool:
    """Installiert die Runtime-Dependencies im virtuellen Environment."""
    if not runtime_requirements:
        SetupConsole.info("Keine Runtime-Dependencies in pyproject.toml gefunden.")
        return True

    pkgs = [_format_requirement(n, s) for n, s in runtime_requirements.items()]
    SetupConsole.info("Installiere Runtime-Dependencies ...")
    try:
        subprocess.run(
            [platform_info.python_venv, "-m", "pip", "install", *pkgs],
            check=True,
        )
        SetupConsole.success("Runtime-Dependencies installiert.")
        return True
    except subprocess.CalledProcessError as exc:
        SetupConsole.error(f"Installation der Runtime-Dependencies fehlgeschlagen: {exc}")
        log.write_error(
            "Runtime-Dependencies",
            "Installation der Runtime-Dependencies fehlgeschlagen",
            str(exc),
        )
        return False


def install_dev_requirements(
        platform_info: PlatformInfo,
        dev_requirements: Mapping[str, str],
        log: ErrorLog,
) -> bool:
    """Installiert die Dev-Dependencies im virtuellen Environment."""
    if not dev_requirements:
        SetupConsole.info("Keine Dev-Dependencies in pyproject.toml gefunden.")
        return True

    pkgs = [_format_requirement(n, s) for n, s in dev_requirements.items()]
    SetupConsole.info("Installiere Dev-Dependencies ...")
    try:
        subprocess.run(
            [platform_info.python_venv, "-m", "pip", "install", *pkgs],
            check=True,
        )
        SetupConsole.success("Dev-Dependencies installiert.")
        return True
    except subprocess.CalledProcessError as exc:
        SetupConsole.error(f"Installation der Dev-Dependencies fehlgeschlagen: {exc}")
        log.write_error(
            "Dev-Dependencies",
            "Installation der Dev-Dependencies fehlgeschlagen",
            str(exc),
        )
        return False


def install_project_editable(platform_info: PlatformInfo, log: ErrorLog) -> bool:
    """Installiert das Projekt selbst im Editable-Modus."""
    SetupConsole.info("Installiere Projekt im Editable-Modus (-e .) ...")
    try:
        subprocess.run(
            [platform_info.python_venv, "-m", "pip", "install", "-e", "."],
            check=True,
        )
        SetupConsole.success("Projekt im Editable-Modus installiert.")
        return True
    except subprocess.CalledProcessError as exc:
        SetupConsole.error(f"Editable-Installation fehlgeschlagen: {exc}")
        log.write_error(
            "Editable-Installation",
            "Projekt konnte nicht im Editable-Modus installiert werden",
            str(exc),
        )
        return False


def verify_installation(
        runtime_requirements: Mapping[str, str],
        dev_requirements: Mapping[str, str],
        log: ErrorLog,
) -> bool:
    """Prüft installierte Pakete via importlib.metadata und ergänzt fehlende Pakete."""
    failed: list[tuple[str, str, str]] = []

    def check_and_fix(scope: str, name: str, version_spec: str) -> None:
        display = _format_requirement(name, version_spec)
        try:
            installed_version = importlib_metadata.version(name)
            SetupConsole.success(f"[{scope}] {display} (installiert: {installed_version})")
            return
        except importlib_metadata.PackageNotFoundError:
            SetupConsole.warning(
                f"[{scope}] {display} - nicht gefunden, versuche Installation ...",
            )

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", display],
                check=True,
            )
            installed_version = importlib_metadata.version(name)
            SetupConsole.success(
                f"[{scope}] {display} (nach Installation: {installed_version})",
            )
        except (subprocess.CalledProcessError, importlib_metadata.PackageNotFoundError) as exc:
            SetupConsole.error(f"[{scope}] {display} - Installation fehlgeschlagen: {exc}")
            failed.append((scope, name, version_spec))
            log.write_error(
                f"Verifikation: {scope} - {display}",
                "Paket konnte nicht installiert/verifiziert werden",
                str(exc),
            )

    SetupConsole.info("✔️  Prüfe Installation (Runtime-Dependencies) ...")
    for name, spec in runtime_requirements.items():
        check_and_fix("runtime", name, spec)

    if dev_requirements:
        SetupConsole.info("\n✔️  Prüfe Installation (Dev-Dependencies) ...")
        for name, spec in dev_requirements.items():
            check_and_fix("dev", name, spec)

    if failed:
        SetupConsole.error("Folgende Pakete konnten nicht verifiziert werden:")
        for scope, name, spec in failed:
            SetupConsole.error(f"  - [{scope}] {_format_requirement(name, spec)}")
        SetupConsole.info(f"Details siehe {log.path}")
        return False

    SetupConsole.info("Alle relevanten Pakete wurden erfolgreich verifiziert.")
    return True
