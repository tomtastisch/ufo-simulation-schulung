from __future__ import annotations

import subprocess
import sys
from venv import create as venv_create

from tools.analysis.imports import run_import_linter
from tools.common import ErrorLog
from tools.setup.config import BootstrapConfig
from tools.setup.profile import PyProjectProfile, load_pyproject_profile
from tools.ui import SetupConsole, StepProgress
from tools.ui.resources import TextCatalog

_TEXTS = TextCatalog()


def _check_python_version(profile: PyProjectProfile) -> bool:
    """Prüft, ob die laufende Python-Version die Mindestanforderung erfüllt."""
    if profile.requires_min_python is None:
        return True
    major, minor = profile.requires_min_python
    if sys.version_info[:2] < (major, minor):
        SetupConsole.error(
            f"Python {major}.{minor} oder neuer erforderlich, gefunden: "
            f"{sys.version_info.major}.{sys.version_info.minor}",
        )
        return False
    return True


def _create_venv(config: BootstrapConfig) -> bool:
    """Erzeugt das virtuelle Environment, falls noch nicht vorhanden."""
    if config.venv_dir.exists():
        SetupConsole.info(f"Virtuelle Umgebung existiert bereits: {config.venv_dir}")
        return True

    SetupConsole.info(f"Erzeuge virtuelle Umgebung in {config.venv_dir} ...")
    venv_create(config.venv_dir, with_pip=True)
    return True


def _install_requirements_batch(
        python_venv: str,
        requirements: dict[str, str],
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

            try:
                subprocess.run(
                    [python_venv, "-m", "pip", "install", spec, "--progress-bar", "off"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                installed += 1
                progress.advance()
            except subprocess.CalledProcessError as exc:
                SetupConsole.error(f"Fehler bei der Installation von {spec}")
                msg = exc.stderr or exc.stdout or str(exc)
                if msg:
                    SetupConsole.info(msg)
                log.write_error(
                    f"{category_name} Installation: {spec}",
                    f"Fehler beim Installieren von {spec}",
                    details=(exc.stdout or "") + (exc.stderr or ""),
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


def _run_import_checks(config: BootstrapConfig, profile: PyProjectProfile, log: ErrorLog) -> bool:
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

    if output.strip():
        first_lines = "\n".join(output.strip().splitlines()[:10])
        SetupConsole.info(first_lines)

    log.write_error(
        "Import-Linter",
        human,
        output or "keine Ausgabe von Import-Linter",
    )
    return False


def _run_tests(config: BootstrapConfig, log: ErrorLog) -> bool:
    """Führt pytest mit kompakter Ausgabe, Progress-Bar und dynamischem Status aus."""
    python_venv = config.venv_python
    project_root = config.repo_root

    SetupConsole.subheader("Tests ausführen (Validierung der Installation)")

    try:
        result = subprocess.run(
            [python_venv, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        SetupConsole.info(f"pytest Version: {result.stdout.strip()}\n")
    except subprocess.CalledProcessError:
        SetupConsole.error("pytest konnte nicht gestartet werden – überspringe Tests.")
        log.write_error(
            "pytest",
            "pytest konnte nicht gestartet werden",
            "Aufruf von 'pytest --version' ist fehlgeschlagen.",
        )
        return False

    cmd = [python_venv, "-m", "pytest"]

    stdout_lines: list[str] = []

    from tools.ui import StepProgress  # falls nicht oben importiert

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

            if stripped.startswith("tests/") and "::" in stripped:
                first_token = stripped.split(" ", 1)[0]
                parts = first_token.split("::")

                # parts[0] = Pfad zur Testdatei
                # parts[1:-1] = ggf. Testklasse / Parametrisierungen
                # parts[-1] = eigentlicher Funktionsname
                func_name = parts[-1]
                progress.set_status(func_name)

        returncode = proc.wait()

    stdout = "".join(stdout_lines)
    output = stdout

    if returncode == 0:
        summary = ""
        for line in reversed(stdout.splitlines()):
            if " passed " in line and " in " in line:
                summary = line.strip()
                break

        if summary:
            SetupConsole.success(f"Tests erfolgreich: {summary}")
        else:
            SetupConsole.success("Tests erfolgreich abgeschlossen.")

        log.write_error(
            "pytest",
            "Testlauf erfolgreich (Details)",
            output or "pytest lieferte keine Ausgabe.",
        )
        return True

    SetupConsole.error("pytest hat Fehler gemeldet. Details siehe setup.log.")

    if output.strip():
        short = "\n".join(output.strip().splitlines()[:10])
        SetupConsole.info(short)

    log.write_error(
        "pytest",
        "Testlauf fehlgeschlagen",
        output or "pytest lieferte keine Ausgabe.",
    )
    return False


def main(argv: list[str] | None = None) -> int:
    """Haupteinstieg für das Setup (wird von setup.py aufgerufen)."""
    args = list(sys.argv[1:] if argv is None else argv)
    skip_tests = "--skip-tests" in args
    if skip_tests:
        args.remove("--skip-tests")

    config = BootstrapConfig(skip_tests=skip_tests)
    profile = load_pyproject_profile()
    log = ErrorLog(config.log_path)

    SetupConsole.header(_TEXTS.text("setup_header", field="title"))
    SetupConsole.info(_TEXTS.text("setup_header", field="intro"))
    SetupConsole.legend()
    SetupConsole.info(f"Betriebssystem: {sys.platform}\n")

    if not _check_python_version(profile):
        return 1

    if not _create_venv(config):
        return 1

    if not _install_all_dependencies(config, profile, log):
        SetupConsole.from_resource("troubleshooting")
        return 1

    if not _run_import_checks(config, profile, log):
        SetupConsole.from_resource("troubleshooting")
        return 1

    if profile.uses_pytest and not config.skip_tests:
        if not _run_tests(config, log):
            SetupConsole.from_resource("troubleshooting")
            return 1
    elif profile.uses_pytest and config.skip_tests:
        SetupConsole.info(_TEXTS.text("tests", field="skipped_hint"))

    SetupConsole.from_resource("next_steps")
    return 0