from __future__ import annotations

"""Bootstrap-Logik für das Setup der UFO-Simulation.

Verantwortlichkeiten:
- Python-Version prüfen
- virtuelle Umgebung anlegen
- Runtime- und Dev-Abhängigkeiten installieren
- Import-Linter ausführen
- pytest-Tests starten und Ergebnis auswerten
"""

import subprocess
import sys
import time
import re
from collections.abc import Mapping, Sequence
from typing import Final
from venv import create as venv_create

from tools.analysis.imports import run_import_linter
from tools.common import ErrorLog
from tools.setup.config import BootstrapConfig
from tools.setup.profile import PyProjectProfile, load_pyproject_profile
from tools.ui import SetupConsole, StepProgress
from tools.ui.resources import TextCatalog

_TEXTS: Final[TextCatalog] = TextCatalog()
PYTEST_MODULE: Final[str] = "pytest"
PYTEST_SUMMARY_TOKEN: Final[str] = " passed "
PYTEST_TIME_TOKEN: Final[str] = " in "

# dezente Standardpausen für eine flüssige, professionelle Ausgabe
PAUSE_VERY_SHORT: Final[float] = 0.25
PAUSE_SHORT: Final[float] = 0.50
PAUSE_MEDIUM: Final[float] = 0.75


def _pause(seconds: float) -> None:
    """Zentrale Wartefunktion für eine sanfte, konsistente Ausgabe."""
    if seconds > 0:
        time.sleep(seconds)


def _check_python_version(profile: PyProjectProfile) -> bool:
    """Prüft, ob die laufende Python-Version die Mindestanforderung erfüllt."""
    required = profile.requires_min_python
    if required is None:
        return True

    major, minor = required
    if sys.version_info[:2] >= (major, minor):
        return True

    SetupConsole.error(
        f"Python {major}.{minor} oder neuer erforderlich, gefunden: "
            f"{sys.version_info.major}.{sys.version_info.minor}",
    )
    return False


def _create_venv(config: BootstrapConfig) -> bool:
    """Erzeugt das virtuelle Environment, falls noch nicht vorhanden."""
    if config.venv_dir.exists():
        SetupConsole.info(f"Virtuelle Umgebung existiert bereits: {config.venv_dir}")
        return True

    SetupConsole.info(f"Erzeuge virtuelle Umgebung in {config.venv_dir} ...")
    venv_create(config.venv_dir, with_pip=True)
    return True


def _run_command(
        args: Sequence[str],
        *,
        cwd: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Führt einen einfachen Subprozess mit Textausgabe aus (kein Exception-Throw)."""
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _short_output(output: str, *, max_lines: int = 10) -> str:
    """Begrenzt Ausgaben auf die ersten max_lines Zeilen."""
    stripped = output.strip()
    if not stripped:
        return ""
    lines = stripped.splitlines()
    if len(lines) <= max_lines:
        return stripped
    return "\n".join(lines[:max_lines])


def _install_requirements_batch(
        python_venv: str,
        requirements: Mapping[str, str],
        category_name: str,
        success_message: str,
        log: ErrorLog,
) -> bool:
    """Installiert eine Gruppe von Requirements mit Progress-Bar."""
    total = len(requirements)
    if total == 0:
        SetupConsole.warning(f"Keine {category_name}-Pakete gefunden.")
        return True

    SetupConsole.info(f"Pakete werden geladen... ({category_name}, {total} Einträge)")

    installed = 0
    with StepProgress(f"{category_name}-Installation", total=total) as progress:
        for name, version_spec in requirements.items():
            spec = f"{name}{version_spec}"
            progress.set_status(f"Paket: {name}")

            result = _run_command(
                (python_venv, "-m", "pip", "install", spec, "--progress-bar", "off"),
            )

            if result.returncode == 0:
                installed += 1
                progress.advance()
                continue

            SetupConsole.error(f"Fehler bei der Installation von {spec}")
            short = _short_output(result.stderr or result.stdout or "")
            if short:
                SetupConsole.info(short)

            log.write_error(
                f"{category_name} Installation: {spec}",
                f"Fehler beim Installieren von {spec}",
                details=(result.stdout or "") + (result.stderr or ""),
            )
            return False

    SetupConsole.success(f"{success_message.strip()} ({installed}/{total})\n")
    return True


def _install_all_dependencies(
        config: BootstrapConfig,
        profile: PyProjectProfile,
        log: ErrorLog,
) -> bool:
    """Installiert Runtime- und Dev-Abhängigkeiten."""
    python_venv = config.venv_python

    if not _install_requirements_batch(
            python_venv,
            profile.runtime_requirements,
            "Runtime-Dependencies",
            "Runtime-Dependencies installiert",
            log,
    ):
        return False

    if not profile.dev_requirements:
        return True

    return _install_requirements_batch(
        python_venv,
        profile.dev_requirements,
        "Dev-Dependencies",
        "Dev-Dependencies installiert",
        log,
    )


def _run_import_checks(
        config: BootstrapConfig,
        profile: PyProjectProfile,
        log: ErrorLog,
) -> bool:
    """Führt Import-Linter aus, falls im Profil aktiviert."""
    if not profile.uses_import_linter:
        return True

    SetupConsole.info("Starte Import-Prüfung (import-linter)...")

    ok, output = run_import_linter(config.venv_python, config.repo_root)

    if ok:
        SetupConsole.info(_TEXTS.text("import_linter", field="success"))
        return True

    SetupConsole.error(_TEXTS.text("import_linter", field="failed"))

    text_lower = output.lower()
    if "no module named" in text_lower and "importlinter" in text_lower:
        human = (
            "Import-Linter ist installiert, aber das CLI-Modul konnte nicht "
            "korrekt ausgeführt werden (fehlende __main__-Konfiguration)."
        )
    else:
        human = (
            "Import-Linter hat entweder Contract-Verstöße gemeldet oder ist "
            "mit einem Fehler beendet worden."
        )

    SetupConsole.info(human)

    short = _short_output(output)
    if short:
        SetupConsole.info(short)

    log.write_error(
        "Import-Linter",
        human,
        output or "keine Ausgabe von Import-Linter",
    )
    return False


def _detect_pytest_summary(output: str) -> str:
    """Extrahiert die pytest-Zusammenfassung aus der Ausgabe, falls vorhanden."""
    for line in reversed(output.splitlines()):
        if PYTEST_SUMMARY_TOKEN in line and PYTEST_TIME_TOKEN in line:
            return line.strip()
    return ""


def _run_tests(config: BootstrapConfig, log: ErrorLog) -> bool:
    """Führt pytest mit kompakter Ausgabe, Progress-Bar und dynamischem Status aus."""
    python_venv = config.venv_python
    project_root = config.repo_root

    SetupConsole.subheader("Tests ausführen (Validierung der Installation)")

    # 1) pytest-Version prüfen
    version_result = _run_command(
        (python_venv, "-m", PYTEST_MODULE, "--version"),
    )
    if version_result.returncode != 0:
        SetupConsole.error("pytest konnte nicht gestartet werden – überspringe Tests.")
        log.write_error(
            "pytest",
            "pytest konnte nicht gestartet werden",
            version_result.stdout or version_result.stderr or "",
        )
        return False

    SetupConsole.info(f"pytest Version: {version_result.stdout.strip()}\n")

    # 2) eigentlicher Testlauf mit Live-Streaming
    cmd = (python_venv, "-m", PYTEST_MODULE)
    stdout_lines: list[str] = []

    # total=0 -> indeterministischer Balken (roter Spinner)
    with StepProgress("pytest-Testlauf", total=0) as progress:
        progress.set_status("Tests werden ausgeführt...")

        proc = subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        assert proc.stdout is not None
        for line in proc.stdout:
            stdout_lines.append(line)
            stripped = line.strip()
            if not stripped:
                continue

            # Testnamen erkennen und als Status setzen
            if stripped.startswith("tests/") and "::" in stripped:
                first_token = stripped.split(" ", 1)[0]
                parts = first_token.split("::")
                func_name = parts[-1]
                progress.set_status(func_name)

        returncode = proc.wait()

        # Abschluss-Status für den Progressbalken (ohne pytest-'===='-Zeilen)
        if returncode == 0:
            progress.set_status("Tests erfolgreich abgeschlossen.")
            # __exit__ ruft mark_finished() -> grauer OK-Balken
        else:
            progress.set_status("pytest-Fehler – Details siehe setup.log.")
            progress.mark_failed()

    stdout = "".join(stdout_lines)
    output = stdout

    if returncode == 0:
        nice_summary = _format_pytest_summary(stdout)

        if nice_summary:
            # kompakte, einzeilige Zusammenfassung
            SetupConsole.success(f"Tests erfolgreich: {nice_summary}")
        else:
            SetupConsole.success("Tests erfolgreich abgeschlossen.")

        log.write_error(
            "pytest",
            "Testlauf erfolgreich (Details)",
            output or "pytest lieferte keine Ausgabe.",
        )
        return True

    SetupConsole.error("pytest hat Fehler gemeldet. Details siehe setup.log.")

    short = _short_output(output)
    if short:
        SetupConsole.info(short)

    log.write_error(
        "pytest",
        "Testlauf fehlgeschlagen",
        output or "pytest lieferte keine Ausgabe.",
    )
    return False


def _format_pytest_summary(output: str) -> str | None:
    """Formatiert die pytest-Zusammenfassung ohne '====' sauber für die Ausgabe."""
    line = _detect_pytest_summary(output)
    if not line:
        return None

    match = re.search(r"(\d+)\s+passed\s+in\s+([\d\.]+)s", line)
    if not match:
        # Fallback: original Zeile ohne weitere Aufbereitung
        return line

    count, seconds = match.groups()
    return f"{count} Tests in {seconds}s"


def _get_activate_command(config: BootstrapConfig) -> str:
    """Gibt den passenden Aktivierungsbefehl für das Virtualenv zurück."""
    # Falls du später den Pfad in BootstrapConfig parametrisieren willst,
    # kannst du hier aus config.venv_dir ableiten.
    if sys.platform.startswith("win"):
        # PowerShell-Variante
        return r".\.venv\Scripts\Activate.ps1"
    # macOS / Linux
    return "source .venv/bin/activate"


def _print_next_steps(config: BootstrapConfig) -> None:
    """Zeigt empfohlene Schritte nach erfolgreichem Bootstrap an (Next Steps)."""
    title = _TEXTS.text("next_steps", field="title")
    if title:
        # entspricht deinem print_header("🎉 Setup erfolgreich abgeschlossen!")
        SetupConsole.header(title)

    body = _TEXTS.format(
        "next_steps",
        activate_cmd=_get_activate_command(config),
    )
    # entspricht den vielen print()-Zeilen in deinem Beispiel
    SetupConsole.info(body)

def main(argv: list[str] | None = None) -> int:
    """Haupteinstieg für das Setup (wird von setup.py aufgerufen)."""
    args = list(sys.argv[1:] if argv is None else argv)
    skip_tests = "--skip-tests" in args

    if skip_tests:
        args.remove("--skip-tests")

    config = BootstrapConfig(skip_tests=skip_tests)
    profile = load_pyproject_profile()
    log = ErrorLog(config.log_path)

    # 1) Lizenz- / Projektkopf
    SetupConsole.from_resource("license_header")
    _pause(PAUSE_SHORT)

    # 2) Begrüßung und Überblick über den Setup-Ablauf
    SetupConsole.header(_TEXTS.text("setup_header", field="title"))
    SetupConsole.info(_TEXTS.text("setup_header", field="intro"))

    setup_body = _TEXTS.text("setup_header", field="body")
    if setup_body:
        _pause(PAUSE_VERY_SHORT)
        SetupConsole.info(setup_body)

    _pause(PAUSE_SHORT)

    # 3) Legende und Systeminformationen – optischer „Preflight-Check“
    SetupConsole.legend()
    _pause(PAUSE_VERY_SHORT)
    SetupConsole.info(f"Betriebssystem: {sys.platform}\n")

    _pause(PAUSE_MEDIUM)

    # 4) Technische Schritte des Setups

    # 4.1 Python-Version prüfen
    if not _check_python_version(profile):
        return 1

    _pause(PAUSE_VERY_SHORT)

    # 4.2 Virtuelle Umgebung erstellen oder wiederverwenden
    if not _create_venv(config):
        return 1

    _pause(PAUSE_VERY_SHORT)

    # 4.3 Abhängigkeiten installieren
    if not _install_all_dependencies(config, profile, log):
        SetupConsole.from_resource("troubleshooting")
        return 1

    _pause(PAUSE_VERY_SHORT)

    # 4.4 Import-Contracts prüfen
    if not _run_import_checks(config, profile, log):
        SetupConsole.from_resource("troubleshooting")
        return 1

    _pause(PAUSE_VERY_SHORT)

    # 4.5 Tests ausführen (falls aktiviert)
    if profile.uses_pytest and not config.skip_tests:
        if not _run_tests(config, log):
            SetupConsole.from_resource("troubleshooting")
            return 1
    elif profile.uses_pytest and config.skip_tests:
        SetupConsole.info(_TEXTS.text("tests", field="skipped_hint"))

    _pause(PAUSE_SHORT)

    # Nächste Schritte analog zur alten print_next_steps-Funktion
    _print_next_steps(config)
    return 0