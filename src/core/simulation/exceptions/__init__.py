#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zentrale Exception-Hierarchie für die UFO-Simulation.

Modulzweck
----------
Dieses Modul organisiert alle projektspezifischen Exceptions nach fachlichen
Zuständigkeitsbereichen. Die Strukturierung ermöglicht eine klare Fehlerbehandlung
und vereinfacht das gezielte Abfangen von Fehlern auf unterschiedlichen
Abstraktionsebenen.

Strukturelle Verantwortlichkeiten
----------------------------------
Das Modul ist nach folgenden Prinzipien organisiert:

1. **Trennung nach Zuständigkeitsbereich**: Jede Exception-Datei behandelt einen
   spezifischen fachlichen Bereich (Simulation, Visualisierung, I/O, Netzwerk).

2. **Hierarchische Organisation**: Basis-Exceptions ermöglichen das Abfangen
   ganzer Exception-Kategorien, während spezifische Exceptions präzise
   Fehlerbehandlung erlauben.

3. **Zentrale API**: Alle öffentlichen Exceptions werden über dieses Modul
   exportiert, unabhängig von ihrer internen Dateistruktur.

Modul-Bestandteile
------------------
- simulation.py: Exceptions für Kern-Simulationslogik (Physik, State, Controller, Config)
- (zukünftig) visualization.py: GUI- und Rendering-Fehler
- (zukünftig) io.py: Datei-I/O und Serialisierungsfehler
- (zukünftig) network.py: Netzwerk- und Kommunikationsfehler

Öffentliche API
---------------
Simulation-Exceptions:
    - SimulationError: Basis-Exception für alle Simulationsfehler
    - ConfigError: Fehler bei Konfigurationsparametern

Verwendungsbeispiele
--------------------
    >>> from core.simulation.exceptions import SimulationError, ConfigError
    >>>
    >>> # Spezifischen Fehler werfen
    >>> raise ConfigError("Ungültiger Parameter: vmax muss > 0 sein")
    >>>
    >>> # Kategorie von Fehlern abfangen
    >>> try:
    ...     # Simulationscode
    ...     pass
    >>> except SimulationError as e:
    ...     # Behandelt alle Simulation-bezogenen Fehler
    ...     print(f"Simulationsfehler: {e}")

Architektur-Prinzipien
----------------------
- Exception-Klassen sind minimalistisch und enthalten keine Logik
- Jede Exception hat einen klaren, selbsterklärenden Namen
- Die Hierarchie folgt dem Prinzip der zunehmenden Spezialisierung
- Keine zirkulären Abhängigkeiten zu anderen Modulen
"""

from __future__ import annotations

# Import aller Simulation-Exceptions
from .simulation import ConfigError, SimulationError

# Definiere öffentliche API
__all__ = [
    # Simulation-Exceptions
    "SimulationError",
    "ConfigError",
]

