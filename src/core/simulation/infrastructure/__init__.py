#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Infrastructure-Modul für die UFO-Simulation.

Modulzweck
----------
Dieses Modul bündelt alle Infrastruktur-Komponenten, die grundlegende Dienste
für die gesamte Simulation bereitstellen, aber selbst keine Simulationslogik
enthalten. Es bildet die technische Basis für alle anderen Module.

Strukturelle Verantwortlichkeiten
----------------------------------
Das Infrastructure-Modul folgt diesen Architektur-Prinzipien:

1. **Framework-Unabhängigkeit**: Keine direkten Abhängigkeiten zu UI-, OS- oder
   Netzwerk-Frameworks. Ausschließlich Python-Standardbibliothek und minimal
   erforderliche externe Pakete.

2. **Keine Simulationslogik**: Keine Abhängigkeiten zu State, Physics, Controller
   oder anderen fachlichen Simulationsmodulen. Reine Infrastruktur-Dienste.

3. **Thread-Sicherheit**: Alle öffentlichen APIs sind thread-sicher konzipiert
   und können aus mehreren Threads ohne externe Synchronisation verwendet werden.

4. **Single Source of Truth**: Zentrale Definitionen für Konfiguration und
   Logging-Verhalten. Keine duplizierten Konstanten oder Konfigurationen.

Modul-Bestandteile
------------------
config.py:
    Zentrale Konfigurationsverwaltung mit allen physikalischen Parametern,
    Schwellenwerten und Visualisierungseinstellungen als immutable Dataclass.
    Abgeleitete Werte werden als Properties berechnet.

logging_setup.py:
    Zentrale Logging-Konfiguration mit thread-sicherer Initialisierung und
    einheitlichem Logging-Verhalten für die gesamte Anwendung.

Öffentliche API
---------------
Konfiguration:
    - SimulationConfig: Zentrale Konfigurationsklasse (frozen dataclass)
    - DEFAULT_CONFIG: Standard-Konfigurationsinstanz

Logging:
    - configure_logging(level, format_string, datefmt): Initialisiert das Logging-System
    - get_logger(name): Gibt einen konfigurierten Logger zurück

Verwendungsbeispiele
--------------------
Konfiguration:
    >>> from core.simulation.infrastructure import SimulationConfig, DEFAULT_CONFIG
    >>>
    >>> # Standard-Konfiguration verwenden
    >>> config = DEFAULT_CONFIG
    >>> print(f"vmax: {config.vmax_kmh} km/h = {config.vmax_ms} m/s")
    >>>
    >>> # Custom-Konfiguration erstellen
    >>> custom_config = SimulationConfig(vmax_kmh=20.0, dt=0.05)
    >>> print(f"Safe landing threshold: {custom_config.safe_landing_v_threshold_kmh} km/h")

Logging:
    >>> from core.simulation.infrastructure import configure_logging, get_logger
    >>> import logging
    >>>
    >>> # Einmalig beim Programmstart
    >>> configure_logging(level=logging.DEBUG)
    >>>
    >>> # In jedem Modul
    >>> logger = get_logger(__name__)
    >>> logger.info("Simulation gestartet")
    >>> logger.debug("Debug-Information")

Kombination:
    >>> from core.simulation.infrastructure import SimulationConfig, get_logger
    >>>
    >>> logger = get_logger(__name__)
    >>> config = SimulationConfig(vmax_kmh=25.0)
    >>> logger.info(f"Konfiguration geladen: vmax={config.vmax_kmh} km/h")

Erweiterbarkeit
---------------
Zukünftige Infrastruktur-Komponenten können hier ergänzt werden:
    - metrics.py: Performance-Metriken und Telemetrie
    - profiling.py: Profiling-Werkzeuge für Performance-Analyse
    - validation.py: Zentrale Eingabe-Validierung
    - serialization.py: Konfiguration laden/speichern (JSON, YAML, etc.)

Architektur-Prinzipien
----------------------
- Minimale externe Abhängigkeiten (nur Standardbibliothek wo möglich)
- Thread-Sicherheit für alle öffentlichen APIs
- Keine Nebenwirkungen auf andere Projekte im gleichen Prozess
- Vollständige Dokumentation aller öffentlichen Schnittstellen
- Testbarkeit ohne spezielle Mocks oder Fixtures
"""

from __future__ import annotations

# Import aller Konfigurationsklassen
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

