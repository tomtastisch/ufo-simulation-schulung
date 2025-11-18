#!/usr/bin/env python3
"""Setup/Bootstrap-Skript für die UFO-Simulation (vormals setup.py)."""

from __future__ import annotations

import importlib.metadata as importlib_metadata
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


# --- CLI-Output helpers ----------------------------------------------------


def print_header(text: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_success(text: str) -> None:
    print(f"   ✅ {text}")


def print_error(text: str) -> None:
    print(f"   ❌ {text}")


def print_warning(text: str) -> None:
    print(f"   ⚠️  {text}")


def print_info(text: str) -> None:
    print(f"   ℹ️  {text}")


def print_fix(text: str) -> None:
    print(f"   🔧 {text}")


# --- Platform helpers ------------------------------------------------------


def get_platform_info() -> dict[str, str]:
    """Ermittelt Betriebssystemdaten sowie Aktivierungshinweise für das Virtualenv."""
    import platform

    system = platform.system()
    venv_dir = Path(".venv")
    if system == "Windows":
        python_venv = str(venv_dir / "Scripts" / "python.exe")
        activate_cmd = ".venv\\Scripts\\activate"
    else:
        python_venv = str(venv_dir / "bin" / "python")
        activate_cmd = "source .venv/bin/activate"

    return {
        "system": system,
        "python_venv": python_venv,
        "activate_cmd": activate_cmd,
    }


# --- pyproject + requirements parsing -------------------------------------


def parse_pyproject_toml() -> dict[str, Any]:
    """Liest pyproject.toml und liefert Versionsanforderungen sowie Metadaten."""
    print("📖 Lese pyproject.toml...")
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print_error("pyproject.toml nicht gefunden!")
        return {}

    try:
        with pyproject_file.open("rb") as fh:
            data = tomllib.load(fh)
        requires_python = data.get("project", {}).get("requires-python", ">=3.11")
        print_info(f"Python-Anforderung: {requires_python}")
        match = re.search(r"(\d+)\.(\d+)", requires_python)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            print_success(f"Erkannt: Python {major}.{minor}+\n")
            return {
                "requires_python": requires_python,
                "python_major": major,
                "python_minor": minor,
                "raw": data,
            }
    except Exception as exc:  # noqa: BLE001
        print_error(f"Fehler beim Parsen von pyproject.toml: {exc}")
    return {}


def read_dev_requirements_from_pyproject(pyproject_data: dict[str, Any]) -> dict[str, str]:
    """Extrahiert optionale Dev-Abhängigkeiten als Mapping von Name zu Versionsspezifikation."""
    dev_reqs: dict[str, str] = {}
    opt = pyproject_data.get("project", {}).get("optional-dependencies", {})
    dev_entries = opt.get("dev", [])
    if not dev_entries:
        return dev_reqs

    print("📖 Lese Dev-Dependencies aus pyproject.toml ([project.optional-dependencies].dev)...")
    pattern = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*(.*)$")
    for entry in dev_entries:
        line = entry.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        name = match.group(1)
        version_spec = match.group(2).strip()
        dev_reqs[name] = version_spec
        print_info(f"{name}{version_spec}")

    print_success(f"Dev-Dependencies gelesen: {len(dev_reqs)} Pakete\n")
    return dev_reqs


def parse_requirements() -> dict[str, str]:
    """Parst requirements.txt in ein Paket-zu-Versionsspezifikation-Mapping."""
    print("📖 Lese requirements.txt...")
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print_error("requirements.txt nicht gefunden!")
        return {}

    requirements: dict[str, str] = {}
    try:
        with req_file.open("r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                match = re.match(r"([A-Za-z0-9_.\-]+)(.*)", line)
                if match:
                    name = match.group(1)
                    version_spec = match.group(2).strip()
                    requirements[name] = version_spec
                    print_info(f"{name}{version_spec}")
    except Exception as exc:  # noqa: BLE001
        print_error(f"Fehler beim Parsen von requirements.txt: {exc}")
        return {}

    print_success(f"Requirements gelesen: {len(requirements)} Pakete\n")
    return requirements


# --- Python + venv ---------------------------------------------------------


def check_python_version(pyproject_info: dict[str, Any] | None) -> bool:
    """Prüft, ob der aktive Interpreter die geforderte Basisversion erfüllt."""
    if not pyproject_info:
        print_warning(
            "Konnte Python-Anforderung aus pyproject.toml nicht lesen – überspringe Versionstest.",
        )
        return True

    required = (int(pyproject_info.get("python_major", 3)), int(pyproject_info.get("python_minor", 11)))
    current = (sys.version_info.major, sys.version_info.minor)
    print("📋 Prüfe Python-Version...")
    print_info(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if current < required:
        print_error(
            f"Python {required[0]}.{required[1]}+ benötigt, aber {current[0]}.{current[1]} gefunden.",
        )
        return False

    print_success(
        f"Python {required[0]}.{required[1]}+ OK (Anforderung: {pyproject_info.get('requires_python')})\n",
    )
    return True


def create_virtualenv() -> bool:
    """Erstellt .venv, falls noch nicht vorhanden."""
    venv_dir = Path(".venv")
    if venv_dir.exists():
        print_success("Virtual Environment existiert bereits\n")
        return True

    print("📦 Erstelle Virtual Environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print_success("Virtual Environment erstellt\n")
        return True
    except subprocess.CalledProcessError as exc:  # noqa: TRY003
        print_error(f"Fehler beim Erstellen des Virtual Environment: {exc}")
        return False


def update_pip(platform_info: dict[str, str]) -> bool:
    """Aktualisiert pip, setuptools und wheel innerhalb des Virtualenv."""
    python_venv = platform_info["python_venv"]
    print("⬆️  Aktualisiere pip, setuptools und wheel...")
    try:
        subprocess.run([python_venv, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run(
            [python_venv, "-m", "pip", "install", "--upgrade", "setuptools>=66.1.0", "wheel"],
            check=True,
        )
        print_success("pip, setuptools und wheel aktualisiert\n")
        return True
    except subprocess.CalledProcessError as exc:  # noqa: TRY003
        print_error(f"Fehler beim Aktualisieren von pip/setuptools/wheel: {exc}")
        return False


def configure_pip_index(platform_info: dict[str, str]) -> None:
    """Setzt den Standard-PyPI-Index für reproduzierbare Installationen."""
    python_venv = platform_info["python_venv"]
    print_fix("Konfiguriere pip Index (behebt typische PyPI-Fehler)...")
    try:
        subprocess.run(
            [python_venv, "-m", "pip", "config", "set", "global.index-url", "https://pypi.org/simple"],
            check=False,
        )
        print_success("PyPI Index konfiguriert")
    except Exception as exc:  # noqa: BLE001
        print_warning(f"Konnte pip Index nicht konfigurieren: {exc}")
    print()


def check_pyqt5_macos(platform_info: dict[str, str]) -> None:
    """Führt einen kurzen PyQt5-Importtest unter macOS durch."""
    if platform_info["system"] != "Darwin":
        return

    python_venv = platform_info["python_venv"]
    print("🍎 Prüfe macOS PyQt5-Kompatibilität...")
    try:
        subprocess.run(
            [
                python_venv,
                "-c",
                "import PyQt5; from PyQt5.QtWidgets import QApplication; print('OK')",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print_success("PyQt5 funktioniert auf macOS")
    except subprocess.CalledProcessError as exc:  # noqa: TRY003
        print_warning(f"PyQt5-Test fehlgeschlagen: {exc}")
    print()


# --- Dependency installation ----------------------------------------------


def install_runtime_requirements(platform_info: dict[str, str]) -> bool:
    """Installiert Laufzeitabhängigkeiten aus requirements.txt."""
    python_venv = platform_info["python_venv"]
    print("📥 Installiere Runtime-Dependencies (aus requirements.txt)...")
    try:
        subprocess.run([python_venv, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("Alle Runtime-Dependencies installiert\n")
        return True
    except subprocess.CalledProcessError as exc:  # noqa: TRY003
        print_error(f"Fehler bei der Installation der Runtime-Dependencies: {exc}")
        return False


def install_dev_requirements(platform_info: dict[str, str], dev_requirements: dict[str, str]) -> bool:
    """Installiert optionale Entwicklungsabhängigkeiten sequenziell."""
    if not dev_requirements:
        return True

    python_venv = platform_info["python_venv"]
    print("📥 Installiere Dev-Dependencies (pytest, black, flake8, ...)...")
    try:
        for name, version_spec in dev_requirements.items():
            spec = f"{name}{version_spec}"
            print_info(f"Installiere {spec}...")
            subprocess.run([python_venv, "-m", "pip", "install", spec], check=True)
        print_success("Alle Dev-Dependencies installiert\n")
        return True
    except subprocess.CalledProcessError as exc:  # noqa: TRY003
        print_error(f"Fehler bei der Installation der Dev-Dependencies: {exc}")
        return False


def install_project_editable(platform_info: dict[str, str]) -> bool:
    """Registriert das Projekt mittels pip install -e . im Virtualenv."""
    python_venv = platform_info["python_venv"]
    print("📦 Installiere Projekt (Editable-Modus, -e .) im Virtual Environment...")
    try:
        subprocess.run([python_venv, "-m", "pip", "install", "-e", "."], check=True)
        print_success("Projekt als Editable installiert (core.* ist als Paket verfügbar)\n")
        return True
    except subprocess.CalledProcessError as exc:  # noqa: TRY003
        print_error(f"Fehler bei der Installation des Projekts (-e .): {exc}")
        return False


# --- Verification ----------------------------------------------------------


def verify_installation(
        runtime_requirements: dict[str, str],
        dev_requirements: dict[str, str],
) -> bool:
    """Überprüft installierte Pakete via importlib.metadata und ergänzt fehlende Komponenten."""
    failed: list[tuple[str, str, str]] = []

    def check_and_fix(scope: str, name: str, version_spec: str) -> None:
        display = f"{name}{version_spec}"
        try:
            installed_version = importlib_metadata.version(name)
            print_success(f"   ✅ [{scope}] {display} (installiert: {installed_version})")
            return
        except importlib_metadata.PackageNotFoundError:
            print_warning(f"   ⚠️  [{scope}] {display} - nicht gefunden, versuche Installation...")

        try:
            subprocess.run([sys.executable, "-m", "pip", "install", f"{name}{version_spec}"], check=True)
            installed_version = importlib_metadata.version(name)
            print_success(f"   ✅ [{scope}] {display} (nach Installation: {installed_version})")
        except (subprocess.CalledProcessError, importlib_metadata.PackageNotFoundError) as exc:
            print_error(f"   ❌ [{scope}] {display} - Installation fehlgeschlagen: {exc}")
            failed.append((scope, name, version_spec))

    print("✔️  Prüfe Installation (Runtime-Dependencies)...")
    for name, spec in runtime_requirements.items():
        check_and_fix("runtime", name, spec)

    if dev_requirements:
        print("\n✔️  Prüfe Installation (Dev-Dependencies)...")
        for name, spec in dev_requirements.items():
            check_and_fix("dev", name, spec)

    if failed:
        print("\n")
        print_error("   ❌ Folgende Pakete konnten nicht verifiziert werden:")
        for scope, name, spec in failed:
            print_error(f"      - [{scope}] {name}{spec}")
        return False
    print()
    return True


# --- Final instructions ----------------------------------------------------


def print_next_steps(platform_info: dict[str, str]) -> None:
    """Zeigt empfohlene Schritte nach erfolgreichem Bootstrap an."""
    print_header("🎉 Setup erfolgreich abgeschlossen!")
    print("📍 Nächste Schritte:\n")
    print("1️⃣  Aktiviere das Virtual Environment:")
    print(f"    {platform_info['activate_cmd']}\n")
    print("2️⃣  Starte die Demo (Simulation mit Demo-Autopilot):")
    print("    python -m core.simulation.ufo_main\n")
    print("3️⃣  Öffne die Autopilot-Aufgabe:")
    print("    src/task/autopilot/autopilot.py\n")
    print("    Implementiere die 3 Aufgaben:\n")
    print("    - takeoff()  - Startphase")
    print("    - cruise()   - Reiseflug")
    print("    - landing()  - Landephase\n")
    print("4️⃣  Setze USE_DEMO = False in der Klasse Autopilot (Attribut USE_DEMO)\n")
    print("5️⃣  Starte die Demo erneut und teste deinen Autopiloten!\n")
    print("Guten Flug! 🚀\n")


def print_troubleshooting() -> None:
    """Gibt allgemeine Hinweise zur Fehlerdiagnose aus."""
    print_header("🛠 Troubleshooting-Hinweise")
    print("Wenn Probleme auftreten:")
    print("1. Stelle sicher, dass du Python 3.11+ verwendest.")
    print("2. Lösche ggf. das .venv Verzeichnis und führe bootstrap_env.py erneut aus.")
    print("3. Prüfe deine Internetverbindung für pip-Installationen.")
    print("4. Falls weiterhin Fehler auftreten, prüfe die vollständige Fehlermeldung oben.")


# --- Entry point -----------------------------------------------------------


def main() -> int:
    print_header("🛸 UFO-Simulation Schulung - Setup")
    platform_info = get_platform_info()
    print_info(f"Betriebssystem: {platform_info['system']}\n")

    pyproject_info = parse_pyproject_toml()
    pyproject_raw = pyproject_info.get("raw", {}) if pyproject_info else {}
    runtime_requirements = parse_requirements()
    if not runtime_requirements:
        print_error("Keine Requirements gefunden!")
        return 1

    if not check_python_version(pyproject_info):
        return 1
    if not create_virtualenv():
        print_troubleshooting()
        return 1
    if not update_pip(platform_info):
        print_troubleshooting()
        return 1

    configure_pip_index(platform_info)
    check_pyqt5_macos(platform_info)

    if not install_runtime_requirements(platform_info):
        print_troubleshooting()
        return 1

    dev_requirements = read_dev_requirements_from_pyproject(pyproject_raw)
    if not install_dev_requirements(platform_info, dev_requirements):
        print_troubleshooting()
        return 1

    if not install_project_editable(platform_info):
        print_troubleshooting()
        return 1

    if not verify_installation(runtime_requirements, dev_requirements):
        print_troubleshooting()
        return 1

    print_next_steps(platform_info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
