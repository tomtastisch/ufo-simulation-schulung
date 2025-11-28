# tools/setup/ui/resources/icons.py
from __future__ import annotations

"""
Enum-basierte Icon- und Statusdefinitionen für das Setup-UI.

Dieses Modul kapselt:
- MessageLevel: logische Stufen für Konsolenmeldungen (info, success, ...)
- ProgressStatus: Zustände von Fortschrittsblöcken inkl. Icon-/Label-Metadaten.
"""

from enum import Enum
from functools import cached_property
from typing import Final

from tools.setup.ui.resources.catalog import CATALOG


class MessageLevel(Enum):
    """Logische Stufen für strukturierte Konsolenausgaben."""

    INFO = ("info", "ℹ️", None)
    SUCCESS = ("success", "✅", "bold green")
    WARNING = ("warning", "⚠️", "yellow")
    ERROR = ("error", "❌", "bold red")
    CONTINUE = ("continue", "🚀", None)
    PLAIN = ("plain", "", None)

    def __init__(self, icon_key: str, fallback_icon: str, style: str | None) -> None:
        self._icon_key: Final[str] = icon_key
        self._fallback_icon: Final[str] = fallback_icon
        self.style: str | None = style

    @cached_property
    def icon(self) -> str:
        """Liefert das Icon aus dem Katalog oder den Fallback."""
        return CATALOG.icon(self._icon_key, self._fallback_icon)


class ProgressStatus(Enum):
    """
    Interner Status eines Fortschrittsblocks inkl. Icon- und Label-Metadaten.
    """

    # Keys passend zu [icons] in setup_ui.toml: start, run, ok, fail
    STARTING = ("start", "🔄", "started")
    RUNNING = ("run", "⏳", "running")
    FINISHED = ("ok", "✅", "finished")
    FAILED = ("fail", "❌", "failed")

    def __init__(self, icon_key: str, fallback_icon: str, label: str) -> None:
        self._icon_key: Final[str] = icon_key
        self._fallback_icon: Final[str] = fallback_icon
        self.label: str = label

    @cached_property
    def icon(self) -> str:
        """Liefert das Icon aus dem Katalog oder den Fallback."""
        return CATALOG.icon(self._icon_key, self._fallback_icon)
