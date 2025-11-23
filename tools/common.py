from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final


@dataclass(slots=True)
class ErrorLog:
    """Einfache Fehlerprotokollierung in eine Log-Datei.

    Die Datei wird bei der ersten Nutzung angelegt. Nachfolgende
    Aufrufe hängen Einträge an.
    """

    path: Path
    _initialized: bool = field(default=False, init=False, repr=False)

    HEADER: Final[str] = "=== UFO-Simulation Setup Log ==="

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self.path.write_text(f"{self.HEADER}\n", encoding="utf-8")
            self._initialized = True

    def write_error(self, section: str, message: str, details: str | None = None) -> None:
        """Schreibt einen strukturierten Fehlerblock in die Log-Datei."""
        self._ensure_initialized()
        lines = [f"\n[SECTION] {section}", f"[MESSAGE] {message}"]
        if details:
            lines.append("[DETAILS]")
            lines.append(details)
        lines.append("")
        self.path.write_text(
            self.path.read_text(encoding="utf-8") + "\n".join(lines),
            encoding="utf-8",
        )
