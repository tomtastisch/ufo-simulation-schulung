"""
Gemeinsame UI-Text-Helfer für Statuszeilen in Progress-Balken.

Alle Texte werden zentral aus tools/setup/ui/resources/setup_ui.toml geladen
und hier nur noch bequem formatiert. So bleiben Ausgaben einheitlich.
"""
from __future__ import annotations

from tools.setup.ui import CATALOG


def initial_running_text() -> str:
    """Initialer Status-Text vor dem ersten Abschluss."""
    return CATALOG.format(
        "step_default",
        field="progress_running",
        default="Running   /   {details}",
        details="–",
    )


def running_text(details: str) -> str:
    """Status-Text für laufende Ausführung mit Detail-Text."""
    return CATALOG.format(
        "step_default",
        field="progress_running",
        default="Running   /   {details}",
        details=details,
    )


def finished_text(details: str | None = None) -> str:
    return CATALOG.format(
        "step_default",
        field="progress_finished",
        default="Finished /   {details}",
        details=details or "",
    )


def failed_text(details: str | None = None) -> str:
    return CATALOG.format(
        "step_default",
        field="progress_failed",
        default="Failed     /   {details}",
        details=details or "",
    )
