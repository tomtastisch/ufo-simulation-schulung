# tools/setup/ui/progress/mode.py
from __future__ import annotations

"""
Steuerung des Fortschrittsverhaltens von Setup-Schritten.
"""

from contextlib import nullcontext
from enum import Enum, auto
from typing import ContextManager, TYPE_CHECKING

from tools.setup.ui.console import SetupConsole

if TYPE_CHECKING:
    from .step import ProgressStep


class ProgressMode(Enum):
    """
    Steuerung des Fortschrittsverhaltens eines Setup-Schritts.

    NONE   → keine Fortschrittsanzeige
    AUTO   → Standard-Fortschrittsanzeige
    SIMPLE → aktuell identisch zu AUTO, für spätere Varianten reserviert
    """

    NONE = auto()
    AUTO = auto()
    SIMPLE = auto()

    def make_context(
            self,
            description: str,
            console: SetupConsole,
    ) -> ContextManager["ProgressStep | None"]:
        """
        Liefert den passenden Kontextmanager:

        - NONE  → nullcontext(None) (kein Fortschritt)
        - AUTO/SIMPLE → ProgressStep mit initial indeterminiertem Balken.
        """
        if self is ProgressMode.NONE:
            return nullcontext(None)

        from .step import ProgressStep

        return ProgressStep(
            description=description,
            total=None,
            console=console,
        )
