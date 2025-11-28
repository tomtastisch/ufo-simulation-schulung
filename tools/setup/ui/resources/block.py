from __future__ import annotations

"""
Grundlegender Textbaustein für UI-Ressourcen im Setup.

Dieses Modul definiert die generische Struktur eines Textblocks,
der von Katalogen wie TextCatalog verwendet wird.
"""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(slots=True, frozen=True)
class TextBlock:
    """
    Textbaustein mit frei definierbaren Feldern.

    Typische Felder (konventionell):
    - title
    - intro
    - body
    - hint
    """

    key: str
    fields: Mapping[str, Any]

    @staticmethod
    def _normalize(value: Any, default: str) -> str:
        """
        Normalisiert einen Feldwert zu einem String.

        None → default, alles andere → str(value).
        """
        result: str = default if value is None else str(value)
        return result

    def get(self, field: str, default: str = "") -> str:
        """
        Liefert ein Feld oder einen Default-Text.

        Args:
            field: Feldname innerhalb des Blocks.
            default: Rückgabewert, falls das Feld nicht existiert.

        Returns:
            Feldinhalt als String oder der Default-Wert.
        """
        raw_value: Any = self.fields.get(field, default)
        result: str = self._normalize(raw_value, default)
        return result

    def format(self, field: str = "body", **kwargs: Any) -> str:
        """
        Formatiert ein Feld mit den gegebenen Platzhaltern.

        Nicht vorhandene Felder werden als leerer String behandelt.

        Args:
            field: Feldname, der formatiert werden soll.
            **kwargs: Platzhalter für die Formatierung.

        Returns:
            Formatierter Text oder ein leerer String.
        """
        template: str = self.get(field, "")
        result: str = "" if not template else template.format(**kwargs)
        return result
