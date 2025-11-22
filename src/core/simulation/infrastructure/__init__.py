#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Infrastruktur-Komponenten für die UFO-Simulation.

Stellt grundlegende Dienste bereit (Konfiguration, Logging) ohne
Simulationslogik. Framework-unabhängig und thread-sicher.

Komponenten:
    - SimulationConfig: Zentrale Konfigurations-Dataclass (immutable)
    - DEFAULT_CONFIG: Standard-Konfigurationsinstanz
    - configure_logging: Logging-System initialisieren (thread-sicher)
    - get_logger: Logger-Factory (thread-sicher)

Architektur-Hinweis:
    Alle Konfigurationsklassen (auch zukünftige) sollten in simulation_config.py
    definiert werden, um eine einheitliche Konfigurationsverwaltung
    sicherzustellen. Logging-Funktionen bleiben in logging_config.py.
"""

from __future__ import annotations

# Logging
from .logging_config import configure_logging, get_logger
# Konfiguration
from .simulation_config import DEFAULT_CONFIG, SimulationConfig

# Öffentliche API
__all__ = [
    # Konfiguration
    "SimulationConfig",
    "DEFAULT_CONFIG",
    # Logging
    "configure_logging",
    "get_logger",
]
