"""
Aufgabenpaket für die UFO-Simulation-Schulung.

Enthält einzelne Aufgabenmodule (z. B. Winkelaufgaben, Autopilot),
die auf den Kernmodulen unter core.* aufbauen.
"""

from . import angle, autopilot

__all__ = ["angle", "autopilot"]