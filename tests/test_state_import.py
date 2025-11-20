#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-Test für core.simulation.state Modul.

Testet grundlegende Import- und Instanziierungsfähigkeit von UfoState.
"""

import sys
from pathlib import Path

# Sicherstellen, dass src/ im Python-Pfad ist
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_state_import():
    """Test: UfoState kann importiert werden."""
    from core.simulation.state import UfoState
    assert UfoState is not None


def test_state_instantiation_defaults():
    """Test: UfoState kann mit Defaults instanziiert werden - robuste Invarianten."""
    from core.simulation.state import UfoState
    
    state = UfoState()
    assert state is not None
    
    # Position initial bei Null
    assert state.x == 0.0
    assert state.y == 0.0
    assert state.z == 0.0
    
    # Geschwindigkeitskomponenten initial bei Null
    assert state.vx == 0.0
    assert state.vy == 0.0
    assert state.vz == 0.0
    
    # Beschleunigungskomponenten initial bei Null
    assert state.accel_x == 0.0
    assert state.accel_y == 0.0
    assert state.accel_z == 0.0
    
    # Statistik initial bei Null
    assert state.dist == 0.0
    assert state.ftime == 0.0
    
    # Winkel in gültigem Wertebereich (nicht auf spezifische Werte festgelegt)
    assert 0.0 <= state.d < 360.0
    assert 0.0 <= state.i <= 180.0


def test_state_instantiation_custom():
    """Test: UfoState kann mit benutzerdefinierten Werten instanziiert werden."""
    from core.simulation.state import UfoState
    
    state = UfoState(
        x=100.0,
        y=200.0,
        z=50.0,
        v=72.0,
        d=45.0,
        i=60.0
    )
    
    assert state.x == 100.0
    assert state.y == 200.0
    assert state.z == 50.0
    assert state.v == 72.0
    assert state.d == 45.0
    assert state.i == 60.0


def test_state_vector_properties():
    """Test: UfoState-Properties liefern korrekte NumPy-Arrays."""
    from core.simulation.state import UfoState
    import numpy as np
    
    state = UfoState(x=10.0, y=20.0, z=30.0, vx=1.0, vy=2.0, vz=3.0, accel_x=0.1, accel_y=0.2, accel_z=0.3)
    
    # Position Vector
    pos_vec = state.position_vector
    assert isinstance(pos_vec, np.ndarray)
    assert len(pos_vec) == 3
    assert pos_vec[0] == 10.0
    assert pos_vec[1] == 20.0
    assert pos_vec[2] == 30.0
    
    # Velocity Vector
    vel_vec = state.velocity_vector
    assert isinstance(vel_vec, np.ndarray)
    assert len(vel_vec) == 3
    assert vel_vec[0] == 1.0
    assert vel_vec[1] == 2.0
    assert vel_vec[2] == 3.0
    
    # Acceleration Vector
    accel_vec = state.acceleration_vector
    assert isinstance(accel_vec, np.ndarray)
    assert len(accel_vec) == 3
    assert accel_vec[0] == 0.1
    assert accel_vec[1] == 0.2
    assert accel_vec[2] == 0.3


def test_state_is_dataclass():
    """Test: UfoState ist ein dataclass."""
    from core.simulation.state import UfoState
    from dataclasses import is_dataclass
    
    assert is_dataclass(UfoState)


def test_state_uses_slots():
    """Test: UfoState nutzt slots für Performance."""
    from core.simulation.state import UfoState
    
    state = UfoState()
    
    # Wenn slots=True, dann sollte es kein __dict__ geben
    assert not hasattr(state, "__dict__")


if __name__ == "__main__":
    from conftest import run_manual_tests

    tests = [
        test_state_import,
        test_state_instantiation_defaults,
        test_state_instantiation_custom,
        test_state_vector_properties,
        test_state_is_dataclass,
        test_state_uses_slots,
    ]

    run_manual_tests("core.simulation.state", tests)
