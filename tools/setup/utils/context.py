from __future__ import annotations

import traceback

"""
Technische Hilfsfunktionen für den Setup-Prozess.

Dieses Modul bündelt generische Helfer wie Subprozess-Aufrufe und das
Kürzen langer Konsolen-Ausgaben.
"""

from dataclasses import dataclass
from collections.abc import Sequence
from typing import Final

import subprocess


@dataclass(slots=True, frozen=True)
class CommandResult:
    """Ergebnis eines Subprozess-Aufrufs."""

    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        """True, wenn der Prozess mit Exit-Code 0 beendet wurde."""
        return self.returncode == 0


DEFAULT_MAX_LINES: Final[int] = 10


def run_command(
        args: Sequence[str],
        *,
        cwd: str | None = None,
        timeout: float | None = None,
) -> CommandResult:
    """
    Führt einen Subprozess mit den gegebenen Argumenten aus.

    Args:
        args: Befehlsargumente, z. B. ("python", "-m", "pytest").
        cwd: Optionales Working-Directory.
        timeout: Optionaler Timeout in Sekunden.

    Returns:
        Ein CommandResult mit Exit-Code sowie stdout/stderr (immer als String).
    """
    completed = subprocess.run(
        tuple(args),
        cwd=cwd,
        timeout=timeout,
        check=False,
        text=True,
        capture_output=True,
    )

    return CommandResult(
        args=tuple(args),
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def short_output(output: str, *, max_lines: int = 40) -> str:
    """
    Begrenzt eine Ausgabe auf die ersten `max_lines` Zeilen.

    Leere oder whitespace-only Eingaben liefern einen leeren String.

    Args:
        output: Originale Ausgabe (z. B. pytest-Log).
        max_lines: Maximale Anzahl der zurückgegebenen Zeilen.

    Returns:
        Gekürzte Ausgabe oder ein leerer String bei leerem Input.
    """
    stripped: str = output.strip()
    result: str = ""

    if stripped:
        lines: list[str] = stripped.splitlines()
        line_count: int = len(lines)

        if line_count <= max_lines:
            result = stripped
        else:
            head: str = "\n".join(lines[:max_lines])
            remaining: int = line_count - max_lines
            result = f"{head}\n... ({remaining} weitere Zeilen ausgeblendet)"

    return result
