from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(slots=True)
class TextCatalog:
    """Zentrale Verwaltung von Text- und Icon-Ressourcen aus TOML-Dateien."""

    path: Path = field(
        default_factory=lambda: Path(__file__).with_name("setup_flow_text.toml"),
    )
    _data: Mapping[str, Any] | None = field(default=None, init=False, repr=False)

    def _ensure_loaded(self) -> None:
        if self._data is None:
            self._data = tomllib.loads(self.path.read_text(encoding="utf-8"))

    def block(self, name: str) -> Mapping[str, Any]:
        """Liefert den vollständigen Block (z.B. [setup_header])."""
        self._ensure_loaded()
        raw = self._data or {}
        block = raw.get(name)
        if not isinstance(block, dict):
            raise KeyError(f"Kein Textblock mit Namen '{name}' gefunden.")
        return block

    def text(self, name: str, field: str = "body", fallback: str = "") -> str:
        """Liefert ein einzelnes Textfeld eines Blocks."""
        try:
            return str(self.block(name)[field])
        except KeyError:
            return fallback

    def format(self, name: str, field: str = "body", **kwargs: Any) -> str:
        """Liefert Text und formatiert ihn mit den übergebenen Platzhaltern."""
        template = self.text(name, field=field)
        return template.format(**kwargs)

    def icon(self, key: str, fallback: str = "") -> str:
        """Liefert das Icon mit dem angegebenen Schlüssel aus [icons]."""
        self._ensure_loaded()
        icons = (self._data or {}).get("icons", {})
        if isinstance(icons, dict) and key in icons:
            return str(icons[key])
        return fallback
