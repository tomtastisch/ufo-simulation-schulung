#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generische Utility-Funktionen.

Stellt wiederverwendbare Hilfsfunktionen ohne Simulationsabhängigkeiten bereit.
Reine Funktionen ohne Zustand oder Seiteneffekte.

Komponenten:
    - maths: Trigonometrie, Winkel-Normalisierung, Wertebegrenzung
    - validation: Wertebereichs-Validierung
    - geometry: 3D-Koordinatentransformationen (kartesisch ↔ sphärisch)
    - threads: Thread-Synchronisations-Utilities
    - condition_waiter: Event-basiertes Warten auf Bedingungen
"""

from .condition_waiter import ConditionWaiter
from .geometry import cartesian_to_spherical, spherical_to_cartesian
from .maths import clamp, deg_to_rad, rad_to_deg, wrap_angle_deg, wrap_angle_rad
from .threads import synchronized
from .validation import is_in_range, validate_range

__all__ = [
    # maths
    "deg_to_rad",
    "rad_to_deg",
    "wrap_angle_deg",
    "wrap_angle_rad",
    "clamp",
    # validation
    "validate_range",
    "is_in_range",
    # geometry
    "cartesian_to_spherical",
    "spherical_to_cartesian",
    # threads
    "synchronized",
    # condition_waiter
    "ConditionWaiter",
]

