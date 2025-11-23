from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import TracebackType
from typing import Final

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

from tools.ui.resources import TextCatalog


class ProgressStatus(StrEnum):
    """Status eines Fortschrittsbalkens."""

    STARTING = "starting"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"


_TEXTS: Final[TextCatalog] = TextCatalog()

_CONSOLE: Final[Console] = Console(
    force_terminal=True,  # TTY erzwingen, auch in IDE-Konsolen
    force_interactive=True,  # Live-Updates erzwingen
)

_PROGRESS_ICONS: Final[dict[ProgressStatus, str]] = {
    ProgressStatus.STARTING: _TEXTS.icon("progress_start", "🔄"),
    ProgressStatus.RUNNING: _TEXTS.icon("progress_run", "⏳"),
    ProgressStatus.FINISHED: _TEXTS.icon("progress_ok", "✅"),
    ProgressStatus.FAILED: _TEXTS.icon("progress_fail", "❌"),
}


class SetupConsole:
    """Zentrale Hilfsklasse für formatierte Konsolenausgabe."""

    @staticmethod
    def header(title: str) -> None:
        _CONSOLE.rule(title, style="bold green")

    @staticmethod
    def subheader(title: str) -> None:
        """Optisch abgesetzte Zwischenüberschrift."""
        _CONSOLE.rule(title, style="cyan")

    @staticmethod
    def info(message: str) -> None:
        icon = _TEXTS.icon("info", "ℹ️")
        _CONSOLE.print(f"{icon} {message}")

    @staticmethod
    def success(message: str) -> None:
        icon = _TEXTS.icon("success", "✅")
        _CONSOLE.print(f"{icon} {message}", style="bold green")

    @staticmethod
    def warning(message: str) -> None:
        icon = _TEXTS.icon("warning", "⚠️")
        _CONSOLE.print(f"{icon} {message}", style="yellow")

    @staticmethod
    def error(message: str) -> None:
        icon = _TEXTS.icon("error", "❌")
        _CONSOLE.print(f"{icon} {message}", style="bold red")

    @staticmethod
    def legend() -> None:
        """Gibt die Legende der Symbole aus."""
        text = _TEXTS.format(
            "legend",
            info=_TEXTS.icon("info", "ℹ️"),
            success=_TEXTS.icon("success", "✅"),
            warning=_TEXTS.icon("warning", "⚠️"),
            error=_TEXTS.icon("error", "❌"),
            rocket=_TEXTS.icon("rocket", "🚀"),
        )
        _CONSOLE.print(text)

    @staticmethod
    def from_resource(block: str, field: str = "body") -> None:
        """Gibt einen Textblock aus der Ressourcen-Datei aus."""
        _CONSOLE.print(_TEXTS.text(block, field))


@dataclass(slots=True)
class StepProgress:
    """Kontextmanager für einen einfachen Fortschrittsbalken.

    Die Beschreibung (Status) kann dynamisch angepasst werden, ohne die
    Konsole mit neuen Zeilen zu überfluten.
    """

    description: str
    total: int
    console: Console = field(default=_CONSOLE)

    _progress: Progress | None = field(default=None, init=False, repr=False)
    _task_id: TaskID | None = field(default=None, init=False, repr=False)
    _status: ProgressStatus = field(
        default=ProgressStatus.STARTING,
        init=False,
        repr=False,
    )

    def __enter__(self) -> StepProgress:
        self._progress = Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[bold cyan]{task.description}", justify="left"),
            BarColumn(bar_width=None),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,  # Zeile bleibt stehen
            refresh_per_second=12,  # flüssigere Updates
            disable=False,  # niemals automatisch abschalten
        )
        self._progress.start()
        self._task_id = self._progress.add_task(
            f"{_PROGRESS_ICONS[self._status]} {self.description}",
            total=self.total if self.total > 0 else None,
        )
        self._status = ProgressStatus.RUNNING
        return self

    def _update_description(self, text: str) -> None:
        if not self._progress or self._task_id is None:
            return
        icon = _PROGRESS_ICONS[self._status]
        self._progress.update(self._task_id, description=f"{icon} {text}")

    def advance(self, step: int = 1, *, status: str | None = None) -> None:
        """Erhöht den Fortschritt und aktualisiert optional den Status."""
        if status is not None:
            self._update_description(status)
        if self._progress and self._task_id is not None and self.total > 0:
            self._progress.advance(self._task_id, step)

    def update_status(self, status: str) -> None:
        """Aktualisiert nur den Beschreibungstext."""
        self._update_description(status)

    def set_status(self, status: str) -> None:
        """Alias für update_status für eine klarere API."""
        self.update_status(status)

    def mark_finished(self) -> None:
        """Markiert den Fortschritt als erfolgreich abgeschlossen."""
        self._status = ProgressStatus.FINISHED
        if self._progress and self._task_id is not None:
            current = self._progress.tasks[self._task_id].description
            clean = current.split(" ", 1)[-1] if " " in current else current
            self._progress.update(
                self._task_id,
                description=f"{_PROGRESS_ICONS[ProgressStatus.FINISHED]} {clean}",
            )

    def mark_failed(self) -> None:
        """Markiert den Fortschritt als fehlgeschlagen."""
        self._status = ProgressStatus.FAILED
        if self._progress and self._task_id is not None:
            current = self._progress.tasks[self._task_id].description
            clean = current.split(" ", 1)[-1] if " " in current else current
            self._progress.update(
                self._task_id,
                description=f"{_PROGRESS_ICONS[ProgressStatus.FAILED]} {clean}",
            )

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> None:
        if exc_type is None and self._status == ProgressStatus.RUNNING:
            self.mark_finished()
        elif exc_type is not None:
            self.mark_failed()

        if self._progress is not None:
            self._progress.stop()
            self._progress = None
            self._task_id = None
