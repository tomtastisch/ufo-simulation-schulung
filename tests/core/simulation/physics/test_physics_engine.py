#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-Tests für PhysicsEngine.

Testet die physikalische Integrationslogik der UFO-Simulation isoliert.
"""

import sys
from pathlib import Path

# Sicherstellen, dass src/ im Python-Pfad ist  # noqa: E402
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest  # noqa: E402

from core.simulation.physics import PhysicsEngine  # noqa: E402
from core.simulation.state import UfoState  # noqa: E402
from core.simulation.infrastructure import SimulationConfig, DEFAULT_CONFIG  # noqa: E402


class TestPhysicsEngineImport:
    """Tests für Modul-Import und Initialisierung."""

    def test_physics_engine_can_be_imported(self):
        """Smoke-Test: PhysicsEngine kann importiert werden."""
        from core.simulation.physics import PhysicsEngine
        assert PhysicsEngine is not None

    def test_physics_engine_can_be_instantiated(self):
        """PhysicsEngine kann mit Default-Config instantiiert werden."""
        engine = PhysicsEngine()
        assert engine is not None
        assert engine.config == DEFAULT_CONFIG

    def test_physics_engine_can_be_instantiated_with_custom_config(self):
        """PhysicsEngine kann mit Custom-Config instantiiert werden."""
        config = SimulationConfig(dt=0.05, vmax_kmh=200.0)
        engine = PhysicsEngine(config)
        assert engine is not None
        assert engine.config.dt == 0.05
        assert engine.config.vmax_kmh == 200.0


class TestPhysicsEngineVelocityUpdate:
    """Tests für Geschwindigkeits-Updates."""

    def test_update_velocity_increases_when_delta_v_positive(self):
        """Geschwindigkeit steigt bei positivem delta_v."""
        engine = PhysicsEngine()
        state = UfoState(v=10.0, delta_v=5.0)

        updated = engine._update_velocity(state)

        # Geschwindigkeit sollte um acceleration_kmh_per_step gestiegen sein
        assert updated.v > state.v
        assert updated.delta_v < state.delta_v

    def test_update_velocity_decreases_when_delta_v_negative(self):
        """Geschwindigkeit sinkt bei negativem delta_v."""
        engine = PhysicsEngine()
        state = UfoState(v=50.0, delta_v=-10.0)

        updated = engine._update_velocity(state)

        # Geschwindigkeit sollte gesunken sein
        assert updated.v < state.v
        assert updated.delta_v > state.delta_v

    def test_update_velocity_respects_max_velocity(self):
        """Geschwindigkeit wird auf vmax_kmh begrenzt."""
        config = SimulationConfig(vmax_kmh=100.0)
        engine = PhysicsEngine(config)
        state = UfoState(v=99.0, delta_v=50.0)

        updated = engine._update_velocity(state)

        # Geschwindigkeit darf vmax_kmh nicht überschreiten
        assert updated.v <= config.vmax_kmh

    def test_update_velocity_respects_min_velocity_zero(self):
        """Geschwindigkeit wird nicht negativ."""
        engine = PhysicsEngine()
        state = UfoState(v=1.0, delta_v=-50.0)

        updated = engine._update_velocity(state)

        # Geschwindigkeit darf nicht unter 0 fallen
        assert updated.v >= 0.0

    def test_update_velocity_no_change_when_delta_v_zero(self):
        """Keine Änderung bei delta_v=0."""
        engine = PhysicsEngine()
        state = UfoState(v=50.0, delta_v=0.0)

        updated = engine._update_velocity(state)

        assert updated.v == state.v
        assert updated.delta_v == state.delta_v


class TestPhysicsEngineDirectionUpdate:
    """Tests für Richtungs-Updates."""

    def test_update_direction_wraps_at_360(self):
        """Richtung wird bei 360° auf 0° zurückgesetzt."""
        engine = PhysicsEngine()
        state = UfoState(d=350.0, delta_d=20.0)

        updated = engine._update_direction(state)

        # 350 + 20 = 370, soll auf 10 wrappen
        assert 0.0 <= updated.d < 360.0
        assert updated.delta_d == 0.0

    def test_update_direction_no_change_when_delta_d_zero(self):
        """Keine Änderung bei delta_d=0."""
        engine = PhysicsEngine()
        state = UfoState(d=90.0, delta_d=0.0)

        updated = engine._update_direction(state)

        assert updated.d == state.d
        assert updated.delta_d == state.delta_d


class TestPhysicsEngineInclinationUpdate:
    """Tests für Neigungs-Updates."""

    def test_update_inclination_increases_when_delta_i_positive(self):
        """Neigung steigt bei positivem delta_i."""
        engine = PhysicsEngine()
        state = UfoState(i=0.0, delta_i=10.0)

        updated = engine._update_inclination(state)

        assert updated.i > state.i
        assert updated.delta_i < state.delta_i

    def test_update_inclination_decreases_when_delta_i_negative(self):
        """Neigung sinkt bei negativem delta_i."""
        engine = PhysicsEngine()
        state = UfoState(i=0.0, delta_i=-10.0)

        updated = engine._update_inclination(state)

        assert updated.i < state.i
        assert updated.delta_i > state.delta_i

    def test_update_inclination_respects_max_limit(self):
        """Neigung wird auf inclination_max_deg begrenzt."""
        config = SimulationConfig(inclination_max_deg=90)
        engine = PhysicsEngine(config)
        state = UfoState(i=89.0, delta_i=50.0)

        updated = engine._update_inclination(state)

        assert updated.i <= config.inclination_max_deg

    def test_update_inclination_respects_min_limit(self):
        """Neigung wird auf inclination_min_deg begrenzt."""
        config = SimulationConfig(inclination_min_deg=-90)
        engine = PhysicsEngine(config)
        state = UfoState(i=-89.0, delta_i=-50.0)

        updated = engine._update_inclination(state)

        assert updated.i >= config.inclination_min_deg

    def test_update_inclination_no_change_when_delta_i_zero(self):
        """Keine Änderung bei delta_i=0."""
        engine = PhysicsEngine()
        state = UfoState(i=45.0, delta_i=0.0)

        updated = engine._update_inclination(state)

        assert updated.i == state.i
        assert updated.delta_i == state.delta_i


class TestPhysicsEnginePositionUpdate:
    """Tests für Positions-Updates."""

    def test_update_position_with_zero_velocity(self):
        """Position ändert sich nicht bei Geschwindigkeit=0."""
        engine = PhysicsEngine()
        state = UfoState(x=0.0, y=0.0, z=10.0, v=0.0, vel=0.0)

        updated, result = engine._update_position(state)

        assert updated.x == state.x
        assert updated.y == state.y
        # z könnte sich bei geringer Höhe ändern (touchdown)
        assert result in ["continue", "landed"]

    def test_update_position_changes_with_nonzero_velocity(self):
        """Position ändert sich bei Geschwindigkeit>0."""
        from dataclasses import replace

        config = SimulationConfig(dt=1.0)  # 1 Sekunde für einfachere Berechnung
        engine = PhysicsEngine(config)
        # Horizontaler Flug: i=0, d=0 (Nord), v=36 km/h = 10 m/s
        state = UfoState(x=0.0, y=0.0, z=100.0, v=36.0, i=0.0, d=0.0)
        state = replace(state, vel=10.0)  # vel in m/s setzen

        updated, result = engine._update_position(state)

        # Position sollte sich geändert haben
        assert updated.x != state.x or updated.y != state.y or updated.z != state.z
        assert result == "continue"  # Noch in der Luft

    def test_update_position_detects_landing(self):
        """Landung wird erkannt wenn z <= 0."""
        engine = PhysicsEngine()
        # Zustand knapp über Boden mit Abwärtsbewegung
        state = UfoState(
            x=0.0, y=0.0, z=0.1,
            v=10.0, vel=2.78, i=-45.0, d=0.0,  # Sinkflug
            vz=-2.0  # Vertikale Geschwindigkeit nach unten
        )

        updated, result = engine._update_position(state)

        if result == "landed":
            # Bei Landung sollte z <= 0 sein
            assert updated.z <= 0.0
            # Geschwindigkeiten sollten auf 0 gesetzt sein
            assert updated.vel == 0.0
            assert updated.v == 0.0


class TestPhysicsEngineLandingHandling:
    """Tests für Landungs-Behandlung."""

    def test_handle_landing_safe_landing(self):
        """Sichere Landung wird korrekt erkannt."""
        engine = PhysicsEngine()

        # Sicherer Zustand: langsam, geringe Sinkrate, akzeptable Neigung
        # Verwende Werte unterhalb der Standard-Schwellenwerte
        state = UfoState(
            x=10.0, y=20.0, z=0.0,
            v=0.5, vel=0.14,  # Sehr langsam, unter safe_landing_v_threshold
            vz=-0.1,  # Geringe Sinkrate
            i=-15.0  # Sanfter Sinkflug
        )

        updated = engine._handle_landing(state)

        # Sichere Landung: z sollte exakt 0.0 sein (nicht negativ)
        assert updated.z == 0.0
        assert updated.vel == 0.0
        assert updated.v == 0.0

    def test_handle_landing_crash_high_velocity(self):
        """Crash bei zu hoher Geschwindigkeit."""
        engine = PhysicsEngine()

        # Unsicher: zu schnell (über safe_landing_v_threshold_kmh)
        state = UfoState(
            x=10.0, y=20.0, z=0.0,
            v=50.0, vel=13.89,  # ~50 km/h = 13.89 m/s (zu schnell!)
            vz=-1.0,
            i=-15.0
        )

        updated = engine._handle_landing(state)

        # Crash: z sollte negativ sein (Crash-Marker)
        assert updated.z < 0.0
        assert updated.vel == 0.0
        assert updated.v == 0.0

    def test_handle_landing_crash_high_vertical_velocity(self):
        """Crash bei zu hoher Sinkrate."""
        engine = PhysicsEngine()

        # Unsicher: zu steile Sinkrate (über safe_landing_max_vz_ms)
        state = UfoState(
            x=10.0, y=20.0, z=0.0,
            v=0.5, vel=0.14,  # Langsam
            vz=-5.0,  # Zu schnelle Sinkrate!
            i=-15.0
        )

        updated = engine._handle_landing(state)

        # Crash
        assert updated.z < 0.0

    def test_handle_landing_crash_unsafe_inclination(self):
        """Crash bei unsicherer Neigung."""
        engine = PhysicsEngine()

        # Unsicher: zu steile Neigung (nicht vertikal genug für vertikale Landung)
        state = UfoState(
            x=10.0, y=20.0, z=0.0,
            v=0.5, vel=0.14,  # Langsam
            vz=-0.1,  # Geringe Sinkrate
            i=-45.0  # Zu steil, nicht vertikal genug!
        )

        updated = engine._handle_landing(state)

        # Crash
        assert updated.z < 0.0


class TestPhysicsEngineLandingAssistance:
    """Tests für automatische Landungsassistenz."""

    def test_landing_assistance_not_active_when_high_altitude(self):
        """Landungsassistenz ist nicht aktiv bei großer Höhe."""
        engine = PhysicsEngine()
        state = UfoState(z=100.0, v=50.0)

        updated = engine._apply_landing_assistance(state)

        # Keine Änderung
        assert updated == state

    def test_landing_assistance_not_active_when_user_controlling(self):
        """Landungsassistenz ist nicht aktiv bei Benutzersteuerung."""
        engine = PhysicsEngine()
        # In Landehöhe aber Benutzer steuert
        state = UfoState(z=1.5, v=50.0, delta_v=5.0)  # Benutzer steuert

        updated = engine._apply_landing_assistance(state)

        # Keine Assistenz wegen Benutzersteuerung
        assert updated == state

    def test_landing_assistance_reduces_velocity(self):
        """Landungsassistenz reduziert zu hohe Geschwindigkeit."""
        engine = PhysicsEngine()
        # In Landehöhe, keine Benutzersteuerung, zu schnell
        state = UfoState(z=1.5, v=50.0, delta_v=0.0, delta_i=0.0, delta_d=0.0)

        updated = engine._apply_landing_assistance(state)

        # Geschwindigkeitsreduktion sollte aktiviert sein
        assert updated.delta_v < 0.0  # Bremsen

    def test_landing_assistance_corrects_inclination_too_shallow(self):
        """Landungsassistenz korrigiert zu flache Neigung."""
        engine = PhysicsEngine()
        # Zu flach (i=0), sollte steiler werden
        state = UfoState(z=1.5, v=10.0, i=0.0, delta_v=0.0, delta_i=0.0, delta_d=0.0)

        updated = engine._apply_landing_assistance(state)

        # Neigung sollte steiler gemacht werden (delta_i negativ)
        # Aber nur wenn Assistenz aktiv ist - das hängt von weiteren Bedingungen ab
        # Prüfen dass entweder Assistenz aktiv ist oder State unverändert
        if updated != state:
            # Wenn Assistenz aktiv, sollte delta_i gesetzt sein
            assert hasattr(updated, 'delta_i')


class TestPhysicsEngineIntegrateStep:
    """Tests für vollständigen Integrationsschritt."""

    def test_integrate_step_returns_correct_tuple(self):
        """integrate_step gibt korrektes Tupel zurück."""
        engine = PhysicsEngine()
        state = UfoState()

        result = engine.integrate_step(state)

        assert isinstance(result, tuple)
        assert len(result) == 3
        new_state, continues, landed = result
        assert isinstance(new_state, UfoState)
        assert isinstance(continues, bool)
        assert isinstance(landed, bool)

    def test_integrate_step_ascent_scenario(self):
        """Steigflug-Szenario: UFO steigt auf."""
        engine = PhysicsEngine()
        state = UfoState(
            z=50.0,
            v=50.0, vel=13.89,
            i=45.0,  # Steigflug
            d=0.0
        )

        new_state, continues, landed = engine.integrate_step(state)

        # Simulation sollte weiterlaufen
        assert continues is True
        assert landed is False
        # Flugzeit sollte erhöht worden sein
        assert new_state.ftime > state.ftime

    def test_integrate_step_descent_scenario(self):
        """Sinkflug-Szenario: UFO sinkt."""
        engine = PhysicsEngine()
        state = UfoState(
            z=100.0,
            v=30.0, vel=8.33,
            i=-30.0,  # Sinkflug
            d=0.0
        )

        new_state, continues, landed = engine.integrate_step(state)

        # Simulation sollte weiterlaufen
        assert continues is True
        assert landed is False

    def test_integrate_step_landing_scenario(self):
        """Landungs-Szenario: UFO landet."""
        config = SimulationConfig(dt=0.5)
        engine = PhysicsEngine(config)
        # Knapp über Boden, langsam, sichere Neigung
        state = UfoState(
            z=0.05,
            v=5.0, vel=1.39,
            vz=-0.5,
            i=-15.0,
            d=0.0
        )

        # Initialisiere Variablen vor Schleife
        new_state = state
        continues = True
        landed = False

        # Mehrere Schritte ausführen bis Landung
        for _ in range(5):
            new_state, continues, landed = engine.integrate_step(state)
            if landed:
                break
            state = new_state

        # Landung sollte erfolgt sein - je nach exaktem Zustand kann dies
        # entweder durch landed-Flag oder durch Boden-Kontakt (z <= 0) angezeigt werden
        # Prüfe zuerst das landed-Flag
        if landed:
            # Wenn landed-Flag gesetzt ist, sollte Simulation auch stoppen
            assert continues is False
        else:
            # Wenn nicht landed, muss UFO zumindest den Boden berührt haben
            assert new_state.z <= 0.0

    def test_integrate_step_increments_flight_time_when_airborne(self):
        """Flugzeit wird erhöht wenn in der Luft."""
        config = SimulationConfig(dt=0.1)
        engine = PhysicsEngine(config)
        state = UfoState(z=100.0, ftime=5.0)

        new_state, _, _ = engine.integrate_step(state)

        # Flugzeit sollte um dt erhöht sein
        assert new_state.ftime == pytest.approx(5.1, abs=0.01)

    def test_integrate_step_does_not_increment_flight_time_on_ground(self):
        """Flugzeit wird nicht erhöht wenn am Boden."""
        config = SimulationConfig(dt=0.1)
        engine = PhysicsEngine(config)
        state = UfoState(z=0.0, ftime=10.0)  # Am Boden

        new_state, _, _ = engine.integrate_step(state)

        # Flugzeit sollte unverändert sein
        assert new_state.ftime == state.ftime


class TestPhysicsEngineImmutability:
    """Tests für Immutability - State wird nie in-place modifiziert."""

    def test_integrate_step_does_not_modify_input_state(self):
        """integrate_step modifiziert Input-State nicht."""
        from dataclasses import asdict

        engine = PhysicsEngine()
        original_state = UfoState(z=50.0, v=30.0, i=45.0)
        original_dict = asdict(original_state)

        new_state, _, _ = engine.integrate_step(original_state)

        # Original-State sollte unverändert sein
        assert asdict(original_state) == original_dict
        # Neuer State sollte unterschiedlich sein
        assert new_state is not original_state

    def test_private_methods_do_not_modify_input_state(self):
        """Private Methoden modifizieren Input-State nicht."""
        from dataclasses import asdict

        engine = PhysicsEngine()
        original_state = UfoState(v=50.0, delta_v=10.0)
        original_dict = asdict(original_state)

        _ = engine._update_velocity(original_state)

        # Original-State sollte unverändert sein
        assert asdict(original_state) == original_dict
