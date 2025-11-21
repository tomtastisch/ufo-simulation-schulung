#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Physik-Engine für UFO-Simulation - Kernlogik für physikalische Berechnungen.

Diese Datei enthält die PhysicsEngine-Klasse, welche die gesamte physikalische
Integrationslogik für die UFO-Simulation bereitstellt.
"""

from __future__ import annotations

from dataclasses import replace as dataclass_replace
from typing import Tuple, Literal

import numpy as np

from ..infrastructure import SimulationConfig, DEFAULT_CONFIG, get_logger
from ..state import UfoState

logger = get_logger(__name__)


class PhysicsEngine:
    """
    Physik-Engine für UFO-Simulation.

    Enthält alle Berechnungen für Bewegung, Beschleunigung und Landung.
    Rein funktional - keine Seiteneffekte, arbeitet mit immutable State.
    Thread-sicher durch externes Locking (über StateManager).

    Refactored für frozen UfoState: Alle Methoden geben neue State-Instanzen zurück
    statt in-place zu modifizieren (via dataclasses.replace).
    """

    def __init__(self, config: SimulationConfig = DEFAULT_CONFIG):
        """
        Initialisiert PhysicsEngine mit Konfiguration.

        Args:
            config: Simulations-Konfiguration
        """
        self.config = config
        logger.debug(f"PhysicsEngine initialized with dt={config.dt}s, vmax={config.vmax_kmh}km/h")

    def integrate_step(self, state: UfoState) -> Tuple[UfoState, bool, bool]:
        """
        Führt einen vollständigen Physik-Integrationsschritt aus.

        Gibt neuen State und Flags zurück (immutable Pattern).

        Args:
            state: Aktueller State (wird nicht modifiziert)

        Returns:
            Tupel (updated_state, simulation_should_continue, landing_occurred)
        """
        simulation_continues = True
        landing_occurred = False

        # Working copy für Updates
        current_state = state

        # Flugzeit hochzählen wenn in der Luft
        if current_state.z > self.config.zero_value:
            current_state = dataclass_replace(current_state, ftime=current_state.ftime + self.config.dt)

        # Automatische Landungsassistenz aktivieren wenn nötig
        current_state = self._apply_landing_assistance(current_state)

        # Zustandsgrößen aktualisieren
        current_state = self._update_velocity(current_state)
        current_state = self._update_direction(current_state)
        current_state = self._update_inclination(current_state)

        # Geschwindigkeit umrechnen und Distanz akkumulieren
        vel = current_state.v * self.config.kmh_to_ms
        dist = current_state.dist + vel * self.config.dt
        current_state = dataclass_replace(current_state, vel=vel, dist=dist)

        # Position und Beschleunigung aktualisieren
        current_state, position_result = self._update_position(current_state)

        if position_result == "landed":
            landing_occurred = True
            simulation_continues = False

        return current_state, simulation_continues, landing_occurred

    def _apply_landing_assistance(self, state: UfoState) -> UfoState:
        """
        Automatische Landungsassistenz für sichere Landungen.

        Aktiviert sich bei Landephase (z < 2.0m und sinkend) und korrigiert automatisch:
        - Geschwindigkeit auf sichere Landungsgeschwindigkeit
        - Neigung auf sicheren Landewinkel
        - Sinkrate auf maximal zulässige Rate

        Wird NICHT aktiv wenn der Benutzer manuell steuert (delta_v, delta_i, delta_d != 0).

        Args:
            state: Aktueller State

        Returns:
            Aktualisierter State (oder unverändert falls keine Assistenz nötig)
        """
        # Nur aktivieren wenn:
        # 1. In Landehöhe (z < 2.0m)
        # 2. Noch nicht gelandet (z > 0)
        # 3. In Bewegung (v > 0)
        if not (self.config.zero_value < state.z <= self.config.landing_detection_height_m and state.v > 0):
            return state

        # Prüfe ob Benutzer aktiv steuert
        user_is_controlling = (
                state.delta_v != self.config.zero_value or
                state.delta_i != self.config.zero_value or
                state.delta_d != self.config.zero_value
        )

        if user_is_controlling:
            # Benutzer hat Kontrolle - keine Assistenz
            return state

        # === ASSISTENZ AKTIV ===

        updates = {}

        # 1. Geschwindigkeitsreduktion auf sichere Landungsgeschwindigkeit
        safe_v_kmh = self.config.safe_landing_v_threshold_kmh
        if state.v > safe_v_kmh:
            # Sanft abbremsen (1 km/h pro Schritt)
            reduction = min(self.config.acceleration_kmh_per_step, state.v - safe_v_kmh)
            updates['delta_v'] = -reduction
            logger.debug(f"Landing assist: reducing velocity {state.v:.1f} -> {state.v - reduction:.1f} km/h")

        # 2. Neigungskorrektur für sichere Landung
        # Ziel: Sichere Neigung zwischen -20° und -15° für Sinkflug
        # ODER: Vertikale Landung (-90°) wenn Geschwindigkeit sehr niedrig
        current_i = state.i

        # Sichere Landungsneigungen:
        # - Ideal: -20° bis -10° (sanfter Sinkflug)
        # - Akzeptabel: -90° bis -70° (vertikale Landung bei niedriger Geschwindigkeit)

        is_safe_angle = (
                (-self.config.safe_landing_inclination_max_deg <= current_i <= -10.0) or
                (-90.0 <= current_i <= -70.0)
        )

        if not is_safe_angle:
            # Neigung liegt außerhalb sicherer Bereiche -> korrigieren

            if current_i > -10.0:
                # Zu flach -> steiler machen (Richtung -15°)
                updates['delta_i'] = -self.config.inclination_step_deg
                logger.debug(f"Landing assist: increasing descent angle {current_i:.1f}° -> steeper")

            elif -70.0 < current_i < -self.config.safe_landing_inclination_max_deg:
                # Zu steil aber nicht vertikal -> abflachen (Richtung -20°)
                updates['delta_i'] = self.config.inclination_step_deg
                logger.debug(f"Landing assist: reducing descent angle {current_i:.1f}° -> shallower")

        if updates:
            return dataclass_replace(state, **updates)
        return state

    def _update_velocity(self, state: UfoState) -> UfoState:
        """
        Aktualisiert Geschwindigkeit basierend auf Sollwert-Änderung.

        Args:
            state: Aktueller State

        Returns:
            Aktualisierter State
        """
        dv = state.delta_v
        step = (dv > 0) - (dv < 0)

        if step != 0:
            new_v = state.v + step * self.config.acceleration_kmh_per_step
            clamped_v = max(0.0, min(new_v, self.config.vmax_kmh))
            new_delta_v = state.delta_v - step * self.config.acceleration_kmh_per_step
            return dataclass_replace(state, v=clamped_v, delta_v=new_delta_v)

        return state

    def _update_direction(self, state: UfoState) -> UfoState:
        """
        Aktualisiert Richtung mit Wrap-Around bei 360°.

        Args:
            state: Aktueller State

        Returns:
            Aktualisierter State
        """
        if state.delta_d != 0.0:
            new_d = (state.d + state.delta_d) % self.config.direction_full_circle_deg
            return dataclass_replace(state, d=new_d, delta_d=0.0)
        return state

    def _update_inclination(self, state: UfoState) -> UfoState:
        """
        Aktualisiert Neigung mit Clamping auf zulässigen Bereich.

        Args:
            state: Aktueller State

        Returns:
            Aktualisierter State
        """
        step = (state.delta_i > 0) - (state.delta_i < 0)

        if step != 0:
            new_i = state.i + step * self.config.inclination_step_deg
            max_d = float(self.config.inclination_max_deg)
            min_d = float(self.config.inclination_min_deg)
            clamped_i = max(min_d, min(new_i, max_d))

            new_delta_i = state.delta_i - step * self.config.inclination_step_deg
            return dataclass_replace(state, i=clamped_i, delta_i=new_delta_i)

        return state

    def _update_position(self, state: UfoState) -> Tuple[UfoState, Literal["continue", "landed"]]:
        """
        Aktualisiert Position, Geschwindigkeiten und Beschleunigungen.

        Verwendet NumPy für effiziente 3D-Vektormathematik.

        Args:
            state: Aktueller State

        Returns:
            Tupel (updated_state, result) wobei result "continue" oder "landed" ist
        """
        result: Literal["continue", "landed"] = "continue"

        if state.vel > self.config.velocity_epsilon_ms:
            # Vorherige Geschwindigkeit speichern
            if state.vx == 0.0 and state.vy == 0.0 and state.vz == 0.0 and state.ftime == 0.0:
                prev_velocity = np.array([0.0, 0.0, 0.0], dtype=np.float64)
            else:
                prev_velocity = state.velocity_vector.copy()

            # 3D-Vektormathematik mit sphärischen Koordinaten
            theta = np.radians(90.0 - state.i)
            phi = np.radians(state.d)

            direction_unit = np.array([
                np.sin(theta) * np.sin(phi),
                np.sin(theta) * np.cos(phi),
                np.cos(theta)
            ], dtype=np.float64)

            # Neue Geschwindigkeiten
            new_velocity = state.vel * direction_unit
            vx, vy, vz = new_velocity

            # Position aktualisieren
            position_delta = new_velocity * self.config.dt
            x = state.x + position_delta[0]
            y = state.y + position_delta[1]
            z = state.z + position_delta[2]

            # Beschleunigung berechnen
            if self.config.dt > self.config.zero_value:
                acceleration = (new_velocity - prev_velocity) / self.config.dt
                accel_x, accel_y, accel_z = acceleration
            else:
                accel_x, accel_y, accel_z = state.accel_x, state.accel_y, state.accel_z

            # State mit neuen Werten aktualisieren
            state = dataclass_replace(
                state,
                vx=vx, vy=vy, vz=vz,
                x=x, y=y, z=z,
                accel_x=accel_x, accel_y=accel_y, accel_z=accel_z
            )

            # Landungs-Check
            if state.z <= self.config.zero_value:
                result = "landed"
                state = self._handle_landing(state)
        else:
            # Stillstand
            updates = {
                'vx': self.config.zero_value,
                'vy': self.config.zero_value,
                'vz': self.config.zero_value,
                'accel_x': self.config.zero_value,
                'accel_y': self.config.zero_value,
                'accel_z': self.config.zero_value
            }

            # Touchdown bei geringer Höhe
            if self.config.zero_value < state.z <= self.config.landing_touchdown_z_eps:
                updates['z'] = self.config.zero_value
                updates['vel'] = self.config.zero_value
                updates['v'] = 0.0
                result = "landed"

            state = dataclass_replace(state, **updates)

        return state, result

    def _handle_landing(self, state: UfoState) -> UfoState:
        """
        Behandelt Landung: Prüft Kriterien und setzt Crash-Marker wenn nötig.

        Args:
            state: Aktueller State

        Returns:
            Aktualisierter State mit Landungsverarbeitung
        """
        # Sichere Landungskriterien prüfen
        safe_velocity = state.vel <= self.config.safe_landing_v_threshold_ms
        safe_vertical = abs(state.vz) <= self.config.safe_landing_max_vz_ms
        safe_inclination = (
                abs(state.i) <= self.config.safe_landing_inclination_max_deg
                or abs(state.i - self.config.inclination_max_deg) <= self.config.safe_landing_vertical_tolerance_deg
                or abs(state.i - self.config.inclination_min_deg) <= self.config.safe_landing_vertical_tolerance_deg
        )

        is_safe_landing = safe_velocity and safe_vertical and safe_inclination

        if not is_safe_landing:
            z_value = -self.config.one_value  # Crash-Marker
            logger.warning(
                f"CRASH: safe_v={safe_velocity} (vel={state.vel:.2f}m/s, max={self.config.safe_landing_v_threshold_ms:.2f}m/s), "
                f"safe_vz={safe_vertical} (vz={state.vz:.2f}m/s, max={self.config.safe_landing_max_vz_ms:.2f}m/s), "
                f"safe_i={safe_inclination} (i={state.i:.1f}°)"
            )
        else:
            z_value = self.config.zero_value
            logger.info(f"Safe landing at position ({state.x:.1f}, {state.y:.1f})")

        # Alle Bewegungsgrößen nullen
        return dataclass_replace(
            state,
            z=z_value,
            vel=self.config.zero_value,
            v=0.0,
            vx=self.config.zero_value,
            vy=self.config.zero_value,
            vz=self.config.zero_value
        )
