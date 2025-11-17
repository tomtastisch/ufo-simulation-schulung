"""
Kernmodule der UFO-Simulation-Schulung.

Bündelt die zentrale Simulation (core.simulation) und stellt sie als Package bereit.
"""

from . import simulation

__all__ = ["simulation"]