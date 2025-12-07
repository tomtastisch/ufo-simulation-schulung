from __future__ import annotations

"""
Text- und Icon-Katalog für das Setup der UFO-Simulation.

Dieses Modul lädt die Ressourcen aus der TOML-Datei `setup_ui.toml`
und stellt eine Lookup-API für Texte und Icons bereit.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Mapping, Optional

import tomllib

from tools.setup.ui.resources.block import TextBlock


@dataclass(slots=True, frozen=True)
class TextCatalog:
    """
    Katalog aller Textbausteine und Icons für das Setup.

    Lädt Inhalte aus der TOML-Ressource `setup_ui.toml` und bietet
    Zugriff über `text()`, `format()` und `icon()`.
    """

    _blocks: Mapping[str, TextBlock]
    _icons: Mapping[str, str]

    @classmethod
    def load(cls, path: Path) -> "TextCatalog":
        """
        Erzeugt einen Katalog aus der angegebenen TOML-Datei.

        Args:
            path: Pfad zur TOML-Datei mit den UI-Ressourcen.

        Returns:
            Initialisierter TextCatalog. Bei fehlender Datei ein leerer Katalog.
        """
        blocks: dict[str, TextBlock] = {}
        icons: dict[str, str] = {}

        if path.exists():
            with path.open("rb") as f:
                raw: dict[str, Any] = tomllib.load(f)

                blocks = {
                    name: TextBlock(key=name, fields=fields)
                    for name, fields in raw.get("texts", {}).items()
                }

                icons = {name: str(value) for name, value in raw.get("icons", {}).items()}

        catalog: TextCatalog = cls(_blocks=blocks, _icons=icons)
        return catalog

    @classmethod
    def default(cls) -> "TextCatalog":
        """
        Lädt den Standard-Katalog aus `setup_ui.toml` neben diesem Modul.
        """
        path: Path = Path(__file__).with_name("setup_ui.toml")
        catalog: TextCatalog = cls.load(path)
        return catalog

    def _resolve_field(
            self,
            key: str,
            field: str,
            default: str,
    ) -> str:
        """
        Interner Helfer zur Feldauflösung mit Fallback.

        Args:
            key: Name des Textblocks.
            field: Feldname innerhalb des Blocks.
            default: Fallback-Text.

        Returns:
            Aufgelöster Feldwert oder Default.
        """
        block: Optional[TextBlock] = self._blocks.get(key)
        value: str = block.get(field, default) if not block is None else default
        return value

    def text(self, key: str, field: str = "body", default: str = "") -> str:
        """
        Liefert ein Textfeld aus dem angegebenen Block oder einen Default.
        """
        result: str = self._resolve_field(key, field, default)
        return result

    def format(self, key: str, field: str = "body", default: str = "", **kwargs: Any) -> str:
        """
        Liefert einen formatierten Text aus dem angegebenen Block.

        Nicht vorhandene Blöcke oder Felder liefern einen leeren String.
        """
        template: str = self._resolve_field(key, field, default)
        if not template:
            return default
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            # Bei Formatierungsproblemen lieber den Roh-Template-Text oder Default zurückgeben
            return default or template

    def icon(self, key: str, default: str) -> str:
        """
        Liefert ein Icon (Emoji oder Zeichenfolge) für den angegebenen Schlüssel.

        Falls kein Icon definiert ist, wird der Default-Wert verwendet.
        """
        icon_value: Optional[str] = self._icons.get(key)
        result: str = default if icon_value is None else icon_value
        return result

    @classmethod
    def load_catalog(cls, path: Path | None = None) -> TextCatalog:
        """
        Liefert entweder den Standardkatalog oder eine benutzerdefinierte Variante.

        Semantik:
        - path is None          → interner Standardkatalog (setup_ui.toml neben diesem Modul)
        - path ist ein Ordner   → es wird path / "setup_ui.toml" verwendet
        - path ist eine Datei   → genau diese Datei wird geladen
        """
        if path is None:
            return cls.default()

        candidate = path

        # Wenn ein Verzeichnis übergeben wurde, dort nach setup_ui.toml suchen
        if candidate.is_dir():
            candidate = candidate / "setup_ui.toml"

        # cls.load(...) ist bereits robust: bei fehlender Datei → leerer Katalog
        return cls.load(candidate)


CATALOG: Final[TextCatalog] = TextCatalog.load_catalog()
