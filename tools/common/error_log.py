from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ErrorLog:
    """Schreibt Fehler strukturiert in eine Logdatei."""

    path: Path
    _initialized: bool = field(default=False, init=False)

    def _ensure_header(self) -> None:
        """Initialisiert die Logdatei bei erster Verwendung."""
        if self._initialized:
            return
        if not self.path.exists():
            self.path.write_text(
                "# Setup Error Log\n# Nur Fehler werden hier protokolliert\n\n",
                encoding="utf-8",
            )
        self._initialized = True

    def write_error(self, section: str, message: str, details: str = "") -> None:
        """Schreibt einen Fehlerblock in die Logdatei."""
        self._ensure_header()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.path.open("a", encoding="utf-8") as log:
            log.write(f"\n{'=' * 70}\n")
            log.write(f"[{timestamp}] FEHLER: {section}\n")
            log.write(f"{'-' * 70}\n")
            log.write(f"{message}\n")
            if details:
                log.write(f"\nDetails:\n{details}\n")
