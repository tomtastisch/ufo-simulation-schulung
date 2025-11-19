#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests für immutable PhysicsEngine (T3-1).

Testet dass PhysicsEngine keine in-place Mutationen mehr vornimmt
und korrekt mit frozen=True dataclasses arbeitet.
"""

import pytest
from dataclasses import FrozenInstanceError
from core.simulation.state import UfoState
from core.simulation.config import SimulationConfig, DEFAULT_CONFIG
from core.simulation.ufosim import PhysicsEngine


def test_ufostate_is_frozen():
    """Test: UfoState ist frozen und verhindert direkte Mutationen."""
    state = UfoState(x=10.0, y=20.0, z=5.0)
    
    # Versuch direkt zu mutieren sollte FrozenInstanceError auslösen
    with pytest.raises(FrozenInstanceError):
        state.x = 15.0  # type: ignore
    
    with pytest.raises(FrozenInstanceError):
        state.vx = 2.5  # type: ignore
    
    with pytest.raises(FrozenInstanceError):
        state.ftime = 10.0  # type: ignore


def test_physics_engine_returns_new_state():
    """Test: PhysicsEngine.integrate_step gibt ein neues State-Objekt zurück."""
    engine = PhysicsEngine(DEFAULT_CONFIG)
    old_state = UfoState(x=0.0, y=0.0, z=10.0, v=5.0, i=90.0, d=90.0)
    
    new_state, should_continue, landed = engine.integrate_step(old_state)
    
    # Neue Instanz sollte zurückgegeben werden
    assert id(new_state) != id(old_state), "integrate_step should return a new State instance"
    
    # Alte Instanz sollte unverändert sein
    assert old_state.x == 0.0
    assert old_state.y == 0.0
    assert old_state.z == 10.0
    
    # Flags sollten korrekt sein
    assert should_continue is True
    assert landed is False


def test_physics_engine_updates_position():
    """Test: PhysicsEngine aktualisiert Position korrekt (immutable)."""
    config = SimulationConfig(dt=0.1, vmax_kmh=20.0)
    engine = PhysicsEngine(config)
    
    # Setze Anfangszustand mit Geschwindigkeit nach Norden (d=0°, i=0° = horizontal)
    state = UfoState(
        x=0.0,
        y=0.0,
        z=10.0,
        v=10.0,  # 10 km/h
        vel=10.0 * (1000.0 / 3600.0),  # ~2.78 m/s
        d=0.0,  # Norden
        i=0.0   # horizontal
    )
    
    # Ein Schritt ausführen
    new_state, _, _ = engine.integrate_step(state)
    
    # Position sollte sich geändert haben
    assert new_state.y != state.y, "Position should have changed"
    
    # Alter State ist unverändert
    assert state.y == 0.0
    assert state.ftime == 0.0
    
    # Neuer State hat aktualisierte Werte
    assert new_state.ftime > 0.0, "Flight time should increase"


def test_physics_engine_landing():
    """Test: PhysicsEngine behandelt Landung korrekt (immutable)."""
    config = SimulationConfig(dt=0.1)
    engine = PhysicsEngine(config)
    
    # Zustand bei Landung (am Boden, sehr langsam)
    state = UfoState(
        x=10.0,
        y=20.0,
        z=0.01,  # Praktisch am Boden
        v=1.0,   # Sehr langsam
        vel=1.0 * (1000.0 / 3600.0),  # ~0.28 m/s
        d=0.0,
        i=-15.0,  # Sinkend
        vz=-0.2   # Langsam sinkend
    )
    
    # Mehrere Schritte ausführen um Landung zu erreichen
    current_state = state
    landed = False
    for _ in range(5):
        current_state, should_continue, landed = engine.integrate_step(current_state)
        if landed or current_state.z <= 0.0:
            break
    
    # Landung sollte erkannt worden sein
    assert current_state.z <= 0.0, "Should have landed (z <= 0)"
    
    # Alter State unverändert
    assert state.z == 0.01
    
    # Neuer State hat Landungszustand
    assert current_state.vel == 0.0, "Velocity should be zero after landing"
    assert current_state.v == 0.0, "Target velocity should be zero after landing"


def test_physics_engine_multiple_steps_immutability():
    """Test: Mehrere Physics-Steps erzeugen jeweils neue States."""
    engine = PhysicsEngine(DEFAULT_CONFIG)
    
    states = []
    current = UfoState(x=0.0, y=0.0, z=10.0, v=5.0, i=90.0, d=0.0)
    states.append(current)
    
    # 5 Schritte ausführen
    for _ in range(5):
        current, _, _ = engine.integrate_step(current)
        states.append(current)
    
    # Alle States sollten unterschiedliche Objekte sein
    state_ids = [id(s) for s in states]
    assert len(set(state_ids)) == len(states), "Each step should create a new State instance"
    
    # Erster State sollte unverändert sein
    assert states[0].x == 0.0
    assert states[0].z == 10.0


def test_physics_engine_velocity_update_immutable():
    """Test: Geschwindigkeits-Update ist immutable."""
    engine = PhysicsEngine(DEFAULT_CONFIG)
    
    state = UfoState(x=0.0, y=0.0, z=10.0, v=5.0, delta_v=3.0)
    old_v = state.v
    old_delta_v = state.delta_v
    
    new_state, _, _ = engine.integrate_step(state)
    
    # Alter State unverändert
    assert state.v == old_v
    assert state.delta_v == old_delta_v
    
    # Neuer State hat aktualisierte Werte
    # (delta_v wird bei der Beschleunigung verarbeitet)
    assert new_state is not state


def test_physics_engine_direction_update_immutable():
    """Test: Richtungs-Update ist immutable."""
    engine = PhysicsEngine(DEFAULT_CONFIG)
    
    state = UfoState(x=0.0, y=0.0, z=10.0, d=90.0, delta_d=45.0)
    old_d = state.d
    old_delta_d = state.delta_d
    
    new_state, _, _ = engine.integrate_step(state)
    
    # Alter State unverändert
    assert state.d == old_d
    assert state.delta_d == old_delta_d
    
    # Neuer State ist anderes Objekt
    assert id(new_state) != id(state)


def test_physics_engine_inclination_update_immutable():
    """Test: Neigungs-Update ist immutable."""
    engine = PhysicsEngine(DEFAULT_CONFIG)
    
    state = UfoState(x=0.0, y=0.0, z=10.0, i=90.0, delta_i=-10.0)
    old_i = state.i
    old_delta_i = state.delta_i
    
    new_state, _, _ = engine.integrate_step(state)
    
    # Alter State unverändert
    assert state.i == old_i
    assert state.delta_i == old_delta_i
    
    # Neuer State ist anderes Objekt
    assert id(new_state) != id(state)
