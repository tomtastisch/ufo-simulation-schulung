#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State-Paket für UFO-Simulation.

Dieses Paket kapselt die vollständige Zustandsrepräsentation der Simulation
und stellt das zentrale Datenmodell für den physikalischen Zustand des UFOs bereit.

Rolle und Verantwortlichkeiten:
    - Definiert die Datenstruktur für den Simulationszustand (Position, Geschwindigkeit,
      Beschleunigung, Statistik)
    - Bietet Properties für effiziente Vektorberechnungen mittels NumPy
    - Gewährleistet eine klare Trennung zwischen Zustandsdaten und Zustandsverwaltung
      (StateManager ist in einem separaten Modul state/manager.py)

Hauptklassen:
    UfoState: Immutable dataclass (frozen=True) mit slots für den physikalischen Zustand
              (18 Felder: Position, Geschwindigkeit, Beschleunigung, Statistik, Steuerkommandos)

Architektur-Konformität:
    - Keine Abhängigkeiten zu höherwertigen Modulen (StateManager, PhysicsEngine,
      Controller, View, Command, Observer)
    - Erlaubte Imports: dataclasses, numpy, typing
    - Optional: config (für Konstanten) und generische Utilities

Verwendung:
    >>> from core.simulation.state import UfoState
    >>> state = UfoState(x=10.0, y=20.0, z=30.0)
    >>> print(state.position_vector)  # NumPy array [10., 20., 30.]
"""

from .state import UfoState

__all__ = ["UfoState"]
