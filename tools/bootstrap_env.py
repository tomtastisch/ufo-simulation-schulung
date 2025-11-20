#!/usr/bin/env python3
"""Automatisiertes Setup-Skript mit Progress-Tracking und Error-Logging.

Dieses Skript führt alle notwendigen Setup-Schritte aus:
- Virtual Environment Erstellung
- Dependency-Installation (Runtime + Dev)
- Projekt-Installation (Editable Mode)
- Automatische Test-Validierung

Ausgabe wird minimiert durch Progress-Bars. Fehler werden in setup.log protokolliert.
Kann direkt ausgeführt werden oder via setup.py aufgerufen.

Siehe tools/__init__.py für vollständige Modul-Dokumentation.
"""

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


# --- Error Logging & Subprocess Helpers -----------------------------------

# Globales Flag um zu tracken ob dies der erste Fehler im aktuellen Setup ist
_first_error_in_setup = True


def extract_subprocess_error_details(exc: subprocess.CalledProcessError) -> str:
    """Extrahiert Fehlerdetails aus einer CalledProcessError.

    Args:
        exc: Die CalledProcessError Exception

    Returns:
        Formatierter String mit stdout und stderr
    """
    details = []

    if hasattr(exc, 'stdout') and exc.stdout:
        details.append(str(exc.stdout))

    if hasattr(exc, 'stderr') and exc.stderr:
        details.append(f"\nSTDERR:\n{exc.stderr}")

    return ''.join(details) if details else str(exc)


def get_error_message(exc: subprocess.CalledProcessError) -> str:
    """Gibt eine lesbare Fehlermeldung für Subprocess-Fehler zurück.

    Args:
        exc: Die CalledProcessError Exception

    Returns:
        Fehlermeldung (bevorzugt stderr, sonst Fallback)
    """
    if hasattr(exc, 'stderr') and exc.stderr:
        return str(exc.stderr)
    return str(exc)


def _extract_test_summary(stdout: str) -> str | None:
    """Extrahiert die Test-Zusammenfassung aus pytest stdout.

    Args:
        stdout: Die stdout-Ausgabe von pytest

    Returns:
        Zusammenfassungs-Zeile oder None
    """
    lines = stdout.strip().split("\n")
    for line in reversed(lines):
        if "passed" in line.lower():
            return line.strip()
    return None


def _extract_test_failure_summary(stdout: str) -> list[str]:
    """Extrahiert die Fehler-Zusammenfassung aus pytest stdout.

    Args:
        stdout: Die stdout-Ausgabe von pytest

    Returns:
        Liste der relevanten Zusammenfassungs-Zeilen
    """
    lines = stdout.strip().split("\n")
    summary_started = False
    summary_lines = []

    for line in lines:
        if "FAILED" in line or "ERROR" in line or "passed" in line.lower():
            summary_started = True
        if summary_started and line.strip():
            summary_lines.append(line)

    return summary_lines


def log_error_to_file(log_file: Path, section: str, error_info: str, details: str = "") -> None:
    """Schreibt Fehlerinformationen in die Log-Datei (nur bei Fehlern).

    Beim ersten Fehler wird die Datei neu erstellt (überschrieben falls vorhanden).
    Weitere Fehler im selben Setup-Durchlauf werden angehängt.

    Args:
        log_file: Pfad zur Log-Datei
        section: Name des Abschnitts (z.B. "Installation: PyQt5")
        error_info: Kurze Fehlerbeschreibung
        details: Detaillierte Ausgabe (stdout/stderr)
    """
    global _first_error_in_setup

    # Beim ersten Fehler: Datei neu erstellen (überschreiben)
    if _first_error_in_setup:
        log_file.write_text("# Setup Error Log\n# Nur Fehler werden hier protokolliert\n\n")
        _first_error_in_setup = False

    # Fehler anhängen (append)
    with log_file.open("a", encoding="utf-8") as log:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"\n{'=' * 70}\n")
        log.write(f"[{timestamp}] FEHLER: {section}\n")
        log.write(f"{'=' * 70}\n")
        log.write(f"{error_info}\n")
        if details:
            log.write(f"\nDetails:\n{details}\n")


# --- Progress Bar ---------------------------------------------------------


class ProgressBar:
    """Einfacher ASCII-Progress-Bar ohne externe Dependencies."""

    def __init__(self, total: int, width: int = 40, prefix: str = "") -> None:
        """Initialisiert den Progress-Bar.

        Args:
            total: Gesamtanzahl der Schritte
            width: Breite des Balkens in Zeichen
            prefix: Optional: Prefix-Text vor dem Balken
        """
        self.total = total
        self.width = width
        self.prefix = prefix
        self.current = 0
        self._last_line_length = 0

    def update(self, current: int, status: str = "") -> None:
        """Aktualisiert den Progress-Bar.

        Args:
            current: Aktueller Fortschritt (0 bis total)
            status: Statustext (z.B. aktuelles Paket)
        """
        self.current = min(current, self.total)
        percent = int((self.current / self.total) * 100) if self.total > 0 else 0
        filled = int((self.current / self.total) * self.width) if self.total > 0 else 0
        bar = "█" * filled + "░" * (self.width - filled)

        # Status-Text kürzen falls zu lang
        max_status_len = 40
        if len(status) > max_status_len:
            status = status[:max_status_len - 3] + "..."

        line = f"\r{self.prefix}[{bar}] {percent:3d}% {status}"

        # Überschreibe vorherige Zeile komplett
        if len(line) < self._last_line_length:
            line += " " * (self._last_line_length - len(line))
        self._last_line_length = len(line)

        print(line, end="", flush=True)

    def finish(self, final_status: str = "Fertig!") -> None:
        """Schließt den Progress-Bar ab."""
        self.update(self.total, final_status)
        print()  # Neue Zeile


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
        subprocess.run(
            [python_venv, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [python_venv, "-m", "pip", "install", "--upgrade", "setuptools>=66.1.0", "wheel", "--quiet"],
            check=True,
            capture_output=True,
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
            capture_output=True,
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


def install_runtime_requirements(platform_info: dict[str, str], requirements: dict[str, str]) -> bool:
    """Installiert Laufzeitabhängigkeiten aus requirements.txt mit Progress-Bar."""
    python_venv = platform_info["python_venv"]
    print("📥 Installiere Runtime-Dependencies (aus requirements.txt)...\n")

    if not requirements:
        print_warning("Keine Requirements gefunden!")
        return False

    log_file = Path("setup.log")
    total = len(requirements)
    progress = ProgressBar(total, prefix="   ")

    installed_count = 0
    for idx, (name, version_spec) in enumerate(requirements.items(), start=1):
        spec = f"{name}{version_spec}"
        progress.update(idx - 1, f"Installiere {name}...")

        try:
            subprocess.run(
                [python_venv, "-m", "pip", "install", spec, "--progress-bar", "off"],
                capture_output=True,
                text=True,
                check=True,
            )
            installed_count += 1

        except subprocess.CalledProcessError as exc:
            progress.finish(f"❌ Fehler bei {name}")
            print_error(f"Fehler bei der Installation von {spec}:")
            print(get_error_message(exc))

            # Nur bei Fehler in Log schreiben
            log_error_to_file(
                log_file,
                f"Runtime-Dependency Installation: {spec}",
                f"Fehler beim Installieren von {spec}",
                extract_subprocess_error_details(exc)
            )

            print_info(f"Fehlerdetails in {log_file} gespeichert")
            return False

    progress.finish(f"✓ {installed_count}/{total} Pakete installiert")
    print_success("Alle Runtime-Dependencies installiert\n")
    return True


def install_dev_requirements(platform_info: dict[str, str], dev_requirements: dict[str, str]) -> bool:
    """Installiert optionale Entwicklungsabhängigkeiten mit Progress-Bar."""
    if not dev_requirements:
        return True

    python_venv = platform_info["python_venv"]
    print("📥 Installiere Dev-Dependencies (pytest, black, flake8, ...)...\n")

    log_file = Path("setup.log")
    total = len(dev_requirements)
    progress = ProgressBar(total, prefix="   ")

    installed_count = 0
    for idx, (name, version_spec) in enumerate(dev_requirements.items(), start=1):
        spec = f"{name}{version_spec}"
        progress.update(idx - 1, f"Installiere {name}...")

        try:
            subprocess.run(
                [python_venv, "-m", "pip", "install", spec, "--progress-bar", "off"],
                capture_output=True,
                text=True,
                check=True,
            )
            installed_count += 1

        except subprocess.CalledProcessError as exc:
            progress.finish(f"❌ Fehler bei {name}")
            print_error(f"Fehler bei der Installation von {spec}:")
            print(get_error_message(exc))

            # Nur bei Fehler in Log schreiben
            log_error_to_file(
                log_file,
                f"Dev-Dependency Installation: {spec}",
                f"Fehler beim Installieren von {spec}",
                extract_subprocess_error_details(exc)
            )

            print_info(f"Fehlerdetails in {log_file} gespeichert")
            return False

    progress.finish(f"✓ {installed_count}/{total} Pakete installiert")
    print_success("Alle Dev-Dependencies installiert\n")
    return True


def install_project_editable(platform_info: dict[str, str]) -> bool:
    """Registriert das Projekt mittels pip install -e . im Virtualenv (mit Progress-Simulation)."""
    python_venv = platform_info["python_venv"]
    print("📦 Installiere Projekt (Editable-Modus, -e .) im Virtual Environment...\n")

    log_file = Path("setup.log")

    # Simuliere Progress während der Installation läuft
    import threading
    import time

    progress = ProgressBar(100, prefix="   ")
    install_done = threading.Event()
    install_error: subprocess.CalledProcessError | None = None

    def run_install() -> None:
        nonlocal install_error
        try:
            subprocess.run(
                [python_venv, "-m", "pip", "install", "-e", ".", "--progress-bar", "off"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            install_error = exc
        finally:
            install_done.set()

    # Starte Installation in Thread
    install_thread = threading.Thread(target=run_install)
    install_thread.start()

    # Simuliere Progress durch bekannte Phasen
    phases = [
        (20, "Prüfe Build-Backend..."),
        (40, "Ermittle Requirements..."),
        (60, "Erstelle Metadata..."),
        (80, "Installiere Package..."),
        (95, "Finalisiere Installation..."),
    ]

    for target, status in phases:
        while not install_done.is_set():
            for i in range(progress.current, min(target, 100)):
                if install_done.is_set():
                    break
                progress.update(i, status)
                time.sleep(0.05)
            if progress.current >= target or install_done.is_set():
                break

    # Warte auf Abschluss
    install_thread.join()

    # Nur bei Fehler in Log schreiben
    if install_error is not None:
        progress.finish("❌ Fehler bei Installation")
        print_error("Fehler bei der Installation des Projekts (-e .):")
        print(get_error_message(install_error))

        # Fehler in Log schreiben
        log_error_to_file(
            log_file,
            "Projekt-Installation (Editable Mode): -e .",
            "Fehler beim Installieren des Projekts",
            extract_subprocess_error_details(install_error)
        )

        print_info(f"Fehlerdetails in {log_file} gespeichert")
        return False

    progress.finish("✓ Projekt installiert")
    print_success("Projekt als Editable installiert (core.* ist als Paket verfügbar)\n")
    return True


# --- Verification ----------------------------------------------------------


def verify_installation(
        runtime_requirements: dict[str, str],
        dev_requirements: dict[str, str],
) -> bool:
    """Überprüft installierte Pakete via importlib.metadata und ergänzt fehlende Komponenten."""
    failed: list[tuple[str, str, str]] = []
    log_file = Path("setup.log")

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

            # Fehler in Log schreiben
            log_error_to_file(
                log_file,
                f"Verifikation: {scope} - {name}{version_spec}",
                f"Paket konnte nicht installiert/verifiziert werden",
                str(exc)
            )

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
        print_info(f"Details siehe {log_file}")
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


# --- Test execution --------------------------------------------------------


def run_tests(platform_info: dict[str, str]) -> bool:
    """Führt pytest aus um Installation zu validieren (mit Progress-Bar).

    Args:
        platform_info: Plattform-Informationen mit python_venv Pfad

    Returns:
        True wenn alle Tests erfolgreich waren, False sonst
    """
    python_venv = platform_info["python_venv"]
    print_header("🧪 Führe Tests aus (Validierung der Installation)")

    # Prüfe ob pytest verfügbar ist
    try:
        result = subprocess.run(
            [python_venv, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print_info(f"pytest Version: {result.stdout.strip()}\n")
    except subprocess.CalledProcessError:
        print_error("pytest nicht gefunden - überspringe Tests")
        return False

    # Führe Tests im Hintergrund aus und zeige Progress
    print("Starte Tests...\n")

    import threading
    import time

    tests_done = threading.Event()
    test_result: subprocess.CompletedProcess[str] | None = None
    test_error: Exception | None = None

    def run_pytest() -> None:
        nonlocal test_result, test_error
        try:
            test_result = subprocess.run(
                [python_venv, "-m", "pytest", "-v", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:
            test_error = exc
        finally:
            tests_done.set()

    # Starte Tests in Thread
    test_thread = threading.Thread(target=run_pytest)
    test_thread.start()

    # Simuliere Progress während Tests laufen
    progress = ProgressBar(100, prefix="   ")
    elapsed = 0
    while not tests_done.is_set():
        if elapsed < 90:
            elapsed = min(90, elapsed + 2)
        progress.update(elapsed, "Führe Tests aus...")
        time.sleep(0.1)

    # Warte auf Abschluss
    test_thread.join()

    log_file = Path("setup.log")

    # Error Handling
    if test_error is not None:
        progress.finish("❌ Fehler bei Test-Ausführung")
        print_error(f"Fehler beim Ausführen der Tests: {test_error}")

        log_error_to_file(
            log_file,
            "Test-Ausführung",
            "Exception beim Ausführen von pytest",
            str(test_error)
        )
        return False

    if test_result is None:
        progress.finish("❌ Keine Test-Ergebnisse")
        return False

    progress.finish("✓ Tests abgeschlossen")
    print()

    # Analysiere Ergebnis
    if test_result.returncode == 0:
        summary_line = _extract_test_summary(test_result.stdout)
        if summary_line:
            print_success(f"Alle Tests erfolgreich: {summary_line}")
        else:
            print_success("Alle Tests erfolgreich bestanden! ✓")
        print()
        return True

    # Tests fehlgeschlagen
    print_warning(f"Einige Tests sind fehlgeschlagen (Exit-Code: {test_result.returncode})")

    summary_lines = _extract_test_failure_summary(test_result.stdout)
    if summary_lines:
        print("\n📊 Test-Zusammenfassung:")
        for line in summary_lines[-5:]:
            print(f"   {line}")
    else:
        print_info("Details siehe pytest-Ausgabe (führe manuell aus: pytest -v)")

    # Fehler in Log schreiben
    log_error_to_file(
        log_file,
        "Test-Ausführung",
        f"Tests fehlgeschlagen (Exit-Code: {test_result.returncode})",
        test_result.stdout
    )

    print()
    print_warning("Tests fehlgeschlagen - bitte prüfe die Ausgabe oben.")
    print_info("Das Setup ist dennoch funktionsfähig, aber es könnten Probleme auftreten.")
    print_info(f"Vollständige Test-Ausgabe: pytest -v oder siehe {log_file}")
    print()
    return False


# --- Entry point -----------------------------------------------------------


def main() -> int:
    """Hauptfunktion für Setup/Bootstrap.

    Unterstützt folgende Kommandozeilen-Argumente:
        --skip-tests: Überspringt die Test-Ausführung nach Installation

    Hinweis: setup.log wird nur bei Fehlern erstellt/beschrieben.
    Bei jedem Setup-Durchlauf wird eine vorhandene setup.log überschrieben.
    """
    # Setze Error-Logging-Flag zurück für diesen Setup-Durchlauf
    global _first_error_in_setup
    _first_error_in_setup = True

    # Parse einfache CLI-Args
    skip_tests = "--skip-tests" in sys.argv

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

    # Übergebe requirements dict an install-Funktion
    if not install_runtime_requirements(platform_info, runtime_requirements):
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

    # Tests ausführen (falls nicht übersprungen)
    if not skip_tests:
        test_success = run_tests(platform_info)
        if not test_success:
            print_warning("Setup abgeschlossen, aber Tests sind fehlgeschlagen.")
            print_info("Du kannst das Projekt trotzdem verwenden, aber es könnten Probleme auftreten.\n")
    else:
        print_info("Tests übersprungen (--skip-tests Flag gesetzt)\n")

    print_next_steps(platform_info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
