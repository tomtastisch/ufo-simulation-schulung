"""
Physik-Engine für UFO-Simulation.

Kapselt physikalische Berechnungslogik für Bewegung, Beschleunigung
und Landung. Unabhängig von Threading und Zustandsverwaltung.

Komponenten:
    - PhysicsEngine: Zeitschritt-basierte Integration mit 3D-Vektorrechnung
"""

from .engine import PhysicsEngine

__all__ = ['PhysicsEngine']


