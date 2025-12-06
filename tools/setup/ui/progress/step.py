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
        [██░░…]  42%  ⏳ Running / ...       (eine Zeile, via \\r aktualisiert)

    Besonderheit:
    - Sichtbarer Fortschritt läuft immer in 1%-Schritten von alt → neu,
      auch wenn intern Sprünge wie 0 → 17 → 32 ankommen.
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

    # sichtbarer Prozentwert (0–100), unabhängig von _completed
    _display_percent: int = field(default=0, init=False, repr=False)

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
            self._display_percent = 0
            self._render_locked()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> bool:
        return False

    # ------------------------------------------------------------
    # Öffentliche API für Steps / BaseStep.run
    # ------------------------------------------------------------

    def set_total(self, total: int | None) -> None:
        """
        total=None → indeterminiert (Text "Aktueller Schritt …")
        total>0    → deterministischer Prozentbalken
        """
        with self._lock:
            self.total = total
            if total is None:
                self._completed = 0
                self._display_percent = 0
            else:
                self._completed = min(self._completed, total)
                if self._status is ProgressStatus.STARTING:
                    self._status = ProgressStatus.RUNNING
                    if not self._status_text:
                        self._status_text = self._status.label
            self._render_locked()

    def advance(self, steps: int = 1) -> None:
        """
        Erhöht den logischen Fortschritt um `steps` und rendert neu.
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
            self._render_locked(final=True)

    def mark_failed(self) -> None:
        with self._lock:
            self._status = ProgressStatus.FAILED
            if self.total and self.total > 0:
                self._completed = self.total
            if not self._status_text:
                self._status_text = self._status.label
            self._render_locked(final=True)

    def emit_info(self, *, step: str, message: str) -> None:
        """
        Zusatz-Infos, z. B. Debug-Hinweise während des Steps.
        """
        with self._lock:
            # laufende Progresszeile sauber beenden
            if self._last_line:
                sys.stdout.write("\n")
                sys.stdout.flush()
                self._last_line = ""
            print(f"info: {step}: {message}", flush=True)

    # ------------------------------------------------------------
    # Rendering-Helfer
    # ------------------------------------------------------------

    def _build_header(self) -> str:
        return self.description

    def _build_bar_from_percent(self, percent: int | None) -> str:
        """
        Baut den Balken aus einem Prozentwert (0–100) oder indeterminiert.
        """
        if percent is None:
            return "Aktueller Schritt …"

        percent = max(0, min(100, percent))
        filled = int(_BAR_WIDTH * (percent / 100))
        empty = _BAR_WIDTH - filled
        return f"[{'█' * filled}{'░' * empty}] {percent:3d}%"

    def _build_status(self) -> str:
        text = self._status_text or self._status.label
        base = f"{self._status.icon} {text}"

        if self._status is ProgressStatus.FINISHED:
            return f"{_GREEN}{base}{_RESET}"
        if self._status is ProgressStatus.FAILED:
            return f"{_RED}{base}{_RESET}"
        return f"{_DIM}{base}{_RESET}"

    def _build_line_for_percent(self, percent: int | None) -> str:
        bar = self._build_bar_from_percent(percent)
        status = self._build_status()
        return f"{bar}  {status}"

    # ------------------------------------------------------------
    # Zentrales Rendering
    # ------------------------------------------------------------

    def _render_locked(self, *, final: bool = False) -> None:
        """
        Header einmal ausgeben, Fortschritt in 1%-Schritten von alt → neu animieren.
        """
        # Header genau einmal
        if not self._header_printed:
            print(self._build_header(), flush=True)
            self._header_printed = True

        # indeterminierter Modus: kein % → nur eine Zeile
        if self.total is None or self.total <= 0:
            line = self._build_line_for_percent(None)
            if line != self._last_line:
                sys.stdout.write("\r" + line)
                sys.stdout.flush()
                self._last_line = line
            if final:
                sys.stdout.write("\n")
                sys.stdout.flush()
                self._last_line = ""
            return

        # Ziel-Prozent aus logischem Stand
        target_ratio = self._completed / self.total if self.total else 0.0
        target_percent = max(0, min(100, int(target_ratio * 100)))

        # Rückwärtsbewegung clampen
        if target_percent < self._display_percent:
            self._display_percent = target_percent

        # „Animation“: von aktuellem Display-Wert bis Ziel hochzählen
        start = self._display_percent
        end = target_percent

        if start == end and not final:
            # nichts zu tun
            return

        for p in range(start + 1, end + 1) if end > start else [start]:
            self._display_percent = p
            line = self._build_line_for_percent(p)
            # Minimaler Spam-Schutz
            if line == self._last_line:
                continue
            sys.stdout.write("\r" + line)
            sys.stdout.flush()
            self._last_line = line

        # finaler Abschluss → Zeilenumbruch setzen
        if final:
            sys.stdout.write("\n")
            sys.stdout.flush()
            # self._last_line = ""
