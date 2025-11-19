#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zustandsmodell für UFO-Simulation.

Dieses Modul definiert die zentrale Zustandsrepräsentation `UfoState`,
die den vollständigen physikalischen Zustand des UFOs/der Drohne kapselt.

`UfoState` ist als `dataclass` mit `slots=True` für Performance-Optimierung
implementiert und nutzt numpy für effiziente Vektorberechnungen.

Architektur-Konformität:
- Keine Abhängigkeiten zu höherwertigen Modulen (StateManager, PhysicsEngine,
  Controller, View, Command, Observer)
- Nur Standardbibliothek, typing und numpy
- Reine Datenstruktur mit abgeleiteten Properties
"""

from dataclasses import dataclass
import numpy as np


@dataclass(slots=True, kw_only=True)
class UfoState:
    """
    Repräsentiert den aktuellen physikalischen Zustand des UFOs.

    Alle Felder sind vollständig typisiert und dokumentiert.
    Verwendet numpy für effiziente Vektorberechnungen.

    Felder:
        x, y, z: Position in Metern (kartesische Koordinaten)
        v: Zielgeschwindigkeit in km/h (Legacy-API)
        vel: Aktuelle Geschwindigkeit in m/s (Physik-Engine)
        d: Richtung in Grad (0=Nord, 90=Ost)
        i: Neigung in Grad (90=vertikal hoch, 0=horizontal, -90=vertikal runter)
        vx, vy, vz: Geschwindigkeitskomponenten in m/s
        accel_x, accel_y, accel_z: Beschleunigungskomponenten in m/s²
        dist: Zurückgelegte Distanz in Metern
        ftime: Flugzeit in Sekunden
        delta_v, delta_d, delta_i: Steuerkommandos (Änderungen)
    """

    # Position [m]
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # Geschwindigkeit (v in km/h für Legacy-API, vel in m/s für Physik)
    v: float = 0.0  # Zielgeschwindigkeit in km/h
    vel: float = 0.0  # Aktuelle Geschwindigkeit in m/s
    d: float = 90.0  # Richtung in Grad (0=Nord, 90=Ost)
    i: float = 90.0  # Neigung in Grad (90=vertikal hoch, 0=horizontal, -90=vertikal runter)

    # Geschwindigkeitskomponenten [m/s]
    vx: float = 0.0  # Geschwindigkeit in x-Richtung (Ost/West)
    vy: float = 0.0  # Geschwindigkeit in y-Richtung (Nord/Süd)
    vz: float = 0.0  # Geschwindigkeit in z-Richtung (Höhe)

    # Beschleunigung [m/s²]
    accel_x: float = 0.0
    accel_y: float = 0.0
    accel_z: float = 0.0

    # Statistik
    dist: float = 0.0
    ftime: float = 0.0

    # Steuerkommandos
    delta_v: float = 0.0
    delta_d: float = 0.0
    delta_i: float = 0.0

    @property
    def position_vector(self) -> np.ndarray:
        """3D-Positionsvektor [x, y, z] in m."""
        return np.array([self.x, self.y, self.z], dtype=np.float64)

    @property
    def velocity_vector(self) -> np.ndarray:
        """3D-Geschwindigkeitsvektor [vx, vy, vz] in m/s."""
        return np.array([self.vx, self.vy, self.vz], dtype=np.float64)

    @property
    def acceleration_vector(self) -> np.ndarray:
        """3D-Beschleunigungsvektor [ax, ay, az] in m/s²."""
        return np.array([self.accel_x, self.accel_y, self.accel_z], dtype=np.float64)
