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
    """Test: UfoState kann mit Defaults instanziiert werden."""
    from core.simulation.state import UfoState
    
    state = UfoState()
    assert state is not None
    
    # Prüfe Default-Werte (Position)
    assert state.x == 0.0
    assert state.y == 0.0
    assert state.z == 0.0
    
    # Prüfe Default-Werte (Geschwindigkeit/Richtung)
    assert state.v == 0.0
    assert state.vel == 0.0
    assert state.d == 90.0  # Ost
    assert state.i == 90.0  # Vertikal hoch
    
    # Prüfe Default-Werte (Geschwindigkeitskomponenten)
    assert state.vx == 0.0
    assert state.vy == 0.0
    assert state.vz == 0.0
    
    # Prüfe Default-Werte (Beschleunigung)
    assert state.accel_x == 0.0
    assert state.accel_y == 0.0
    assert state.accel_z == 0.0
    
    # Prüfe Default-Werte (Statistik)
    assert state.dist == 0.0
    assert state.ftime == 0.0
    
    # Prüfe Default-Werte (Steuerkommandos)
    assert state.delta_v == 0.0
    assert state.delta_d == 0.0
    assert state.delta_i == 0.0


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


def test_state_has_required_attributes():
    """Test: UfoState hat alle erforderlichen Attribute."""
    from core.simulation.state import UfoState
    
    state = UfoState()
    
    # Position
    assert hasattr(state, "x")
    assert hasattr(state, "y")
    assert hasattr(state, "z")
    
    # Geschwindigkeit
    assert hasattr(state, "v")
    assert hasattr(state, "vel")
    assert hasattr(state, "d")
    assert hasattr(state, "i")
    
    # Geschwindigkeitskomponenten
    assert hasattr(state, "vx")
    assert hasattr(state, "vy")
    assert hasattr(state, "vz")
    
    # Beschleunigung
    assert hasattr(state, "accel_x")
    assert hasattr(state, "accel_y")
    assert hasattr(state, "accel_z")
    
    # Statistik
    assert hasattr(state, "dist")
    assert hasattr(state, "ftime")
    
    # Steuerkommandos
    assert hasattr(state, "delta_v")
    assert hasattr(state, "delta_d")
    assert hasattr(state, "delta_i")


def test_state_vector_properties():
    """Test: UfoState hat die erforderlichen Vektor-Properties."""
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
    # Manueller Test-Lauf (ohne pytest)
    print("Running smoke tests for core.simulation.state...")
    
    tests = [
        test_state_import,
        test_state_instantiation_defaults,
        test_state_instantiation_custom,
        test_state_has_required_attributes,
        test_state_vector_properties,
        test_state_is_dataclass,
        test_state_uses_slots,
    ]
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
        except Exception as e:
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
    
    print("\nAll smoke tests completed.")
