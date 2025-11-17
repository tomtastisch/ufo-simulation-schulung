"""
Kern-Simulationspaket für die UFO-Simulation-Schulung.

Stellt die zentralen Klassen und Konfigurationen der Simulation bereit.
"""

from .autopilot_base import AutopilotBase
from .ufosim import (
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
    "AutopilotBase",
    "UfoSim",
    "UfoState",
    "Phase",
    "ManeuverAnalysis",
    "SimulationConfig",
    "DEFAULT_CONFIG",
]