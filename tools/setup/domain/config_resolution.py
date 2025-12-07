# tools/setup/domain/config_resolution.py
from __future__ import annotations

"""
Datenmodell für Konfigurationsauflösung.

Enthält das Ergebnis der Drei-Ebenen-Fallback-Resolution.
"""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfigResolution:
    """
    Ergebnis der Konfigurationsauflösung.

    Attributes:
        config: Finale, vollständig aufgelöste Konfiguration
        warnings: Liste von Warnungen (z.B. ungültige Keys)
        suggestions: Mapping von ungültigen Keys zu Vorschlägen
    """

    config: Mapping[str, object]
    warnings: tuple[str, ...] = ()
    suggestions: Mapping[str, tuple[str, ...]] | None = None

    def __post_init__(self) -> None:
        """Initialize suggestions with empty dict if None."""
        if self.suggestions is None:
            object.__setattr__(self, "suggestions", {})
