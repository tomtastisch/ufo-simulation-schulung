#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phasen- und Manöver-Analyse für UFO-Simulation."""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, replace as dataclass_replace
from typing import Literal

import numpy as np

from core.simulation.infrastructure import DEFAULT_CONFIG, SimulationConfig
from core.simulation.state.state import UfoState

# Logger für dieses Modul
logger = logging.getLogger(__name__)

# =============================================================================
# PHASENMODELL - Zentral und threadsicher
# =============================================================================

Phase = Literal["idle", "takeoff", "flying", "landing", "landed", "crashed"]


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
        - landing: kontrollierter Sinkflug nahe Boden (vz < 0)
        - flying: normale Flugphase

    Args:
        s: Aktueller UFO-Zustand
        config: Simulations-Konfiguration

    Returns:
        Phase als Literal-String
    """
    has_flown = s.dist > config.zero_value or s.ftime > config.zero_value

    # Rules werden in Prioritätsreihenfolge geprüft
    rules: list[tuple[Phase, bool]] = [
        ("crashed", s.z < config.zero_value),
        ("landed", s.z == config.zero_value and s.v == 0.0 and has_flown),
        ("takeoff", s.ftime == config.zero_value and s.v > 0.0 and s.z > config.zero_value),
        ("landing", s.v > 0.0 > s.vz and config.zero_value < s.z <= config.landing_detection_height_m),
        ("flying", s.v > 0.0 and s.z > config.zero_value),
    ]

    for phase, condition in rules:
        if condition:
            return phase

    return "idle"  # Default-Fall


# =============================================================================
# MANÖVER-ANALYSE - Beobachter-Schicht
# =============================================================================

@dataclass
class ManeuverAnalysis:
    """
    Strukturierte Auswertung des aktuellen Manövers.

    Wird vom StateObserver aus dem Zustandsverlauf abgeleitet.
    """
    phase: Phase
    is_ascending: bool = False
    is_descending: bool = False
    is_turning: bool = False
    is_stagnating: bool = False
    avg_vz: float = 0.0
    avg_heading_change: float = 0.0


class StateObserver:
    """
    Beobachter-Klasse für Manöver-Erkennung aus Zustandshistorie.

    Hält einen Ringpuffer der letzten N Zustände und leitet daraus
    das aktuelle Manöver ab. Rein lesend, keine Schreibzugriffe auf den State.
    """

    def __init__(self, config: SimulationConfig = DEFAULT_CONFIG):
        """
        Initialisiert den Observer mit gegebener Konfiguration.

        Args:
            config: Simulations-Konfiguration für Schwellenwerte
        """
        self.config = config
        self.history: deque[UfoState] = deque(maxlen=config.observer_history_size)
        logger.info(f"StateObserver initialized with history_size={config.observer_history_size}")

    def observe(self, state: UfoState) -> None:
        """
        Fügt einen neuen Zustand zur Historie hinzu.

        Args:
            state: Aktueller UFO-Zustand (sollte ein Snapshot sein)
        """
        self.history.append(dataclass_replace(state))

    def analyze(self) -> ManeuverAnalysis:
        """
        Analysiert die Historie und gibt eine strukturierte Manöver-Beschreibung zurück.

        Returns:
            ManeuverAnalysis mit Phase und Flags
        """
        if not self.history:
            return ManeuverAnalysis(phase="idle")

        current: UfoState = self.history[-1]
        phase: Phase = compute_phase(current, self.config)

        # Standardwerte
        is_ascending: bool = False
        is_descending: bool = False
        is_turning: bool = False
        is_stagnating: bool = False
        avg_vz: float = 0.0
        avg_heading_change: float = 0.0

        if len(self.history) >= 3:
            # Berechne Durchschnitte über letzte N Zustände
            recent = list(self.history)[-10:]  # Letzte 10 oder weniger

            # Vertikale Bewegung
            vz_values = [s.vz for s in recent]
            if vz_values:
                avg_vz = sum(vz_values) / len(vz_values)
                is_ascending = avg_vz > self.config.climb_vz_threshold_ms
                is_descending = avg_vz < self.config.descent_vz_threshold_ms

            # Drehung (Heading-Änderung)
            if len(recent) >= 2:
                heading_changes = []
                for i in range(1, len(recent)):
                    delta_d = recent[i].d - recent[i - 1].d
                    # Wrap-around berücksichtigen
                    if delta_d > 180:
                        delta_d -= 360
                    elif delta_d < -180:
                        delta_d += 360
                    heading_changes.append(abs(delta_d))

                if heading_changes:
                    avg_heading_change = sum(heading_changes) / len(heading_changes)
                    is_turning = avg_heading_change > self.config.turn_heading_threshold_deg

            # Stagnation (kaum Positionsänderung trotz Sollgeschwindigkeit)
            if len(recent) >= 2:
                total_distance = 0.0
                for i in range(1, len(recent)):
                    # NumPy für effiziente Distanzberechnung
                    pos_delta = recent[i].position_vector - recent[i - 1].position_vector
                    total_distance += np.linalg.norm(pos_delta)

                avg_distance_per_step = total_distance / (len(recent) - 1)
                expected_distance = current.vel * self.config.dt
                # Stagnation, nur wenn Sollgeschwindigkeit > 0 und tatsächliche Bewegung < 50% der erwarteten
                is_stagnating = (
                        current.v > 0.0 and
                        expected_distance > 0.0 and
                        avg_distance_per_step < expected_distance * 0.5
                )

        return ManeuverAnalysis(
            phase=phase,
            is_ascending=is_ascending,
            is_descending=is_descending,
            is_turning=is_turning,
            is_stagnating=is_stagnating,
            avg_vz=avg_vz,
            avg_heading_change=avg_heading_change,
        )

    def get_maneuver_description(self) -> str:
        """
        Gibt eine lesbare Beschreibung des aktuellen Manövers zurück.

        Returns:
            String-Beschreibung des Manövers
        """
        analysis = self.analyze()

        parts = [f"Phase: {analysis.phase}"]

        if analysis.is_ascending:
            parts.append("climbing")
        elif analysis.is_descending:
            parts.append("descending")

        if analysis.is_turning:
            parts.append(f"turning (Δd={analysis.avg_heading_change:.1f}°/step)")

        if analysis.is_stagnating:
            parts.append("stagnating")

        if analysis.avg_vz != 0.0:
            parts.append(f"vz={analysis.avg_vz:.2f}m/s")

        return ", ".join(parts)
