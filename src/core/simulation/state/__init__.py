#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State-Modul für UFO-Simulation.

Modulzweck
----------
Dieses Modul kapselt die vollständige Zustandsrepräsentation der Simulation
und stellt das zentrale Datenmodell für den physikalischen Zustand des UFOs bereit.
Es ist die Single Source of Truth für alle positionsbezogenen, kinematischen und
statistischen Daten während der Simulation.

Strukturelle Verantwortlichkeiten
----------------------------------
Das State-Modul folgt strikten Architektur-Prinzipien:

1. **Datenmodell ohne Logik**: Enthält ausschließlich die Zustandsdatenstruktur,
   keine Verarbeitungslogik. Zustandsverwaltung (StateManager) ist separat.

2. **Keine Abhängigkeiten zu höherwertigen Modulen**: Keine Imports von
   StateManager, PhysicsEngine, Controller, View, Command oder Observer.
   Erlaubt sind nur: dataclasses, numpy, typing sowie optional config und
   generische Utilities.

3. **Immutability**: Die Zustandsklasse ist als frozen dataclass implementiert
   für thread-sichere Verwendung und klare Copy-Semantik.

4. **Effizienz**: Nutzung von slots=True für reduzierten Memory-Footprint und
   schnelleren Attributzugriff. NumPy-basierte Properties für Vektoroperationen.

Modul-Bestandteile
------------------
state.py:
    Definiert UfoState als immutable dataclass mit 18 Feldern für Position,
    Geschwindigkeit, Beschleunigung, Statistik und Steuerkommandos.
    Bietet Properties für effiziente Vektorberechnungen mittels NumPy.

Öffentliche API
---------------
UfoState:
    Immutable Dataclass mit allen physikalischen Zustandsvariablen:
    - Position (x, y, z) in Metern
    - Geschwindigkeit (v, vel, d, i, vx, vy, vz) in km/h bzw. m/s und Grad
    - Beschleunigung (accel_x, accel_y, accel_z) in m/s²
    - Statistik (dist, ftime) für Distanz und Flugzeit
    - Steuerkommandos (delta_v, delta_d, delta_i)
    - Properties: position_vector, velocity_vector, acceleration_vector (NumPy-Arrays)

Verwendungsbeispiele
--------------------
Einfache Instanzierung:
    >>> from core.simulation.state import UfoState
    >>>
    >>> # Default-Zustand (alle Werte 0.0, außer Winkel)
    >>> state = UfoState()
    >>> print(state.x, state.y, state.z)  # 0.0 0.0 0.0
    >>>
    >>> # Custom-Zustand
    >>> state = UfoState(x=10.0, y=20.0, z=30.0, v=15.0)
    >>> print(state.position_vector)  # [10. 20. 30.]

Vektoroperationen:
    >>> state = UfoState(vx=3.0, vy=4.0, vz=0.0)
    >>> import numpy as np
    >>> speed = np.linalg.norm(state.velocity_vector)  # 5.0 m/s
    >>>
    >>> # Beschleunigungsvektor
    >>> state = UfoState(accel_x=1.0, accel_y=2.0, accel_z=-9.81)
    >>> a_mag = np.linalg.norm(state.acceleration_vector)

Immutability (Copy-on-Write):
    >>> state1 = UfoState(x=10.0, y=20.0)
    >>> state2 = state1.replace(x=15.0)  # Erzeugt neue Instanz
    >>> print(state1.x, state2.x)  # 10.0 15.0

Architektur-Prinzipien
----------------------
- Klare Trennung zwischen Zustandsdaten (hier) und Zustandsverwaltung (StateManager)
- Keine Logik außer Property-Berechnungen für Vektorrepräsentationen
- Vollständige Typisierung aller Felder
- Immutability durch frozen=True
- Performance-Optimierung durch slots=True
- NumPy-Integration für effiziente numerische Operationen
"""

from .state import UfoState

__all__ = ["UfoState"]
