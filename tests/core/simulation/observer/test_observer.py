#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-Tests für das observer-Modul.

Testet Phase-Erkennung, Manöver-Analyse und State-Observer mit
synthetischen Zustandsverläufen.
"""

from core.simulation.infrastructure import DEFAULT_CONFIG, SimulationConfig
from core.simulation.observer import (
    ManeuverAnalysis,
    compute_phase,
    StateObserver,
)
from core.simulation.state import UfoState


# =============================================================================
# Tests für compute_phase()
# =============================================================================

class TestComputePhase:
    """Tests für die regelbasierte Phasenbestimmung."""

    def test_idle_initial_state(self):
        """Initialer Zustand (am Boden, nie geflogen) ist idle."""
        state = UfoState(x=0.0, y=0.0, z=0.0, v=0.0, dist=0.0, ftime=0.0)
        assert compute_phase(state) == "idle"

    def test_idle_after_reset(self):
        """Nach Reset (z=0, v=0, keine Flugzeit) ist idle."""
        state = UfoState(x=100.0, y=100.0, z=0.0, v=0.0, dist=0.0, ftime=0.0)
        assert compute_phase(state) == "idle"

    def test_takeoff_just_lifted(self):
        """Gerade abgehoben (ftime=0, z>0, v>0) ist takeoff."""
        state = UfoState(z=0.5, v=5.0, ftime=0.0, dist=0.0)
        assert compute_phase(state) == "takeoff"

    def test_takeoff_very_low_altitude(self):
        """Sehr niedrige Höhe mit Geschwindigkeit ist noch takeoff."""
        state = UfoState(z=0.1, v=3.0, ftime=0.0, dist=0.0)
        assert compute_phase(state) == "takeoff"

    def test_flying_normal_altitude(self):
        """Normale Flughöhe mit Geschwindigkeit ist flying."""
        state = UfoState(z=10.0, v=10.0, vz=0.0, ftime=1.0, dist=5.0)
        assert compute_phase(state) == "flying"

    def test_flying_high_altitude(self):
        """Große Höhe mit Geschwindigkeit ist flying."""
        state = UfoState(z=100.0, v=15.0, vz=2.0, ftime=10.0, dist=50.0)
        assert compute_phase(state) == "flying"

    def test_landing_low_altitude_descending(self):
        """Niedriger Flug mit Sinkflug ist landing."""
        state = UfoState(z=1.5, v=5.0, vz=-0.5, ftime=5.0, dist=20.0)
        assert compute_phase(state) == "landing"

    def test_landing_at_detection_height(self):
        """An der Erkennungshöhe mit Sinkflug ist landing."""
        config = DEFAULT_CONFIG
        state = UfoState(
            z=config.landing_detection_height_m,
            v=3.0,
            vz=-0.3,
            ftime=10.0,
            dist=30.0,
        )
        assert compute_phase(state, config) == "landing"

    def test_landed_after_flight(self):
        """Am Boden nach erfolgreichem Flug ist landed."""
        state = UfoState(z=0.0, v=0.0, ftime=10.0, dist=50.0)
        assert compute_phase(state) == "landed"

    def test_landed_with_flight_distance(self):
        """Am Boden mit zurückgelegter Strecke ist landed."""
        state = UfoState(z=0.0, v=0.0, ftime=0.0, dist=100.0)
        assert compute_phase(state) == "landed"

    def test_crashed_negative_z(self):
        """Negative Höhe ist crashed."""
        state = UfoState(z=-1.0, v=5.0, ftime=5.0, dist=20.0)
        assert compute_phase(state) == "crashed"

    def test_crashed_negative_z_marker(self):
        """Sehr negative Höhe (Crash-Marker) ist crashed."""
        state = UfoState(z=-10.0, v=0.0, ftime=10.0, dist=30.0)
        assert compute_phase(state) == "crashed"


class TestComputePhasePriorities:
    """Tests für die Prioritätsreihenfolge der Phasen-Regeln."""

    def test_crashed_has_highest_priority(self):
        """Crashed hat höchste Priorität (überstimmt alle anderen)."""
        # Auch mit v>0 und z<0 ist es crashed, nicht flying
        state = UfoState(z=-0.1, v=10.0, vz=-2.0, ftime=5.0, dist=20.0)
        assert compute_phase(state) == "crashed"

    def test_landed_before_idle(self):
        """Landed hat Priorität vor idle (has_flown unterscheidet)."""
        # Am Boden mit Flugzeit -> landed
        state1 = UfoState(z=0.0, v=0.0, ftime=10.0, dist=50.0)
        assert compute_phase(state1) == "landed"

        # Am Boden ohne Flugzeit -> idle
        state2 = UfoState(z=0.0, v=0.0, ftime=0.0, dist=0.0)
        assert compute_phase(state2) == "idle"

    def test_takeoff_before_landing(self):
        """Takeoff hat Priorität vor landing (ftime=0 unterscheidet)."""
        # Niedriger Flug mit ftime=0 -> takeoff
        state1 = UfoState(z=1.0, v=5.0, vz=-0.5, ftime=0.0, dist=0.0)
        assert compute_phase(state1) == "takeoff"

        # Niedriger Flug mit ftime>0 und vz<0 -> landing
        state2 = UfoState(z=1.0, v=5.0, vz=-0.5, ftime=2.0, dist=10.0)
        assert compute_phase(state2) == "landing"

    def test_landing_before_flying(self):
        """Landing hat Priorität vor flying (niedrige Höhe + vz<0)."""
        # Niedrig mit Sinkflug -> landing
        state1 = UfoState(z=1.5, v=5.0, vz=-0.5, ftime=5.0, dist=20.0)
        assert compute_phase(state1) == "landing"

        # Niedrig ohne Sinkflug -> flying
        state2 = UfoState(z=1.5, v=5.0, vz=0.0, ftime=5.0, dist=20.0)
        assert compute_phase(state2) == "flying"


class TestComputePhaseEdgeCases:
    """Tests für Grenzfälle und spezielle Konfigurationen."""

    def test_zero_velocity_in_air(self):
        """Geschwindigkeit 0 in der Luft ist idle (kein Flug)."""
        state = UfoState(z=10.0, v=0.0, vz=0.0, ftime=5.0, dist=20.0)
        # v=0 erfüllt keine Flugphase -> idle
        assert compute_phase(state) == "idle"

    def test_custom_landing_detection_height(self):
        """Benutzerdefinierte Landungshöhe wird korrekt verwendet."""
        # landing_detection_height_m ist eine Property, kein Parameter
        # Wir können es nicht direkt setzen, aber testen mit DEFAULT_CONFIG
        config = DEFAULT_CONFIG

        # Knapp unter Schwelle mit vz<0 -> landing
        state1 = UfoState(
            z=config.landing_detection_height_m - 0.1,
            v=5.0,
            vz=-0.5,
            ftime=5.0,
            dist=20.0,
        )
        assert compute_phase(state1, config) == "landing"

        # Über Schwelle mit vz<0 -> flying
        state2 = UfoState(
            z=config.landing_detection_height_m + 0.1,
            v=5.0,
            vz=-0.5,
            ftime=5.0,
            dist=20.0,
        )
        assert compute_phase(state2, config) == "flying"

    def test_zero_threshold_handling(self):
        """Exakte Schwellenwerte (z=0) werden korrekt behandelt."""
        config = DEFAULT_CONFIG

        # Exakt z=0 mit Flugzeit -> landed
        state1 = UfoState(z=config.zero_value, v=0.0, ftime=10.0, dist=50.0)
        assert compute_phase(state1, config) == "landed"

        # Minimal über z=0 mit v>0 -> flying oder takeoff
        state2 = UfoState(
            z=config.zero_value + 0.01, v=5.0, ftime=0.0, dist=0.0
        )
        assert compute_phase(state2, config) == "takeoff"

    def test_positive_vz_in_landing_range(self):
        """Steigflug in niedriger Höhe ist flying, nicht landing."""
        state = UfoState(z=1.5, v=5.0, vz=0.5, ftime=5.0, dist=20.0)
        # vz>0 erfüllt nicht landing-Kriterium
        assert compute_phase(state) == "flying"


# =============================================================================
# Tests für ManeuverAnalysis
# =============================================================================

class TestManeuverAnalysis:
    """Tests für die ManeuverAnalysis Dataclass."""

    def test_default_values(self):
        """Standard-Werte sind korrekt gesetzt."""
        analysis = ManeuverAnalysis(phase="idle")
        assert analysis.phase == "idle"
        assert analysis.is_ascending is False
        assert analysis.is_descending is False
        assert analysis.is_turning is False
        assert analysis.is_stagnating is False
        assert analysis.avg_vz == 0.0
        assert analysis.avg_heading_change == 0.0

    def test_custom_values(self):
        """Benutzerdefinierte Werte werden korrekt gespeichert."""
        analysis = ManeuverAnalysis(
            phase="flying",
            is_ascending=True,
            is_turning=True,
            avg_vz=2.5,
            avg_heading_change=10.0,
        )
        assert analysis.phase == "flying"
        assert analysis.is_ascending is True
        assert analysis.is_descending is False
        assert analysis.is_turning is True
        assert analysis.avg_vz == 2.5
        assert analysis.avg_heading_change == 10.0


# =============================================================================
# Tests für StateObserver
# =============================================================================

class TestStateObserverBasics:
    """Basis-Funktionalität des StateObserver."""

    def test_initialization(self):
        """Observer wird korrekt initialisiert."""
        observer = StateObserver()
        assert observer.config == DEFAULT_CONFIG
        assert len(observer.history) == 0

    def test_custom_config(self):
        """Observer kann mit benutzerdefinierter Config erstellt werden."""
        config = SimulationConfig(observer_history_size=20)
        observer = StateObserver(config)
        assert observer.config == config
        assert observer.history.maxlen == 20

    def test_observe_adds_to_history(self):
        """observe() fügt Zustände zur Historie hinzu."""
        observer = StateObserver()
        state = UfoState(x=10.0, z=5.0)

        observer.observe(state)
        assert len(observer.history) == 1
        assert observer.history[0].x == 10.0
        assert observer.history[0].z == 5.0

    def test_observe_creates_copy(self):
        """observe() erstellt defensive Kopie des States."""
        observer = StateObserver()
        state = UfoState(x=10.0, z=5.0)

        observer.observe(state)
        # Original-State ist nicht das gleiche Objekt
        assert observer.history[0] is not state
        # Aber hat die gleichen Werte
        assert observer.history[0].x == state.x
        assert observer.history[0].z == state.z

    def test_history_respects_maxlen(self):
        """Historie respektiert maxlen (Ringpuffer)."""
        config = SimulationConfig(observer_history_size=3)
        observer = StateObserver(config)

        for i in range(5):
            observer.observe(UfoState(x=float(i)))

        # Nur die letzten 3 Einträge bleiben
        assert len(observer.history) == 3
        assert observer.history[0].x == 2.0
        assert observer.history[1].x == 3.0
        assert observer.history[2].x == 4.0


class TestStateObserverAnalyze:
    """Tests für die analyze() Methode."""

    def test_analyze_empty_history_returns_idle(self):
        """Leere Historie gibt idle zurück."""
        observer = StateObserver()
        analysis = observer.analyze()

        assert analysis.phase == "idle"
        assert analysis.is_ascending is False
        assert analysis.is_descending is False

    def test_analyze_single_state(self):
        """Einzelner State wird korrekt analysiert."""
        observer = StateObserver()
        observer.observe(UfoState(z=10.0, v=10.0, ftime=5.0, dist=20.0))

        analysis = observer.analyze()
        assert analysis.phase == "flying"

    def test_analyze_detects_ascending(self):
        """Steigflug wird erkannt (avg_vz > threshold)."""
        config = SimulationConfig(climb_vz_threshold_ms=0.5)
        observer = StateObserver(config)

        # Mehrere Zustände mit steigendem vz
        for i in range(5):
            observer.observe(UfoState(z=float(i), v=10.0, vz=1.0, ftime=float(i)))

        analysis = observer.analyze()
        assert analysis.is_ascending is True
        assert analysis.avg_vz > config.climb_vz_threshold_ms

    def test_analyze_detects_descending(self):
        """Sinkflug wird erkannt (avg_vz < threshold)."""
        config = SimulationConfig(descent_vz_threshold_ms=-0.5)
        observer = StateObserver(config)

        # Mehrere Zustände mit sinkendem vz
        for i in range(5):
            observer.observe(
                UfoState(z=10.0 - float(i), v=10.0, vz=-1.0, ftime=float(i))
            )

        analysis = observer.analyze()
        assert analysis.is_descending is True
        assert analysis.avg_vz < config.descent_vz_threshold_ms

    def test_analyze_detects_turning(self):
        """Kurven werden erkannt (avg_heading_change > threshold)."""
        config = SimulationConfig(turn_heading_threshold_deg=5.0)
        observer = StateObserver(config)

        # Mehrere Zustände mit sich änderndem Heading
        headings = [0.0, 10.0, 20.0, 30.0, 40.0]
        for i, heading in enumerate(headings):
            observer.observe(
                UfoState(d=heading, v=10.0, z=10.0, ftime=float(i))
            )

        analysis = observer.analyze()
        assert analysis.is_turning is True
        assert analysis.avg_heading_change > config.turn_heading_threshold_deg

    def test_analyze_heading_wrap_around_positive(self):
        """Wrap-around bei Heading (350° → 10°) wird korrekt behandelt."""
        observer = StateObserver()

        observer.observe(UfoState(d=350.0, v=10.0, z=10.0))
        observer.observe(UfoState(d=10.0, v=10.0, z=10.0))

        analysis = observer.analyze()
        # Delta sollte 20° sein, nicht 340°
        assert analysis.avg_heading_change < 30.0

    def test_analyze_heading_wrap_around_negative(self):
        """Wrap-around bei Heading (10° → 350°) wird korrekt behandelt."""
        observer = StateObserver()

        observer.observe(UfoState(d=10.0, v=10.0, z=10.0))
        observer.observe(UfoState(d=350.0, v=10.0, z=10.0))

        analysis = observer.analyze()
        # Delta sollte 20° sein, nicht 340°
        assert analysis.avg_heading_change < 30.0

    def test_analyze_detects_stagnation(self):
        """Stagnation wird erkannt (geringe Bewegung trotz v>0)."""
        config = SimulationConfig(dt=0.1)
        observer = StateObserver(config)

        # UFO sollte sich mit 10m/s bewegen, tut es aber nicht
        for i in range(10):
            # Sehr kleine Positionsänderung trotz vel=10m/s
            observer.observe(
                UfoState(
                    x=float(i) * 0.01,  # Nur 0.01m pro Step statt 1m
                    y=0.0,
                    z=10.0,
                    v=10.0,
                    vel=10.0,
                    ftime=float(i) * 0.1,
                )
            )

        analysis = observer.analyze()
        assert analysis.is_stagnating

    def test_analyze_no_stagnation_when_moving_correctly(self):
        """Keine Stagnation bei korrekter Bewegung."""
        config = SimulationConfig(dt=0.1)
        observer = StateObserver(config)

        # UFO bewegt sich korrekt mit 10m/s
        for i in range(10):
            observer.observe(
                UfoState(
                    x=float(i) * 1.0,  # 1m pro Step bei 10m/s und dt=0.1s
                    y=0.0,
                    z=10.0,
                    v=10.0,
                    vel=10.0,
                    ftime=float(i) * 0.1,
                )
            )

        analysis = observer.analyze()
        assert not analysis.is_stagnating


class TestStateObserverManeuverDescription:
    """Tests für get_maneuver_description()."""

    def test_description_includes_phase(self):
        """Beschreibung enthält immer die Phase."""
        observer = StateObserver()
        observer.observe(UfoState(z=10.0, v=10.0, ftime=5.0))

        desc = observer.get_maneuver_description()
        assert "Phase: flying" in desc

    def test_description_includes_climbing(self):
        """Beschreibung enthält 'climbing' bei Steigflug."""
        config = SimulationConfig(climb_vz_threshold_ms=0.5)
        observer = StateObserver(config)

        for i in range(5):
            observer.observe(UfoState(z=float(i), v=10.0, vz=1.0, ftime=float(i)))

        desc = observer.get_maneuver_description()
        assert "climbing" in desc

    def test_description_includes_descending(self):
        """Beschreibung enthält 'descending' bei Sinkflug."""
        config = SimulationConfig(descent_vz_threshold_ms=-0.5)
        observer = StateObserver(config)

        for i in range(5):
            observer.observe(
                UfoState(z=10.0 - float(i), v=10.0, vz=-1.0, ftime=float(i))
            )

        desc = observer.get_maneuver_description()
        assert "descending" in desc

    def test_description_includes_turning(self):
        """Beschreibung enthält 'turning' und Delta bei Kurven."""
        config = SimulationConfig(turn_heading_threshold_deg=5.0)
        observer = StateObserver(config)

        headings = [0.0, 10.0, 20.0, 30.0]
        for i, heading in enumerate(headings):
            observer.observe(UfoState(d=heading, v=10.0, z=10.0, ftime=float(i)))

        desc = observer.get_maneuver_description()
        assert "turning" in desc
        assert "Δd=" in desc

    def test_description_includes_stagnating(self):
        """Beschreibung enthält 'stagnating' bei Stagnation."""
        config = SimulationConfig(dt=0.1)
        observer = StateObserver(config)

        for i in range(10):
            observer.observe(
                UfoState(
                    x=float(i) * 0.01, y=0.0, z=10.0, v=10.0, vel=10.0, ftime=float(i) * 0.1
                )
            )

        desc = observer.get_maneuver_description()
        assert "stagnating" in desc

    def test_description_includes_vz_when_nonzero(self):
        """Beschreibung enthält vz wenn != 0."""
        observer = StateObserver()

        for i in range(5):
            observer.observe(UfoState(z=float(i), v=10.0, vz=2.5, ftime=float(i)))

        desc = observer.get_maneuver_description()
        assert "vz=" in desc


class TestStateObserverIntegration:
    """Integrationstests mit realistischen Szenarien."""

    def test_complete_takeoff_sequence(self):
        """Komplette Startsequenz wird korrekt erkannt."""
        observer = StateObserver()

        # Start am Boden
        observer.observe(UfoState(z=0.0, v=0.0, ftime=0.0))
        assert observer.analyze().phase == "idle"

        # Abheben - mehrere States für Trend-Erkennung
        observer.observe(UfoState(z=0.3, v=5.0, vz=1.0, ftime=0.0))
        observer.observe(UfoState(z=0.6, v=5.0, vz=1.2, ftime=0.0))
        observer.observe(UfoState(z=0.9, v=5.0, vz=1.5, ftime=0.0))
        analysis = observer.analyze()
        assert analysis.phase == "takeoff"
        # Jetzt haben wir genug States für Trend-Erkennung (>= 3)
        assert analysis.is_ascending

        # Steigflug
        for i in range(10):
            observer.observe(
                UfoState(z=1.0 + float(i), v=10.0, vz=1.0, ftime=float(i) * 0.1)
            )
        analysis = observer.analyze()
        assert analysis.phase == "flying"
        assert analysis.is_ascending

    def test_complete_landing_sequence(self):
        """Komplette Landungssequenz wird korrekt erkannt."""
        observer = StateObserver()

        # Reiseflug
        observer.observe(UfoState(z=20.0, v=10.0, vz=0.0, ftime=10.0, dist=100.0))
        assert observer.analyze().phase == "flying"

        # Landeanflug (Sinkflug)
        for i in range(5):
            observer.observe(
                UfoState(
                    z=5.0 - float(i) * 0.8,
                    v=5.0,
                    vz=-0.8,
                    ftime=10.0 + float(i) * 0.1,
                    dist=100.0 + float(i) * 0.5,
                )
            )
        analysis = observer.analyze()
        assert analysis.phase == "landing"
        assert analysis.is_descending is True

        # Gelandet
        observer.observe(UfoState(z=0.0, v=0.0, ftime=15.0, dist=105.0))
        assert observer.analyze().phase == "landed"

    def test_circular_flight_pattern(self):
        """Kreisflug wird als turning erkannt."""
        config = SimulationConfig(turn_heading_threshold_deg=5.0)
        observer = StateObserver(config)

        # Kreisflug mit konstantem Radius
        import math

        for i in range(20):
            angle = float(i) * 18.0  # 18° pro Schritt = voller Kreis in 20 Schritten
            x = 10.0 * math.cos(math.radians(angle))
            y = 10.0 * math.sin(math.radians(angle))
            observer.observe(
                UfoState(
                    x=x, y=y, z=10.0, d=angle, v=10.0, ftime=float(i) * 0.1
                )
            )

        analysis = observer.analyze()
        assert analysis.phase == "flying"
        assert analysis.is_turning is True
        assert analysis.avg_heading_change > config.turn_heading_threshold_deg
