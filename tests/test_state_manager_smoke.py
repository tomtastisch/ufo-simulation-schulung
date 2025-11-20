#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke-Test für StateManager-Modul - Standalone-Lauffähigkeit."""



def test_state_manager_module_import():
    """StateManager-Modul kann standalone importiert werden."""
    from core.simulation.state import StateManager
    
    assert StateManager is not None


def test_state_manager_instantiation():
    """StateManager kann ohne weitere Dependencies instantiiert werden."""
    from core.simulation.state import StateManager, UfoState
    
    # Default-Initialisierung
    manager = StateManager()
    assert manager is not None
    
    # Mit initial state
    initial = UfoState(x=10.0, z=20.0)
    manager_with_state = StateManager(initial_state=initial)
    assert manager_with_state is not None
    
    snapshot = manager_with_state.get_snapshot()
    assert snapshot.x == 10.0
    assert snapshot.z == 20.0


def test_state_manager_has_required_methods():
    """StateManager hat alle geforderten Methoden gemäß Spec."""
    from core.simulation.state import StateManager
    
    manager = StateManager()
    
    # Geforderte Methoden aus introductions.md Abschnitt 4.1
    assert hasattr(manager, 'update_state')
    assert hasattr(manager, 'get_snapshot')
    assert hasattr(manager, 'register_observer')
    assert hasattr(manager, 'unregister_observer')
    assert hasattr(manager, 'wait_for_condition')
    assert hasattr(manager, 'reset')
    
    # Alle Methoden sollten aufrufbar sein
    assert callable(manager.update_state)
    assert callable(manager.get_snapshot)
    assert callable(manager.register_observer)
    assert callable(manager.unregister_observer)
    assert callable(manager.wait_for_condition)
    assert callable(manager.reset)


def test_state_manager_has_no_forbidden_dependencies():
    """StateManager hat keine verbotenen Dependencies."""
    import sys
    from core.simulation.state import manager as manager_module
    
    # StateManager-Modul laden
    module_source = manager_module.__file__
    
    # Verbotene Imports gemäß Spec (Sicherstellung)
    # Prüfe auf tatsächliche import-Statements, nicht nur Erwähnungen in Docstrings
    forbidden_imports = [
        'from ..physics',
        'from .physics',
        'import physics',
        'from ..command',
        'from .command',
        'import command',
        'from ..controller',
        'from .controller',
        'import controller',
        'from ..view',
        'from .view',
        'import view',
        'from .pview',
        'import pview',
    ]
    
    # Modul-Quelltext überprüfen
    with open(module_source, 'r') as f:
        content = f.read()
    
    for forbidden in forbidden_imports:
        assert forbidden not in content, f"StateManager sollte nicht '{forbidden}' verwenden"
    
    # Stelle sicher, dass nur erlaubte Imports vorhanden sind
    # Mindestens die Kern-Dependencies sollten vorhanden sein
    assert 'from .state import UfoState' in content
    assert 'from ..utils.threads import synchronized' in content
    assert 'import threading' in content


def test_synchronized_decorator_available():
    """@synchronized Decorator ist aus utils.threads verfügbar."""
    from core.simulation.utils.threads import synchronized
    
    assert synchronized is not None
    assert callable(synchronized)


def test_state_manager_uses_synchronized():
    """StateManager verwendet @synchronized Decorator."""
    from core.simulation.state import manager as manager_module
    
    # Überprüfe dass synchronized verwendet wird
    with open(manager_module.__file__, 'r') as f:
        content = f.read()
    
    assert 'from ..utils.threads import synchronized' in content
    assert '@synchronized' in content
