#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Infrastruktur-Komponenten für die UFO-Simulation.

Stellt grundlegende Dienste bereit (Konfiguration, Logging) ohne
Simulationslogik. Framework-unabhängig und thread-sicher.

Komponenten:
    - SimulationConfig: Zentrale Konfiguration als frozen dataclass
    - DEFAULT_CONFIG: Standard-Konfigurationsinstanz
    - configure_logging: Logging-System initialisieren
    - get_logger: Logger-Instanz erzeugen
"""

from __future__ import annotations

from .config import DEFAULT_CONFIG, SimulationConfig
from .logging_setup import configure_logging, get_logger

__all__ = [
    "SimulationConfig",
    "DEFAULT_CONFIG",
    "configure_logging",
    "get_logger",
]

from .config import DEFAULT_CONFIG, SimulationConfig

# Import aller Logging-Funktionen
from .logging_setup import configure_logging, get_logger

# Definiere öffentliche API
__all__ = [
    # Konfiguration
    "SimulationConfig",
    "DEFAULT_CONFIG",
    # Logging
    "configure_logging",
    "get_logger",
]

