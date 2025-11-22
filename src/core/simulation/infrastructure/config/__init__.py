#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Komponenten:
    - SimulationConfig: Zentrale Konfigurations-Dataclass (immutable)
    - DEFAULT_CONFIG: Standard-Konfigurationsinstanz
    - configure_logging: Logging-System initialisieren (thread-sicher)
    - get_logger: Logger-Factory (thread-sicher)

Architektur-Hinweis:
    Alle Konfigurationsklassen (auch zukünftige) sollten in ./config
    definiert werden, um eine einheitliche Konfigurationsverwaltung
    sicherzustellen.
"""
from __future__ import annotations

import core.simulation.infrastructure.config.logging
import core.simulation.infrastructure.config.simulation
from core.simulation.infrastructure.config.logging import configure_logging, get_logger
from core.simulation.infrastructure.config.simulation import DEFAULT_CONFIG, SimulationConfig

# Interne API
__all__ = [
    "SimulationConfig",
    "DEFAULT_CONFIG",
    "configure_logging",
    "get_logger",
]
