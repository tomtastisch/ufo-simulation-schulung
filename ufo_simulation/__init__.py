"""
UFO-Simulation Schulung Package.

Ein interaktives Lermprojekt zur Programmierung von Autopiloten
für eine realistische 3D-UFO/Drohnen-Simulation.

Usage:
    from ufo_simulation import UfoSim, Autopilot

    sim = UfoSim()
    autopilot = Autopilot()
    sim.start(autopilot_callback=autopilot, show_view=True)
"""

from ufo_simulation.autopilot import Autopilot
from ufo_simulation.autopilot_base import AutopilotBase
from ufo_simulation.ufosim import (
    UfoSim,
    UfoState,
    Phase,
    ManeuverAnalysis,
    SimulationConfig,
    DEFAULT_CONFIG,
)

__version__ = "1.0.0"
__author__ = "tomtastisch"
__license__ = "MIT"

__all__ = [
    "Autopilot",
    "AutopilotBase",
    "UfoSim",
    "UfoState",
    "Phase",
    "ManeuverAnalysis",
    "SimulationConfig",
    "DEFAULT_CONFIG",
]