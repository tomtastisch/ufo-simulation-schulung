#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-Tests für das Observer-Modul (Phasen- und Manöver-Analyse).

Testet:
    - compute_phase() für alle 6 Phasen
    - Prioritätsreihenfolge der Phasen
    - StateObserver.analyze() mit synthetischen Zustandsverläufen
    - Manöver-Flags (is_ascending, is_descending, is_turning, is_stagnating)
"""

import pytest

from core.simulation.infrastructure import DEFAULT_CONFIG, SimulationConfig
from core.simulation.observer import ManeuverAnalysis, StateObserver, compute_phase
from core.simulation.state import UfoState


# =============================================================================
# Tests für compute_phase()
# =============================================================================

class TestComputePhase:
    """Tests für die Phasenbestimmung aus dem aktuellen Zustand."""

    def test_phase_idle_at_start(self):
        """Phase 'idle' wenn am Boden, noch nie geflogen."""
        state = UfoState(x=0.0, y=0.0, z=0.0, v=0.0, vel=0.0, dist=0.0, ftime=0.0)
        phase = compute_phase(state, DEFAULT_CONFIG)
        assert phase == "idle"

    def test_phase_crashed_when_z_negative(self):
        """Phase 'crashed' hat höchste Priorität (z < 0)."""
        state = UfoState(z=-1.0, v=10.0, dist=100.0, ftime=10.0)
        phase = compute_phase(state, DEFAULT_CONFIG)
        assert phase == "crashed"

    def test_phase_crashed_priority_over_others(self):
        """Crash-Phase hat Priorität über alle anderen Phasen."""
        # Auch wenn andere Bedingungen erfüllt sind (v > 0, has_flown, etc.)
        state = UfoState(z=-0.5, v=15.0, vel=4.17, dist=200.0, ftime=20.0)
        phase = compute_phase(state, DEFAULT_CONFIG)
        assert phase == "crashed"

    def test_phase_landed_after_flight(self):
        """Phase 'landed' wenn am Boden, v=0, und schon geflogen."""
        state = UfoState(z=0.0, v=0.0, vel=0.0, dist=100.0, ftime=10.0)
        phase = compute_phase(state, DEFAULT_CONFIG)
        assert phase == "landed"

    def test_phase_landed_requires_has_flown(self):
        """Phase 'landed' erfordert dist > 0 oder ftime > 0."""
        # dist > 0
        state1 = UfoState(z=0.0, v=0.0, vel=0.0, dist=1.0, ftime=0.0)
        assert compute_phase(state1, DEFAULT_CONFIG) == "landed"

        # ftime > 0
        state2 = UfoState(z=0.0, v=0.0, vel=0.0, dist=0.0, ftime=1.0)
        assert compute_phase(state2, DEFAULT_CONFIG) == "landed"

        # Beide 0 → idle
        state3 = UfoState(z=0.0, v=0.0, vel=0.0, dist=0.0, ftime=0.0)
        assert compute_phase(state3, DEFAULT_CONFIG) == "idle"

    def test_phase_takeoff_just_lifted(self):
        """Phase 'takeoff' beim Abheben (ftime == 0, v > 0, z > 0)."""
        state = UfoState(z=5.0, v=10.0, vel=2.78, ftime=0.0, dist=0.0)
        phase = compute_phase(state, DEFAULT_CONFIG)
        assert phase == "takeoff"

    def test_phase_landing_descending_near_ground(self):
        """Phase 'landing' bei Sinkflug nahe Boden."""
        config = DEFAULT_CONFIG
        # vz < 0, v > 0, 0 < z <= landing_detection_height_m
        state = UfoState(
            z=config.landing_detection_height_m - 1.0,
            v=10.0,
            vel=2.78,
            vz=-2.0,  # Sinkflug
            dist=50.0,
            ftime=5.0
        )
        phase = compute_phase(state, config)
        assert phase == "landing"

    def test_phase_landing_requires_descending(self):
        """Phase 'landing' erfordert vz < 0."""
        config = DEFAULT_CONFIG
        # vz >= 0 → nicht landing
        state = UfoState(
            z=config.landing_detection_height_m - 1.0,
            v=10.0,
            vel=2.78,
            vz=0.5,  # Steigend oder level
            dist=50.0,
            ftime=5.0
        )
        phase = compute_phase(state, config)
        assert phase != "landing"
        assert phase == "flying"

    def test_phase_landing_requires_low_altitude(self):
        """Phase 'landing' erfordert z <= landing_detection_height_m."""
        config = DEFAULT_CONFIG
        # z zu hoch → flying statt landing
        state = UfoState(
            z=config.landing_detection_height_m + 1.0,
            v=10.0,
            vel=2.78,
            vz=-2.0,
            dist=50.0,
            ftime=5.0
        )
        phase = compute_phase(state, config)
        assert phase == "flying"

    def test_phase_flying_normal_flight(self):
        """Phase 'flying' während normaler Flugphase."""
        state = UfoState(z=50.0, v=15.0, vel=4.17, dist=100.0, ftime=10.0)
        phase = compute_phase(state, DEFAULT_CONFIG)
        assert phase == "flying"

    def test_phase_priority_order(self):
        """Verifiziert die Prioritätsreihenfolge der Phasen."""
        # 1. crashed > landed
        state1 = UfoState(z=-1.0, v=0.0, dist=100.0, ftime=10.0)
        assert compute_phase(state1, DEFAULT_CONFIG) == "crashed"

        # 2. landed > takeoff (beide am Boden, aber landed hat Priorität)
        # (takeoff erfordert z > 0, daher kein Konflikt)

        # 3. takeoff > landing
        config = DEFAULT_CONFIG
        state3 = UfoState(
            z=config.landing_detection_height_m - 1.0,
            v=10.0,
            vz=-1.0,
            ftime=0.0  # ftime=0 → takeoff hat Priorität
        )
        assert compute_phase(state3, config) == "takeoff"

        # 4. landing > flying (bei gleichen Bedingungen)
        state4 = UfoState(
            z=config.landing_detection_height_m - 1.0,
            v=10.0,
            vz=-1.0,
            ftime=5.0
        )
        assert compute_phase(state4, config) == "landing"

    def test_phase_with_custom_config(self):
        """Phase-Bestimmung funktioniert mit custom Config."""
        # Da landing_detection_height_m eine Property ist (hardcoded 2.0),
        # testen wir mit einem anderen Parameter
        custom_config = SimulationConfig(dt=0.05)
        state = UfoState(z=1.5, v=10.0, vz=-1.0, ftime=5.0)

        # Mit beiden configs sollte landing erkannt werden (z < 2.0, vz < 0)
        phase = compute_phase(state, custom_config)
        assert phase == "landing"

        phase_default = compute_phase(state, DEFAULT_CONFIG)
        assert phase_default == "landing"


# =============================================================================
# Tests für StateObserver
# =============================================================================

class TestStateObserver:
    """Tests für historien-basierte Manöver-Analyse."""

    def test_observer_initialization(self):
        """Observer wird korrekt initialisiert."""
        observer = StateObserver(DEFAULT_CONFIG)
        assert observer.config == DEFAULT_CONFIG
        assert len(observer.history) == 0
        assert observer.history.maxlen == DEFAULT_CONFIG.observer_history_size

    def test_observer_observe_adds_state(self):
        """observe() fügt State zur Historie hinzu."""
        observer = StateObserver(DEFAULT_CONFIG)
        state = UfoState(z=10.0, v=15.0)

        observer.observe(state)
        assert len(observer.history) == 1
        assert observer.history[0].z == 10.0

    def test_observer_observe_creates_snapshot(self):
        """observe() erstellt einen Snapshot (via dataclass_replace)."""
        observer = StateObserver(DEFAULT_CONFIG)
        state = UfoState(z=10.0, v=15.0)

        observer.observe(state)
        # State in History sollte ein Copy sein
        assert observer.history[0] is not state
        assert observer.history[0].z == state.z

    def test_observer_history_is_ring_buffer(self):
        """History ist ein Ringpuffer mit maxlen."""
        config = SimulationConfig(observer_history_size=3)
        observer = StateObserver(config)

        for i in range(5):
            observer.observe(UfoState(z=float(i)))

        # Nur die letzten 3 sollten gespeichert sein
        assert len(observer.history) == 3
        assert observer.history[0].z == 2.0
        assert observer.history[1].z == 3.0
        assert observer.history[2].z == 4.0

    def test_analyze_empty_history_returns_idle(self):
        """analyze() ohne History gibt 'idle' zurück."""
        observer = StateObserver(DEFAULT_CONFIG)
        analysis = observer.analyze()

        assert isinstance(analysis, ManeuverAnalysis)
        assert analysis.phase == "idle"
        assert not analysis.is_ascending
        assert not analysis.is_descending

    def test_analyze_single_state(self):
        """analyze() mit einem State funktioniert."""
        observer = StateObserver(DEFAULT_CONFIG)
        observer.observe(UfoState(z=10.0, v=15.0, ftime=1.0))

        analysis = observer.analyze()
        assert analysis.phase == "flying"

    def test_analyze_detects_ascending(self):
        """analyze() erkennt Steigflug (is_ascending)."""
        config = SimulationConfig(climb_vz_threshold_ms=0.5)
        observer = StateObserver(config)

        # Synthetischer Steigflug
        for i in range(10):
            state = UfoState(z=float(i), vz=1.0, v=10.0, ftime=float(i))
            observer.observe(state)

        analysis = observer.analyze()
        assert analysis.is_ascending
        assert not analysis.is_descending
        assert analysis.avg_vz == pytest.approx(1.0, abs=0.01)

    def test_analyze_detects_descending(self):
        """analyze() erkennt Sinkflug (is_descending)."""
        config = SimulationConfig(descent_vz_threshold_ms=-0.5)
        observer = StateObserver(config)

        # Synthetischer Sinkflug
        for i in range(10):
            state = UfoState(z=100.0 - float(i), vz=-1.5, v=10.0, ftime=float(i))
            observer.observe(state)

        analysis = observer.analyze()
        assert analysis.is_descending
        assert not analysis.is_ascending
        assert analysis.avg_vz == pytest.approx(-1.5, abs=0.01)

    def test_analyze_detects_turning(self):
        """analyze() erkennt Drehung (is_turning)."""
        config = SimulationConfig(turn_heading_threshold_deg=5.0)
        observer = StateObserver(config)

        # Synthetische Drehung (10° pro Schritt)
        for i in range(10):
            state = UfoState(d=float(i * 10), v=10.0, z=50.0, ftime=float(i))
            observer.observe(state)

        analysis = observer.analyze()
        assert analysis.is_turning
        assert analysis.avg_heading_change == pytest.approx(10.0, abs=0.01)

    def test_analyze_heading_wrap_around(self):
        """analyze() behandelt Heading-Wrap-Around korrekt."""
        config = SimulationConfig(turn_heading_threshold_deg=5.0)
        observer = StateObserver(config)

        # Drehung über 360° Grenze: 350° → 10°
        headings = [350, 355, 0, 5, 10]
        for h in headings:
            observer.observe(UfoState(d=float(h), v=10.0, z=50.0, ftime=1.0))

        analysis = observer.analyze()
        # Durchschnittliche Änderung sollte ~5° sein, nicht ~350°
        assert analysis.avg_heading_change < 20.0  # Realistischer Wert

    def test_analyze_detects_stagnation(self):
        """analyze() erkennt Stagnation (kaum Bewegung trotz v > 0)."""
        config = SimulationConfig(dt=0.1)
        observer = StateObserver(config)

        # UFO "will" sich bewegen (v > 0), tut es aber nicht (Position konstant)
        for i in range(10):
            state = UfoState(
                x=0.0, y=0.0, z=50.0,  # Position konstant
                v=10.0, vel=2.78,  # Sollgeschwindigkeit > 0
                ftime=float(i) * 0.1
            )
            observer.observe(state)

        analysis = observer.analyze()
        assert analysis.is_stagnating

    def test_analyze_no_stagnation_when_moving(self):
        """analyze() erkennt keine Stagnation bei normaler Bewegung."""
        config = SimulationConfig(dt=0.1)
        observer = StateObserver(config)

        # UFO bewegt sich normal
        for i in range(10):
            state = UfoState(
                x=float(i) * 2.78 * 0.1,  # Realistische Bewegung
                y=0.0,
                z=50.0,
                v=10.0,
                vel=2.78,
                ftime=float(i) * 0.1
            )
            observer.observe(state)

        analysis = observer.analyze()
        assert not analysis.is_stagnating

    def test_analyze_no_stagnation_when_v_zero(self):
        """analyze() erkennt keine Stagnation wenn v = 0 (erwartet)."""
        observer = StateObserver(DEFAULT_CONFIG)

        # UFO steht absichtlich still
        for i in range(10):
            state = UfoState(x=0.0, y=0.0, z=0.0, v=0.0, vel=0.0)
            observer.observe(state)

        analysis = observer.analyze()
        assert not analysis.is_stagnating

    def test_analyze_requires_minimum_history(self):
        """analyze() benötigt mindestens 3 Zustände für Trend-Erkennung."""
        observer = StateObserver(DEFAULT_CONFIG)

        # Nur 2 Zustände
        observer.observe(UfoState(vz=1.0, v=10.0, z=10.0))
        observer.observe(UfoState(vz=1.0, v=10.0, z=11.0))

        analysis = observer.analyze()
        # Flags sollten False sein (zu wenig Historie)
        assert not analysis.is_ascending
        assert not analysis.is_descending
        assert analysis.avg_vz == 0.0

    def test_analyze_uses_last_10_states(self):
        """analyze() nutzt maximal die letzten 10 Zustände."""
        observer = StateObserver(SimulationConfig(observer_history_size=50))

        # Füge 30 Zustände hinzu: erste 20 mit vz=0, letzte 10 mit vz=2.0
        for i in range(20):
            observer.observe(UfoState(vz=0.0, v=10.0, z=50.0))
        for i in range(10):
            observer.observe(UfoState(vz=2.0, v=10.0, z=60.0))

        analysis = observer.analyze()
        # Durchschnitt sollte ~2.0 sein (nur letzte 10), nicht ~0.67 (alle 30)
        assert analysis.avg_vz == pytest.approx(2.0, abs=0.01)

    def test_get_maneuver_description_idle(self):
        """get_maneuver_description() für idle Phase."""
        observer = StateObserver(DEFAULT_CONFIG)
        observer.observe(UfoState(z=0.0, v=0.0))

        description = observer.get_maneuver_description()
        assert "Phase: idle" in description

    def test_get_maneuver_description_ascending(self):
        """get_maneuver_description() für Steigflug."""
        config = SimulationConfig(climb_vz_threshold_ms=0.5)
        observer = StateObserver(config)

        for i in range(10):
            observer.observe(UfoState(z=float(i), vz=1.0, v=10.0, ftime=1.0))

        description = observer.get_maneuver_description()
        assert "climbing" in description
        assert "vz=" in description

    def test_get_maneuver_description_turning(self):
        """get_maneuver_description() für Drehung."""
        config = SimulationConfig(turn_heading_threshold_deg=5.0)
        observer = StateObserver(config)

        for i in range(10):
            observer.observe(UfoState(d=float(i * 10), v=10.0, z=50.0, ftime=1.0))

        description = observer.get_maneuver_description()
        assert "turning" in description
        assert "Δd=" in description

    def test_get_maneuver_description_stagnating(self):
        """get_maneuver_description() für Stagnation."""
        observer = StateObserver(SimulationConfig(dt=0.1))

        for i in range(10):
            observer.observe(UfoState(x=0.0, v=10.0, vel=2.78, z=50.0))

        description = observer.get_maneuver_description()
        assert "stagnating" in description


# =============================================================================
# Integration-Tests
# =============================================================================

class TestObserverIntegration:
    """Integrations-Tests für realistische Szenarien."""

    def test_complete_flight_scenario(self):
        """Vollständiger Flug: idle → takeoff → flying → landing → landed."""
        observer = StateObserver(DEFAULT_CONFIG)

        # 1. idle
        observer.observe(UfoState(z=0.0, v=0.0, dist=0.0, ftime=0.0))
        assert observer.analyze().phase == "idle"

        # 2. takeoff
        observer.observe(UfoState(z=5.0, v=10.0, vel=2.78, dist=0.0, ftime=0.0))
        assert observer.analyze().phase == "takeoff"

        # 3. flying
        for i in range(5):
            observer.observe(UfoState(z=50.0, v=15.0, vel=4.17, dist=50.0, ftime=float(i)))
        assert observer.analyze().phase == "flying"

        # 4. landing
        config = DEFAULT_CONFIG
        for i in range(3):
            observer.observe(UfoState(
                z=config.landing_detection_height_m - 0.5,  # 1.5m (innerhalb landing zone)
                v=10.0,
                vel=2.78,
                vz=-2.0,
                dist=100.0,
                ftime=10.0 + i
            ))
        assert observer.analyze().phase == "landing"

        # 5. landed
        observer.observe(UfoState(z=0.0, v=0.0, vel=0.0, dist=120.0, ftime=15.0))
        assert observer.analyze().phase == "landed"

    def test_crash_scenario(self):
        """Crash-Szenario: z < 0."""
        observer = StateObserver(DEFAULT_CONFIG)

        # Normaler Flug
        observer.observe(UfoState(z=50.0, v=15.0, ftime=5.0))
        assert observer.analyze().phase == "flying"

        # Crash
        observer.observe(UfoState(z=-1.0, v=15.0, ftime=6.0))
        assert observer.analyze().phase == "crashed"

    def test_multiple_maneuvers_simultaneously(self):
        """Mehrere Manöver gleichzeitig (z.B. Steigflug + Drehung)."""
        config = SimulationConfig(
            climb_vz_threshold_ms=0.5,
            turn_heading_threshold_deg=5.0
        )
        observer = StateObserver(config)

        # Steigender Kurvenflug
        for i in range(10):
            observer.observe(UfoState(
                z=50.0 + float(i),
                vz=1.5,
                d=float(i * 15),
                v=15.0,
                ftime=float(i)
            ))

        analysis = observer.analyze()
        assert analysis.is_ascending
        assert analysis.is_turning
        assert not analysis.is_descending
        assert not analysis.is_stagnating
