from __future__ import annotations

"""Lädt Text- und Icon-Blöcke aus einer TOML-Ressourcendatei."""

import tomllib
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

__all__ = ["MissingResourceError", "TextCatalog"]


class MissingResourceError(KeyError):
    """Ausnahme bei fehlenden Textblöcken."""

    def __init__(self, block: str) -> None:
        super().__init__(block)
        self.block = block


@dataclass(frozen=True)  # WICHTIG: KEIN slots=True wegen cached_property
class TextCatalog:
    """Verwaltet Text- und Icon-Ressourcen aus einer TOML-Datei.

    Hinweise:
        - cached_property speichert die Daten im __dict__ der Instanz.
        - Daher darf hier nicht slots=True verwendet werden.
    """

    base_path: Path = Path(__file__).resolve().parent
    filename: str = "text_blocks.toml"

    @cached_property
    def _data(self) -> dict[str, dict[str, str]]:
        path = self.base_path / self.filename
        if not path.exists():
            raise FileNotFoundError(f"Ressourcendatei nicht gefunden: {path}")
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        return data

    def block(self, name: str) -> dict[str, str]:
        """Gibt einen kompletten Block zurück oder wirft MissingResourceError."""
        try:
            value = self._data[name]
        except KeyError as exc:
            raise MissingResourceError(name) from exc
        if not isinstance(value, dict):
            raise MissingResourceError(name)
        return value

    def text(self, name: str, *, field: str = "body", fallback: str = "") -> str:
        """Extrahiert ein einzelnes Textfeld aus einem Block."""
        try:
            block = self.block(name)
            value = block.get(field, fallback)
            return value if isinstance(value, str) else fallback
        except MissingResourceError:
            return fallback

    def format(self, name: str, *, field: str = "body", **kwargs: str) -> str:
        """Formatiert einen Textblock mit Platzhaltern."""
        template = self.text(name, field=field)
        return template.format(**kwargs)

    def icon(self, key: str, fallback: str = "") -> str:
        """Gibt ein Icon aus dem [icons]-Block zurück."""
        return self.text("icons", field=key, fallback=fallback)
