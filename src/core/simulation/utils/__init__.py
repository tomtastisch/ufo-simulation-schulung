"""
Utilities für die UFO-Simulation.

Dieses Paket enthält wiederverwendbare Hilfsfunktionen und Decorators,
die keine direkten Abhängigkeiten zu den Simulationsklassen haben.

Verfügbare Module:
- threads: Threading-Utilities (@synchronized Decorator)
"""

from .threads import synchronized

__all__ = [
    "synchronized",
]
