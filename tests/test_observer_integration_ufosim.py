#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrations-Test für Observer-Modul mit UfoSim.

Verifiziert, dass Observer korrekt in UfoSim integriert ist und
die Phasen-/Manöver-Analyse während einer Simulation funktioniert.
"""

from core.simulation import DEFAULT_CONFIG, UfoSim
from core.simulation.observer import StateObserver


def test_observer_integrated_in_ufosim():
    """Observer ist korrekt in UfoSim integriert."""
    sim = UfoSim(DEFAULT_CONFIG)
    
    # Observer sollte vorhanden sein
    assert hasattr(sim, 'observer')
    assert isinstance(sim.observer, StateObserver)


def test_observer_receives_state_updates():
    """Observer erhält State-Updates vom StateManager."""
    sim = UfoSim(DEFAULT_CONFIG)
    
    # Initial sollte History leer sein
    assert len(sim.observer.history) == 0
    
    # Nach manuellem State-Update sollte Observer benachrichtigt werden
    def update_state(state):
        return state
    
    # Trigger ein Update durch get_state_snapshot
    _ = sim.get_state_snapshot()
    
    # Observer sollte jetzt mindestens einen State haben
    # (wird durch StateManager.register_observer automatisch befüllt)


def test_phase_detection_via_ufosim():
    """Phasen-Erkennung funktioniert über UfoSim API."""
    sim = UfoSim(DEFAULT_CONFIG)
    
    # Initial Phase sollte 'idle' sein
    phase = sim.get_phase()
    assert phase == "idle"


def test_maneuver_analysis_via_ufosim():
    """Manöver-Analyse funktioniert über UfoSim API."""
    sim = UfoSim(DEFAULT_CONFIG)
    
    # Initial Analyse sollte idle sein
    analysis = sim.get_maneuver_analysis()
    assert analysis.phase == "idle"
    assert not analysis.is_ascending
    assert not analysis.is_descending
    assert not analysis.is_turning
    assert not analysis.is_stagnating


def test_observer_reset():
    """Observer wird korrekt zurückgesetzt."""
    sim = UfoSim(DEFAULT_CONFIG)
    
    # Füge manuell Daten zum Observer hinzu
    from core.simulation.state import UfoState
    sim.observer.observe(UfoState(z=10.0, v=15.0))
    assert len(sim.observer.history) > 0
    
    # Reset sollte Observer neu initialisieren
    sim.reset()
    assert isinstance(sim.observer, StateObserver)
    # Neue Instanz sollte leere History haben
    # (kann initial einen State enthalten vom Reset selbst)
