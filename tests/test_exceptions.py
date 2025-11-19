#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-Test für core.simulation.exceptions Modul.

Testet grundlegende Import- und Instanziierungsfähigkeit der Exception-Klassen.
"""

import sys
from pathlib import Path

# Sicherstellen, dass src/ im Python-Pfad ist
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_exceptions_import():
    """Test: Exception-Klassen können importiert werden."""
    from core.simulation.exceptions import SimulationError, ConfigError
    assert SimulationError is not None
    assert ConfigError is not None


def test_simulation_error_is_exception():
    """Test: SimulationError ist eine Exception-Klasse."""
    from core.simulation.exceptions import SimulationError
    
    assert issubclass(SimulationError, Exception)


def test_config_error_is_simulation_error():
    """Test: ConfigError ist eine SimulationError-Unterklasse."""
    from core.simulation.exceptions import SimulationError, ConfigError
    
    assert issubclass(ConfigError, SimulationError)
    assert issubclass(ConfigError, Exception)


def test_simulation_error_can_be_raised():
    """Test: SimulationError kann ausgelöst und gefangen werden."""
    from core.simulation.exceptions import SimulationError
    
    try:
        raise SimulationError("Test-Fehler")
    except SimulationError as e:
        assert str(e) == "Test-Fehler"
        assert isinstance(e, Exception)
    except Exception:
        # Sollte nicht hierher kommen
        assert False, "SimulationError sollte als SimulationError gefangen werden"


def test_config_error_can_be_raised():
    """Test: ConfigError kann ausgelöst und gefangen werden."""
    from core.simulation.exceptions import ConfigError
    
    try:
        raise ConfigError("Ungültige Konfiguration")
    except ConfigError as e:
        assert str(e) == "Ungültige Konfiguration"
        assert isinstance(e, Exception)
    except Exception:
        # Sollte nicht hierher kommen
        assert False, "ConfigError sollte als ConfigError gefangen werden"


def test_config_error_caught_as_simulation_error():
    """Test: ConfigError kann als SimulationError gefangen werden."""
    from core.simulation.exceptions import SimulationError, ConfigError
    
    try:
        raise ConfigError("Test")
    except SimulationError as e:
        # ConfigError sollte als SimulationError gefangen werden können
        assert isinstance(e, ConfigError)
        assert isinstance(e, SimulationError)
        assert str(e) == "Test"
    except Exception:
        # Sollte nicht hierher kommen
        assert False, "ConfigError sollte als SimulationError gefangen werden können"


def test_exception_with_no_message():
    """Test: Exceptions können ohne Nachricht ausgelöst werden."""
    from core.simulation.exceptions import SimulationError, ConfigError
    
    try:
        raise SimulationError()
    except SimulationError:
        pass  # Erfolg
    
    try:
        raise ConfigError()
    except ConfigError:
        pass  # Erfolg


if __name__ == "__main__":
    # Manueller Test-Lauf (ohne pytest)
    print("Running smoke tests for core.simulation.exceptions...")
    
    tests = [
        test_exceptions_import,
        test_simulation_error_is_exception,
        test_config_error_is_simulation_error,
        test_simulation_error_can_be_raised,
        test_config_error_can_be_raised,
        test_config_error_caught_as_simulation_error,
        test_exception_with_no_message,
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
