#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exception-Hierarchie für die UFO-Simulation.

Definiert projektspezifische Exceptions für Fehlerbehandlung in
Simulation, Konfiguration und weiteren fachlichen Bereichen.

Komponenten:
    - SimulationError: Basis-Exception für Simulationsfehler
    - ConfigError: Fehler bei Konfigurationsparametern
"""

from __future__ import annotations

from .simulation import ConfigError, SimulationError

__all__ = [
    "SimulationError",
    "ConfigError",
]



