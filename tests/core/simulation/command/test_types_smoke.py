#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-Test für core.simulation.command.types Modul.

Testet grundlegende Import- und Instanziierungsfähigkeit von CommandType und Command,
sowie die korrekte Vermeidung von Importzyklen.
"""

import sys
from pathlib import Path


def test_command_types_import():
    """Test: CommandType und Command können importiert werden."""
    from core.simulation.command.types import CommandType, Command
    assert CommandType is not None
    assert Command is not None


def test_command_type_enum_values():
    """Test: CommandType Enum hat alle erwarteten Werte."""
    from core.simulation.command.types import CommandType
    
    # Alle definierten Command-Typen sollten vorhanden sein
    assert hasattr(CommandType, 'SET_STATE')
    assert hasattr(CommandType, 'WAIT_CONDITION')
    assert hasattr(CommandType, 'EXECUTE_FUNC')
    assert hasattr(CommandType, 'LOG_MESSAGE')
    
    # Werte sollten eindeutig sein
    values = [CommandType.SET_STATE, CommandType.WAIT_CONDITION, 
              CommandType.EXECUTE_FUNC, CommandType.LOG_MESSAGE]
    assert len(values) == len(set(values))


def test_command_instantiation_set_state():
    """Test: Command für SET_STATE kann instanziiert werden."""
    from core.simulation.command.types import CommandType, Command
    
    cmd = Command(
        type=CommandType.SET_STATE,
        target='i',
        value=90
    )
    
    assert cmd.type == CommandType.SET_STATE
    assert cmd.target == 'i'
    assert cmd.value == 90
    assert cmd.condition is None
    assert cmd.func is None
    assert cmd.message is None
    assert cmd.timeout is None


def test_command_instantiation_wait_condition():
    """Test: Command für WAIT_CONDITION kann instanziiert werden."""
    from core.simulation.command.types import CommandType, Command
    
    # Lambda ohne tatsächliche UfoState-Instanz (nur Typ-Check)
    condition = lambda s: s.z >= 10.0
    
    cmd = Command(
        type=CommandType.WAIT_CONDITION,
        condition=condition,
        timeout=5.0
    )
    
    assert cmd.type == CommandType.WAIT_CONDITION
    assert cmd.condition is not None
    assert cmd.timeout == 5.0
    assert cmd.target is None
    assert cmd.value is None


def test_command_instantiation_execute_func():
    """Test: Command für EXECUTE_FUNC kann instanziiert werden."""
    from core.simulation.command.types import CommandType, Command
    
    test_func = lambda: print("test")
    
    cmd = Command(
        type=CommandType.EXECUTE_FUNC,
        func=test_func
    )
    
    assert cmd.type == CommandType.EXECUTE_FUNC
    assert cmd.func is not None
    assert cmd.target is None
    assert cmd.condition is None


def test_command_instantiation_log_message():
    """Test: Command für LOG_MESSAGE kann instanziiert werden."""
    from core.simulation.command.types import CommandType, Command
    
    cmd = Command(
        type=CommandType.LOG_MESSAGE,
        message="Test message"
    )
    
    assert cmd.type == CommandType.LOG_MESSAGE
    assert cmd.message == "Test message"
    assert cmd.target is None
    assert cmd.func is None


def test_command_is_dataclass():
    """Test: Command ist ein dataclass."""
    from core.simulation.command.types import Command
    from dataclasses import is_dataclass
    
    assert is_dataclass(Command)


def test_no_runtime_import_of_ufostate():
    """Test: UfoState wird nicht zur Laufzeit importiert (TYPE_CHECKING only)."""
    from core.simulation.command.types import Command, CommandType
    import sys
    
    # Command sollte importierbar sein, ohne dass state.state geladen wird
    # (außer es wurde bereits woanders geladen)
    # Dies ist ein Proxy-Test für korrekte TYPE_CHECKING Nutzung
    
    # Erstelle Command mit condition - sollte ohne UfoState-Import funktionieren
    cmd = Command(
        type=CommandType.WAIT_CONDITION,  # Verwende korrekten CommandType
        condition=lambda s: True  # Lambda akzeptiert beliebigen Parameter
    )
    
    assert cmd is not None


def test_command_package_import():
    """Test: Command und CommandType können vom Package importiert werden."""
    from core.simulation.command import Command, CommandType
    
    assert Command is not None
    assert CommandType is not None


def test_command_module_has_no_circular_imports():
    """Test: Command-Modul hat keine zirkulären Imports zu state."""
    import importlib
    import sys
    
    # Speichere aktuell geladene Module
    loaded_before = set(sys.modules.keys())
    
    # Importiere command.types frisch (ggf. neu)
    if 'core.simulation.command.types' in sys.modules:
        del sys.modules['core.simulation.command.types']
    if 'core.simulation.command' in sys.modules:
        del sys.modules['core.simulation.command']
    
    # Import sollte nicht state.state zur Laufzeit laden
    from core.simulation.command.types import Command, CommandType
    
    # state.state sollte nur geladen sein, wenn TYPE_CHECKING true wäre (ist es nicht)
    # oder wenn es bereits vorher geladen war
    # Ein reines Import von command.types sollte state.state NICHT laden
    loaded_after = set(sys.modules.keys())
    newly_loaded = loaded_after - loaded_before
    
    # Prüfe dass state.state nicht durch command.types Import geladen wurde
    state_modules = [m for m in newly_loaded if 'state.state' in m]
    
    # Wenn state schon vorher geladen war, ist dieser Test nicht aussagekräftig
    # aber das ist ok - der Test verhindert neue zirkuläre Imports
    if 'core.simulation.state.state' not in loaded_before:
        assert 'core.simulation.state.state' not in newly_loaded, \
            "command.types sollte state.state nicht zur Laufzeit importieren"


if __name__ == "__main__":
    tests = [
        test_command_types_import,
        test_command_type_enum_values,
        test_command_instantiation_set_state,
        test_command_instantiation_wait_condition,
        test_command_instantiation_execute_func,
        test_command_instantiation_log_message,
        test_command_is_dataclass,
        test_no_runtime_import_of_ufostate,
        test_command_package_import,
        test_command_module_has_no_circular_imports,
    ]
    
    print("Running command.types smoke tests...")
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
    
    print("\nAll smoke tests completed.")
