#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phasenmodell und Phasenerkennung für UFO-Flugzustände.

Dieses Modul definiert die Flugphasen und implementiert die regelbasierte
Phasenerkennung basierend auf dem aktuellen UFO-Zustand.
"""

from __future__ import annotations

from typing import Literal

from ..infrastructure import DEFAULT_CONFIG, SimulationConfig
from ..state.state import UfoState

# =============================================================================
# PHASENMODELL
# =============================================================================

Phase = Literal[
    "idle",  # am Boden, noch nicht gestartet
    "takeoff",  # gerade abgehoben, erste Flugsekunden
    "hovering",  # schwebt bewegungslos in der Luft
    "flying",  # aktiver Flug mit Horizontalbewegung
    "landing",  # kontrollierter Sinkflug zum Boden
    "landed",  # sicher gelandet nach Flug
    "crashed"  # abgestürzt (z < 0)
]


def compute_phase(s: UfoState, config: SimulationConfig = DEFAULT_CONFIG) -> Phase:
    """
    Leitet die Flugphase deterministisch aus dem Zustand ab.

    Threadsicher und zustandslos. Verwendet Rule-basierte Evaluation mit
    Prioritätsreihenfolge - erste erfüllte Bedingung bestimmt die Phase.

    Phasen:
        - crashed: z < 0 (Crash-Marker)
        - idle: am Boden, noch nie geflogen
        - landed: am Boden nach erfolgreichem Flug
        - takeoff: gerade abgehoben (erste Sekunden in der Luft)
        - hovering: schwebt in der Luft (v ≈ 0, z > 0, vz ≈ 0)
        - landing: kontrollierter Sinkflug nahe Boden (vz < 0)
        - flying: normale Flugphase mit Bewegung

    Args:
        s: Aktueller UFO-Zustand
        config: Simulations-Konfiguration

    Returns:
        Phase als Literal-String
    """
    has_flown = s.dist > config.zero_value or s.ftime > config.zero_value

    # Rules werden in Prioritätsreihenfolge geprüft
    rules: list[tuple[Phase, bool]] = [
        (
            "crashed",
            s.z < config.zero_value
        ),
        (
            "landed",
            s.z == config.zero_value and s.v == 0.0 and has_flown
        ),
        (
            "takeoff",
            s.ftime == config.zero_value and s.v > 0.0 and s.z > config.zero_value,
        ),
        (
            "landing",
            s.v > 0.0 > s.vz and
            config.zero_value < s.z <= config.landing_detection_height_m,
        ),
        (
            "hovering",
            s.z > config.zero_value >= abs(s.v) and
            abs(s.vz) <= config.zero_value
        ),
        (
            "flying",
            s.v > 0.0 and s.z > config.zero_value
        ),
    ]

    for phase, condition in rules:
        if condition:
            return phase

    return "idle"  # Default-Fall
