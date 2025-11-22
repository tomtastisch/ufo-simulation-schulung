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
    - condition_waiter: Event-basiertes Warten auf Bedingungen

Hinweis:
    Thread-Synchronisation (synchronized, etc.) ist nach synchronization/ verschoben.
    Nutze: from core.simulation.synchronization import synchronized
"""

from .condition_waiter import ConditionWaiter
from .geometry import cartesian_to_spherical, spherical_to_cartesian
from .maths import clamp, deg_to_rad, rad_to_deg, wrap_angle_deg, wrap_angle_rad
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
    # condition waiting
    "ConditionWaiter",
]

