from __future__ import annotations

"""
Domänenspezifische Typen und Profile für das Setup.

Dieses Unterpaket stellt die zentralen Modelle bereit:
- :class:`BootstrapConfig` für Pfade und Laufzeitparameter,
- :class:`PyProjectProfile` für abgeleitete Projektinformationen,
- :func:`load_pyproject_profile` zum Laden des Profils aus der ``pyproject.toml``.
"""

from .config import BootstrapConfig
from .profile import PyProjectProfile, build_profile

__all__: list[str] = [
    "BootstrapConfig",
    "PyProjectProfile",
    "build_profile",
]
