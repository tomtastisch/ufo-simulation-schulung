from __future__ import annotations

"""Ausführung von pytest zur Validierung der Installation."""

import re
import subprocess

from tools.common import ErrorLog
from tools.setup.config import PlatformInfo
from tools.ui import SetupConsole, StepProgress

_TEST_SUMMARY_PATTERN = re.compile(
    r"(?P<passed>\d+)\s+passed.*?(?P<failed>\d+)\s+failed" r"|" r"(?P<passed_only>\d+)\s+passed",
    re.IGNORECASE,
)


def _extract_test_summary(stdout: str) -> str:
    """Extrahiert eine kompakte Testzusammenfassung aus der pytest-Ausgabe."""
    match = _TEST_SUMMARY_PATTERN.search(stdout)
    if not match:
        return "Keine zusammenfassende pytest-Ausgabe gefunden."

    if match.group("passed_only"):
        passed = int(match.group("passed_only"))
        return f"{passed} Tests erfolgreich bestanden."
    passed = int(match.group("passed") or 0)
    failed = int(match.group("failed") or 0)
    return f"{passed} Tests bestanden, {failed} fehlgeschlagen."


def run_tests(platform_info: PlatformInfo, log: ErrorLog) -> bool:
    """Führt pytest im virtuellen Environment aus und wertet die Ergebnisse aus."""
    python_venv = platform_info.python_venv
    SetupConsole.subheader("Tests ausführen (Validierung der Installation)")

    try:
        result = subprocess.run(
            [python_venv, "-m", "pytest"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        SetupConsole.error(f"pytest konnte nicht ausgeführt werden: {exc}")
        log.write_error(
            "Tests",
            "pytest konnte nicht gestartet werden",
            str(exc),
        )
        return False

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    with StepProgress("pytest-Ausführung", total=1) as sp:
        sp.advance(1)
        if result.returncode == 0:
            sp.mark_success()
        else:
            sp.mark_error()

    summary = _extract_test_summary(stdout)
    SetupConsole.info(f"Testzusammenfassung: {summary}")

    if result.returncode != 0:
        SetupConsole.error("Tests sind fehlgeschlagen.")
        log.write_error(
            "Tests",
            "pytest meldet mindestens einen fehlgeschlagenen Test",
            stdout + "\n" + stderr,
        )
        return False

    SetupConsole.success("Tests wurden erfolgreich ausgeführt.")
    return True
