#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigurationsklasse für Simulationsparameter.

Copyright (C) 2013-2025 R. Gold, tomtastisch (i-ki 1)
Version: 5.2.0-tw-refactored
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """
    Immutable Konfigurationsklasse mit allen physikalischen und visuellen Parametern.

    Basis-Parameter sind als Instanzvariablen mit Defaults definiert.
    Abgeleitete Werte werden als Properties berechnet.
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
    observer_analysis_window_size: int = 10  # Anzahl der Zustände für Trend-Analyse
    stagnation_movement_threshold_ratio: float = 0.5  # Bewegungsschwelle (Faktor der erwarteten Bewegung)
    turn_heading_threshold_deg: float = 5.0  # Minimale Richtungsänderung für Turn-Detektion
    climb_vz_threshold_ms: float = 0.5  # Minimale vz für Steigflug-Detektion
    descent_vz_threshold_ms: float = -0.5  # Maximale vz für Sinkflug-Detektion


# Globale Standard-Konfiguration
# Diese wird als Fallback verwendet, wenn keine explizite Konfiguration übergeben wird
DEFAULT_CONFIG = SimulationConfig()
