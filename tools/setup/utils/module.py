# tools/setup/utils/module.py
from __future__ import annotations

"""
Generische Hilfsfunktionen für Modul-/CLI-Prüfungen im Setup.

Enthält:
- evaluate  → `python -m <module> [args]` testweise ausführen
- classify  → Fehlerursache grob klassifizieren
- install   → generische Paketinstallation via `pip` oder externen Befehl
"""

import subprocess
from pathlib import Path
from typing import Final, Iterable, overload

from tools.setup.utils.context import run_command, short_output

_PIP_ARGS: Final[tuple[str, ...]] = ("-m", "pip", "install", "--progress-bar", "off")


def evaluate(
        python: str,
        module: str,
        *,
        cwd: Path | None = None,
        extra_args: tuple[str, ...] = ("--help",),
) -> tuple[bool, str, str | None]:
    """
    Führt einen minimalen Testlauf für `python -m <module> [extra_args]` aus.

    Rückgabe:
        ok       – True, wenn returncode == 0
        err   – kombinierte stdout/stderr-Ausgabe
        exc_info – Fehlermeldung, falls der Interpreter selbst nicht gestartet werden konnte
    """

    hold: tuple[bool, str, str | None]

    try:
        result = subprocess.run(
            (python, "-m", module, *extra_args),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        comb = (result.stdout or "") + (result.stderr or "")
        hold = (result.returncode == 0, comb, None)

    except (OSError, FileNotFoundError) as exc:
        # Interpreter (z. B. .venv/bin/python) nicht auffindbar
        hold = (False, "", str(exc))

    return hold


def classify(
        exc_info: str | None,
        output: str,
        *,
        module: str,
) -> tuple[str, str]:
    """
    Klassifiziert Fehler für einen Modulaufruf in (kind, details).

    kind    → "interpreter", "module_missing", "module_error"
    details → Text für Log & Ausgabe
    """
    text = (output or "").lower()

    match exc_info, text:
        case str() as e, _:
            return "interpreter", e
        case None, s if "no module named" in s and module in s:
            return "module_missing", output
        case _:
            return "module_error", output


@overload
def install(
        *,
        python: str,
        spec: str,
        cwd: Path | None = None,
) -> tuple[int, str, str]:
    """
    Installation via `python -m pip install <spec>`.
    """
    ...


@overload
def install(
        *,
        cmd: Iterable[str],
        cwd: Path | None = None,
) -> tuple[int, str, str]:
    """
    Generischer Installationsbefehl (z. B. Installer-Skript).
    """
    ...


def install(
        *,
        python: str | None = None,
        spec: str | None = None,
        cmd: Iterable[str] | None = None,
        cwd: Path | None = None,
) -> tuple[int, str, str]:
    """
    Installiert ein Paket oder führt einen generischen Installationsbefehl aus.

    Varianten:
        - python+spec → `python -m pip install <spec>`
        - cmd        → externer Befehl (z. B. Installer-Skript)

    Rückgabe:
        returncode
        raw_output   – stdout+stderr (vollständig)
        short_output – ggf. gekürzte Version für Konsolen-Anzeige
    """

    argv: tuple[str, ...] | None = None

    match python, spec, cmd:
        case str() as py, str() as s, None:
            argv: tuple[str, ...] = (py, *_PIP_ARGS, s)
        case None, None, external if external is not None:
            argv = tuple(external)
        case _:
            raise ValueError(
                "install(): entweder python+spec oder cmd angeben, nicht mehrere oder keine."
            )

    result = run_command(argv, cwd=cwd)

    raw = (result.stdout or "") + (result.stderr or "")
    short = short_output(raw)
    return result.returncode, raw, short
