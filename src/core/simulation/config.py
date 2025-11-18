#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zentrale Konfigurationsschicht für UFO-Simulation.

Alle physikalischen Parameter, Schwellenwerte und Visualisierungs-Einstellungen
sind hier definiert. Keine Magic Numbers im Code!

Immutable (frozen=True) für thread-sichere Verwendung.
"""

from __future__ import annotations
from dataclasses import dataclass

from .exceptions import ConfigError


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """
    Zentrale Konfigurationsklasse für alle physikalischen Parameter.

    Alle Basisparameter und abgeleiteten Schwellenwerte sind hier definiert.
    Immutable (frozen=True) für thread-sichere Verwendung.

    Raises:
        ConfigError: Wenn Parameter ungültig oder inkonsistent sind
    """

    # === Basis-Physik-Parameter ===
    dt: float = 0.1  # Zeitschritt in Sekunden
    vmax_kmh: float = 15.0  # Maximale Geschwindigkeit in km/h
    acceleration_kmh_per_step: float = 1.0  # Beschleunigung pro Schritt in km/h

    # UAV-Geometrie
    uav_radius_m: float = 0.5  # Radius des UAV in Metern
    uav_height_m: float = 0.3  # Höhe des UAV in Metern

    # Maximale Beschleunigungen
    max_lateral_accel_ms2: float = 5.0  # Maximale Querbeschleunigung in m/s²
    max_vertical_accel_ms2: float = 3.0  # Maximale vertikale Beschleunigung in m/s²

    # Winkel-Parameter
    inclination_min_deg: int = -90
    inclination_max_deg: int = 90
    inclination_step_deg: int = 1
    direction_full_circle_deg: int = 360

    # === Abgeleitete Schwellenwerte (automatisch berechnet) ===
    @property
    def vmax_ms(self) -> float:
        """Maximale Geschwindigkeit in m/s."""
        return self.vmax_kmh / 3.6

    @property
    def kmh_to_ms(self) -> float:
        """Umrechnungsfaktor km/h zu m/s."""
        return 1.0 / 3.6

    # Landungsparameter
    safe_landing_v_absolute_kmh: float = 1.0  # Absolute sichere Landungsgeschwindigkeit
    safe_landing_v_relative_factor: float = 0.15  # Relative sichere Geschwindigkeit (Faktor von vmax)
    safe_landing_max_vz_absolute_ms: float = 1.0  # Maximale sichere vertikale Geschwindigkeit

    @property
    def safe_landing_v_threshold_kmh(self) -> float:
        """Sichere Landegeschwindigkeit (min von absolut und relativ)."""
        return min(self.safe_landing_v_absolute_kmh, self.vmax_kmh * self.safe_landing_v_relative_factor)

    @property
    def safe_landing_v_threshold_ms(self) -> float:
        """Sichere Lande-Geschwindigkeit in m/s."""
        return self.safe_landing_v_threshold_kmh * self.kmh_to_ms

    @property
    def safe_landing_max_vz_ms(self) -> float:
        """Maximale vertikale Geschwindigkeit für sichere Landung in m/s."""
        return self.safe_landing_max_vz_absolute_ms

    @property
    def landing_touchdown_z_eps(self) -> float:
        """Höhen-Epsilon für Touchdown (abgeleitet von UAV-Geometrie)."""
        return self.uav_height_m * 0.33  # ~0.1m bei height=0.3m

    @property
    def max_sink_rate_ms(self) -> float:
        """Maximale sichere Sinkrate in m/s."""
        return 2.0

    @property
    def safe_landing_inclination_max_deg(self) -> float:
        """Maximale sichere Neigung bei Landung in Grad."""
        return 20.0

    @property
    def safe_landing_vertical_tolerance_deg(self) -> float:
        """Toleranz für nahezu-vertikale Landung in Grad."""
        return 20.0

    @property
    def landing_detection_height_m(self) -> float:
        """Höhe für Landungsphasen-Detektion in Metern."""
        return 2.0

    # === Visualisierungsparameter ===
    window_size: int = 600
    update_interval_ms: int = 100
    shutdown_delay_ms: int = 1000
    crash_display_duration_ms: int = 2000

    # Viewport
    view_margin_factor: float = 0.8
    view_min_scaling: int = 1
    view_max_scaling: int = 100
    min_coordinate_epsilon: float = 1.0

    # HUD-Elemente
    hud_start_radius: float = 6.0
    hud_dest_out_radius: float = 6.0
    hud_dest_in_radius: float = 3.0
    hud_ufo_dot_radius: float = 4.0
    hud_text_margin: float = 12.0
    hud_text_line_height: float = 13.0
    hud_scale_length_m: float = 10.0

    # === Simulation-Steuerung ===
    speedup_min: int = 1
    speedup_max: int = 25
    speedup_default: int = 1

    # === Numerische Stabilität ===
    velocity_epsilon_ms: float = 0.001
    zero_value: float = 0.0
    one_value: float = 1.0

    # === Manöver-Erkennung ===
    observer_history_size: int = 50  # Anzahl der gespeicherten Zustände
    stagnation_distance_threshold_m: float = 0.1  # Minimale Bewegung für Nicht-Stagnation
    turn_heading_threshold_deg: float = 5.0  # Minimale Richtungsänderung für Turn-Detektion
    climb_vz_threshold_ms: float = 0.5  # Minimale vz für Steigflug-Detektion
    descent_vz_threshold_ms: float = -0.5  # Maximale vz für Sinkflug-Detektion


def validate_config(config: SimulationConfig) -> None:
    """
    Validiert Konfigurationsparameter.

    Args:
        config: Zu validierende Konfiguration

    Raises:
        ConfigError: Wenn Parameter ungültig sind
    """
    # Physik-Parameter
    if config.dt <= 0:
        raise ConfigError(f"dt muss positiv sein, ist aber {config.dt}")
    if config.vmax_kmh <= 0:
        raise ConfigError(f"vmax_kmh muss positiv sein, ist aber {config.vmax_kmh}")

    # Geometrie
    if config.uav_radius_m <= 0:
        raise ConfigError(f"uav_radius_m muss positiv sein, ist aber {config.uav_radius_m}")
    if config.uav_height_m <= 0:
        raise ConfigError(f"uav_height_m muss positiv sein, ist aber {config.uav_height_m}")

    # Winkel
    if not -90 <= config.inclination_min_deg <= 90:
        raise ConfigError(f"inclination_min_deg muss zwischen -90 und 90 liegen, ist aber {config.inclination_min_deg}")
    if not -90 <= config.inclination_max_deg <= 90:
        raise ConfigError(f"inclination_max_deg muss zwischen -90 und 90 liegen, ist aber {config.inclination_max_deg}")

    # Speedup
    if config.speedup_min < 1:
        raise ConfigError(f"speedup_min muss >= 1 sein, ist aber {config.speedup_min}")
    if config.speedup_max < config.speedup_min:
        raise ConfigError(f"speedup_max ({config.speedup_max}) muss >= speedup_min ({config.speedup_min}) sein")


# Globale Default-Konfiguration
DEFAULT_CONFIG = SimulationConfig()
validate_config(DEFAULT_CONFIG)  # Validiere bei Modul-Import

