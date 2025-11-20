"""
Utility-Module für allgemeine, wiederverwendbare Hilfsfunktionen.

Dieses Paket enthält generische Utilities, die keine Abhängigkeiten zu
Simulation-spezifischen Typen haben und projektübergreifend einsetzbar sind.

Module:
    maths: Numerische Hilfsfunktionen (Trigonometrie, Clamping, Normalisierung)

Architektur-Prinzipien:
    - Keine Imports von SimulationConfig, UfoState, UfoSim oder anderen Simulationslogik
    - Nur Standardbibliothek und numpy als Dependencies erlaubt
    - Reine, zustandslose Funktionen (keine Seiteneffekte)
    - Vollständige Type Hints und Docstrings
    - Physikalisch/mathematisch korrekte Implementierungen

Verwendung:
    from core.simulation.utils.maths import deg_to_rad, clamp, wrap_angle_deg
"""

from .maths import (
    clamp,
    deg_to_rad,
    rad_to_deg,
    wrap_angle_deg,
    wrap_angle_rad,
)

__all__ = [
    "clamp",
    "deg_to_rad",
    "rad_to_deg",
    "wrap_angle_deg",
    "wrap_angle_rad",
]
