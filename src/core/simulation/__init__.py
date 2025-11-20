"""
Kern-Simulationspaket für die UFO-Simulation-Schulung.

Stellt die zentralen Klassen und Konfigurationen der Simulation bereit.
"""

from .autopilot_base import AutopilotBase
from .infrastructure import DEFAULT_CONFIG, SimulationConfig
from .state import UfoState
from .ufosim import (
    UfoSim,
    Phase,
    ManeuverAnalysis,
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