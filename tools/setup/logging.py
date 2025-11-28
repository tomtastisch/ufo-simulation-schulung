"""
Fehlerprotokollierung für den Setup-Prozess.

Dieses Modul stellt eine schlanke `ErrorLog`-Klasse bereit, die Einträge
in eine Log-Datei des Setup-Prozesses schreibt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ErrorLog:
    """
    Einfache Fehlerprotokollierung in eine Textdatei.

    Die Klasse kapselt die I/O-Logik und wird von den Setup-Schritten
    genutzt, um technische Details konsistent zu protokollieren.
    """

    path: Path = field()

    def write_error(self, section: str, message: str, details: str | None = None) -> None:
        """
        Schreibt einen Fehlerabschnitt in die Log-Datei.

        Parameter:
            section:
                Grober Kontext des Fehlers (z. B. 'pytest', 'Import-Linter').
            message:
                Kurzbeschreibung des Fehlers.
            details:
                Optionaler, ausführlicherer Text (z. B. stdout/stderr).
        """
        lines: list[str] = [
            "",
            f"[SECTION] {section}",
            f"[MESSAGE] {message}",
        ]

        if details:
            lines.append("[DETAILS]")
            lines.append(details)

        lines.append("")

        with self.path.open("a", encoding="utf-8") as log_file:
            log_file.write("\n".join(lines))
