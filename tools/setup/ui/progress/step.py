from __future__ import annotations

import sys
from dataclasses import dataclass, field
from threading import Lock
from types import TracebackType
from typing import Final

from tools.setup.ui.console import SetupConsole
from tools.setup.ui.resources.icons import ProgressStatus

# einfache ANSI-Farben
_RESET = "\x1b[0m"
_GREEN = "\x1b[32m"
_RED = "\x1b[31m"
_DIM = "\x1b[2m"

_BAR_WIDTH: Final[int] = 40


@dataclass(slots=True)
class ProgressStep:
    """
    Minimalistisch-moderner Fortschritt:

        Setup-<stid> <StepName>: <info>      (header, 1×)
        [██░░…]  42%  ⏳ Running / ...       (eine Zeile, wird mit \\r überschrieben)

    Ziel:
    - In echten Terminals: sichtbarer, sich füllender Balken.
    - In IDE-Konsolen/Logs: maximal eine Fortschrittszeile pro Step,
      keine "Ziegelmauer" aus Balken-Zeilen.
    """

    description: str
    total: int | None
    console: SetupConsole

    _status: ProgressStatus = field(default=ProgressStatus.STARTING, init=False, repr=False)
    _completed: int = field(default=0, init=False, repr=False)
    _status_text: str = field(default="", init=False, repr=False)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    _header_printed: bool = field(default=False, init=False, repr=False)
    _last_line: str = field(default="", init=False, repr=False)

    # ------------------------------------------------------------
    # Eigenschaften, die BaseStep.run erwartet
    # ------------------------------------------------------------

    @property
    def completed(self) -> int:
        return self._completed

    @property
    def status(self) -> ProgressStatus:
        return self._status

    # ------------------------------------------------------------
    # Kontextmanager
    # ------------------------------------------------------------

    def __enter__(self) -> "ProgressStep":
        with self._lock:
            self._status = ProgressStatus.STARTING
            self._status_text = self._status.label
            self._completed = 0
            self._render_locked()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> bool:
        # Status-Wechsel werden von BaseStep.run gesteuert.
        return False

    # ------------------------------------------------------------
    # Öffentliche API für Steps / BaseStep.run
    # ------------------------------------------------------------

    def set_total(self, total: int | None) -> None:
        """
        Schaltet auf deterministischen oder indeterministischen Modus um.

        total=None → indeterminiert (Text "Aktueller Schritt …")
        total>0    → deterministischer Prozentbalken
        """
        with self._lock:
            self.total = total
            if total is None:
                self._completed = 0
            else:
                self._completed = min(self._completed, total)
                if self._status is ProgressStatus.STARTING:
                    self._status = ProgressStatus.RUNNING
                    if not self._status_text:
                        self._status_text = self._status.label
            self._render_locked()

    def advance(self, steps: int = 1) -> None:
        """
        Erhöht den Fortschritt um `steps` Einheiten und rendert sofort neu.
        """
        with self._lock:
            if self.total and self.total > 0:
                self._completed = min(self.total, self._completed + steps)
                if self._status is ProgressStatus.STARTING:
                    self._status = ProgressStatus.RUNNING
            self._render_locked()

    def set_status(self, text: str) -> None:
        """
        Aktualisiert den Status-Text (z. B. "Installiere: Paket X (3/12)").
        """
        with self._lock:
            self._status_text = text
            self._render_locked()

    def mark_finished(self) -> None:
        with self._lock:
            self._status = ProgressStatus.FINISHED
            if self.total and self.total > 0:
                self._completed = self.total
            if not self._status_text:
                self._status_text = self._status.label
            self._render_locked()
            # Fortschrittszeile abschließen → nächste Ausgabe kommt in neuer Zeile.
            sys.stdout.write("\n")
            sys.stdout.flush()

    def mark_failed(self) -> None:
        with self._lock:
            self._status = ProgressStatus.FAILED
            if self.total and self.total > 0:
                self._completed = self.total
            if not self._status_text:
                self._status_text = self._status.label
            self._render_locked()
            sys.stdout.write("\n")
            sys.stdout.flush()

    def emit_info(self, *, step: str, message: str) -> None:
        """
        Zusatz-Infos, z. B. Debug-Hinweise während des Steps.

        Falls eine laufende Progresszeile aktiv ist, wird vor der Info
        ein Zeilenumbruch erzwungen, damit sich Text und Balken nicht überlagern.
        """
        with self._lock:
            if self._last_line:
                sys.stdout.write("\n")
                sys.stdout.flush()
                self._last_line = ""
            print(f"info: {step}: {message}", flush=True)

    # ------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------

    def _build_header(self) -> str:
        # description wird von BaseStep.run geliefert, z. B.:
        # "Setup-{stid} {StepName}: <info>"
        return self.description

    def _build_bar(self) -> str:
        if self.total is None or self.total <= 0:
            return "Aktueller Schritt …"

        ratio = self._completed / self.total if self.total else 0.0
        filled = int(_BAR_WIDTH * ratio)
        empty = _BAR_WIDTH - filled
        return f"[{'█' * filled}{'░' * empty}] {ratio * 100:3.0f}%"

    def _build_status(self) -> str:
        text = self._status_text or self._status.label
        base = f"{self._status.icon} {text}"

        if self._status is ProgressStatus.FINISHED:
            return f"{_GREEN}{base}{_RESET}"
        if self._status is ProgressStatus.FAILED:
            return f"{_RED}{base}{_RESET}"

        # STARTING/RUNNING: leicht abgetönt
        return f"{_DIM}{base}{_RESET}"

    def _build_line(self) -> str:
        """
        Baut die einzeilige Fortschrittsdarstellung:

            [██░░…]  42%  ⏳ Running / Installiere: Paket X (3/12)
        """
        bar = self._build_bar()
        status = self._build_status()
        return f"{bar}  {status}"

    def _render_locked(self) -> None:
        """
        Gibt ggf. Header aus und aktualisiert die einzeilige Fortschrittszeile.

        Strategie:
        - Header einmal mit print() ausgeben.
        - Fortschritt immer auf derselben Zeile halten (\\r), ohne neue Zeilen
          zu produzieren, solange der Step läuft.
        """
        if not self._header_printed:
            # Header klassisch als eigene Zeile ausgeben
            print(self._build_header(), flush=True)
            self._header_printed = True

        line = self._build_line()

        # Wenn sich nichts geändert hat → nicht spammen
        if line == self._last_line:
            return

        # Fortschrittszeile "in place" aktualisieren:
        # - mit \\r an den Zeilenanfang springen,
        # - Zeile überschreiben,
        # - kein \\n anhängen (das passiert erst in mark_finished/mark_failed).
        sys.stdout.write("\r" + line)
        sys.stdout.flush()

        self._last_line = line
