from __future__ import annotations

"""Strukturierte Konsolenausgaben, Fortschritt und Streams für das Setup."""

import datetime
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from types import TracebackType
from typing import Final, TextIO

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from tools.ui.resources import TextCatalog
from tools.common import ErrorLog

_TEXTS: Final[TextCatalog] = TextCatalog()
_CONSOLE: Final[Console] = Console(highlight=False)


class ConsoleMessage(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    FIX = "fix"


@dataclass(slots=True, frozen=True)
class _ConsoleTheme:
    style: str
    icon_name: str


_MESSAGE_THEMES: Final[dict[ConsoleMessage, _ConsoleTheme]] = {
    ConsoleMessage.INFO: _ConsoleTheme(style="bold cyan", icon_name="info"),
    ConsoleMessage.SUCCESS: _ConsoleTheme(style="bold green", icon_name="success"),
    ConsoleMessage.WARNING: _ConsoleTheme(style="bold yellow", icon_name="warning"),
    ConsoleMessage.ERROR: _ConsoleTheme(style="bold red", icon_name="error"),
    ConsoleMessage.FIX: _ConsoleTheme(style="bold magenta", icon_name="fix"),
}


class ProgressStatus(StrEnum):
    STARTING = "starting"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class StepProgress:
    """Kontextmanager für einen einfachen Fortschrittsbalken."""

    description: str
    total: int
    console: Console = field(default=_CONSOLE)

    def __post_init__(self) -> None:
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None
        self._status: ProgressStatus = ProgressStatus.STARTING

    def __enter__(self) -> "StepProgress":
        self._progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(self.description, total=self.total)
        self._status = ProgressStatus.RUNNING
        return self

    def advance(self, step: float = 1.0) -> None:
        """Erhöht den Fortschritt um den angegebenen Schritt."""
        if self._progress is None or self._task_id is None:
            return
        self._progress.update(self._task_id, advance=step)

    def mark_success(self) -> None:
        """Markiert den Schritt als erfolgreich."""
        self._status = ProgressStatus.SUCCESS

    def mark_warning(self) -> None:
        """Markiert den Schritt mit Warnung."""
        self._status = ProgressStatus.WARNING

    def mark_error(self) -> None:
        """Markiert den Schritt als fehlerhaft."""
        self._status = ProgressStatus.ERROR

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> None:
        if exc is not None:
            self._status = ProgressStatus.ERROR
        if self._progress is not None and self._task_id is not None:
            self._progress.update(self._task_id, completed=self.total)
            self._progress.stop()
        icon = _TEXTS.icon("step", "🧩")
        if self._status is ProgressStatus.SUCCESS:
            icon = _TEXTS.icon("success", "✅")
        elif self._status is ProgressStatus.WARNING:
            icon = _TEXTS.icon("warning", "⚠️")
        elif self._status is ProgressStatus.ERROR:
            icon = _TEXTS.icon("error", "❌")
        _CONSOLE.print(f"{icon} {self.description}")


class SetupConsole:
    """Zentrale Helferklasse für strukturierte Konsolenausgaben."""

    @staticmethod
    def _print(message: str, level: ConsoleMessage) -> None:
        theme = _MESSAGE_THEMES[level]
        icon = _TEXTS.icon(theme.icon_name, "")
        prefix = f"{icon} " if icon else ""
        _CONSOLE.print(f"{prefix}{message}", style=theme.style)

    @staticmethod
    def header(title: str) -> None:
        """Zeigt einen hervorgehobenen Haupttitel an."""
        icon = _TEXTS.icon("ufo", "🛸")
        panel = Panel.fit(f"{icon} {title}", style="bold blue", border_style="blue")
        _CONSOLE.print(panel)
        _CONSOLE.print()

    @staticmethod
    def subheader(text: str) -> None:
        """Zeigt einen Abschnittstitel an."""
        _CONSOLE.print()
        _CONSOLE.print(text, style="bold white")
        _CONSOLE.print()

    @staticmethod
    def info(message: str) -> None:
        SetupConsole._print(message, ConsoleMessage.INFO)

    @staticmethod
    def success(message: str) -> None:
        SetupConsole._print(message, ConsoleMessage.SUCCESS)

    @staticmethod
    def warning(message: str) -> None:
        SetupConsole._print(message, ConsoleMessage.WARNING)

    @staticmethod
    def error(message: str) -> None:
        SetupConsole._print(message, ConsoleMessage.ERROR)

    @staticmethod
    def fix(message: str) -> None:
        SetupConsole._print(message, ConsoleMessage.FIX)

    @staticmethod
    def from_resource(block: str, field: str = "body") -> None:
        """Gibt einen Textblock aus der Ressourcen-Datei aus."""
        text = _TEXTS.text(block, field=field)
        if text:
            _CONSOLE.print(text)

    @staticmethod
    def legend() -> None:
        """Zeigt die Legende der verwendeten Icons."""
        text = _TEXTS.format(
            "legend",
            info=_TEXTS.icon("info", "ℹ️"),
            success=_TEXTS.icon("success", "✅"),
            warning=_TEXTS.icon("warning", "⚠️"),
            error=_TEXTS.icon("error", "❌"),
            step=_TEXTS.icon("step", "🧩"),
            start=_TEXTS.icon("start", "🚀"),
        )
        _CONSOLE.print(text)


def echo_stream(stream: TextIO, prefix: str = "") -> None:
    """Leitet einen Textstrom Zeile für Zeile an die Konsole weiter."""
    for line in stream:
        if prefix:
            _CONSOLE.print(f"{prefix}{line.rstrip()}")
        else:
            _CONSOLE.print(line.rstrip())
