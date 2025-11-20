"""
Utilities für die UFO-Simulation.

Dieses Paket enthält wiederverwendbare Hilfsfunktionen und Decorators,
die keine direkten Abhängigkeiten zu den Simulationsklassen haben.

Verfügbare Module:
- threads: Threading-Utilities (@synchronized Decorator für Instanzmethoden)
- global_lock: Threading-Utilities (@synchronized_global Decorator für Modul-Level-Funktionen)
"""

from .threads import synchronized
from .global_lock import synchronized_global

__all__ = [
    "synchronized",
    "synchronized_global",
]
