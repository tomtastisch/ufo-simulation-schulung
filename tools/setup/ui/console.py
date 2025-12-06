# tools/setup/ui/console.py
from __future__ import annotations

from dataclasses import dataclass

from tools.setup.ui.resources.icons import MessageLevel


@dataclass(slots=True)
class SetupConsole:
    """
    Schlankes Konsolen-Frontend für das Setup ohne externe Abhängigkeiten.

    Bietet eine kleine, klar definierte API für Setup-Schritte.
    """

    # noinspection PyMethodMayBeStatic
    def _emit(self, level: MessageLevel, message: str) -> None:
        prefix = level.icon
        line = f"{prefix} {message}" if prefix else message
        print(line)

    # öffentliche API – von Steps verwendet
    def info(self, message: str) -> None:
        self._emit(MessageLevel.INFO, message)

    def warning(self, message: str) -> None:
        self._emit(MessageLevel.WARNING, message)

    def error(self, message: str) -> None:
        self._emit(MessageLevel.ERROR, message)

    def result(self, message: str, ok: bool) -> None:
        level = MessageLevel.SUCCESS if ok else MessageLevel.ERROR
        self._emit(level, message)

    # noinspection PyMethodMayBeStatic
    def header(self, message: str) -> None:
        # Header bewusst ohne Level-Icon, um die Einleitung nicht zu überfrachten
        print(message)
