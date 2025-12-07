from __future__ import annotations

"""
Strukturiertes Nachrichtenmodell für die Setup-Konsole.

Dieses Modul kapselt den Nachrichtentyp, der von der SetupConsole
für eine einheitliche Ausgabe verwendet wird.
"""

from dataclasses import dataclass

from tools.setup.ui.resources.icons import MessageLevel


@dataclass(slots=True, frozen=True)
class Message:
    """
    Strukturierte Nachricht für die Setup-Konsole.

    Attributes:
        level: Logische Stufe der Nachricht (info, success, warning, error, plain).
        content: Auszugebender Nachrichtentext (muss nichtleer sein).
    """

    level: MessageLevel
    content: str

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Message.content must not be empty")
