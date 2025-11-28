from __future__ import annotations

"""
Ressourcen für UI-Texte und Icons des Setup-Prozesses.

Dieses Unterpaket stellt:
- :class:`TextBlock` als Basistyp für Textbausteine,
- :class:`TextCatalog` als TOML-basierte Sammlung von Texten und Icons,
- :data:`CATALOG` als vorkonfigurierte Standardinstanz
bereit.
"""

from .block import TextBlock
from .catalog import TextCatalog, CATALOG

__all__: tuple[str, ...] = (
    "TextBlock",
    "TextCatalog",
    "CATALOG",
)
