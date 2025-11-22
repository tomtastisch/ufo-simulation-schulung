"""
Infrastruktur-Komponenten für die UFO-Simulation.

Stellt grundlegende Dienste bereit (Konfiguration, Logging) ohne
Simulationslogik. Framework-unabhängig und thread-sicher.
"""
from core.simulation.infrastructure.config.logging import configure_logging, get_logger
from core.simulation.infrastructure.config.simulation import SimulationConfig, DEFAULT_CONFIG

__all__ = [
    "SimulationConfig",
    "DEFAULT_CONFIG",
    "configure_logging",
    "get_logger",
]
