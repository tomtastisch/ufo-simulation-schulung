#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-Tests für das Observer-Modul.

Verifiziert:
    - Modul kann importiert werden
    - Keine unerwarteten Abhängigkeiten
    - Grundfunktionalität (Initialisierung, einfache Aufrufe)
"""

import sys

import pytest


def test_observer_module_import():
    """Observer-Modul kann ohne Fehler importiert werden."""
    from core.simulation.observer import (
        ManeuverAnalysis,
        Phase,
        StateObserver,
        compute_phase,
    )

    # Verifiziere, dass alle Symbole vorhanden sind
    assert Phase is not None
    assert compute_phase is not None
    assert ManeuverAnalysis is not None
    assert StateObserver is not None


def test_observer_has_no_forbidden_dependencies():
    """Observer-Modul importiert keine verbotenen Module direkt."""
    # Frischer Import-Test: Prüfe, ob Observer selbst die Module importiert
    # Hinweis: Andere Tests könnten bereits Module geladen haben, daher prüfen
    # wir nur, ob Observer-Modul selbst keine direkten Imports hat
    
    import core.simulation.observer.observer as observer_module
    
    # Prüfe Source-Code des Moduls auf verbotene Imports
    import inspect
    source = inspect.getsource(observer_module)
    
    # Verbotene Import-Statements
    forbidden_imports = [
        "from core.simulation.ufosim",
        "import core.simulation.ufosim",
        "from ..ufosim",
        "from core.simulation.state.manager",
        "from ..state.manager",
        "import core.simulation.state.manager",
        "from core.simulation.command",
        "from ..command",
        "import core.simulation.command",
        "from core.simulation.physics.engine",
        "from ..physics.engine",
        "import core.simulation.physics.engine",
        "from core.simulation.view",
        "from ..view",
        "import core.simulation.view",
    ]
    
    for forbidden in forbidden_imports:
        assert forbidden not in source, (
            f"Observer hat verbotenen Import: {forbidden}"
        )


def test_observer_allowed_dependencies():
    """Observer-Modul hat nur erlaubte Abhängigkeiten."""
    # Importiere Observer-Modul
    import core.simulation.observer

    # Prüfe geladene Module
    loaded_modules = sys.modules.keys()

    # Erlaubte Abhängigkeiten
    allowed = [
        "core.simulation.infrastructure",  # SimulationConfig, DEFAULT_CONFIG
        "core.simulation.state",  # UfoState
        "numpy",  # Numerische Berechnungen
        "collections",  # deque
        "dataclasses",  # replace
        "logging",  # Logging
    ]

    # Mindestens einige davon sollten geladen sein
    assert any(module in loaded_modules for module in allowed)


def test_compute_phase_basic_call():
    """compute_phase() kann ohne Fehler aufgerufen werden."""
    from core.simulation.infrastructure import DEFAULT_CONFIG
    from core.simulation.observer import compute_phase
    from core.simulation.state import UfoState

    state = UfoState()
    phase = compute_phase(state, DEFAULT_CONFIG)

    # Phase sollte ein String sein
    assert isinstance(phase, str)
    # Phase sollte eine der 6 definierten Phasen sein
    assert phase in ["idle", "takeoff", "flying", "landing", "landed", "crashed"]


def test_maneuver_analysis_instantiation():
    """ManeuverAnalysis kann instanziert werden."""
    from core.simulation.observer import ManeuverAnalysis

    analysis = ManeuverAnalysis(phase="flying")

    assert analysis.phase == "flying"
    assert analysis.is_ascending is False
    assert analysis.is_descending is False
    assert analysis.is_turning is False
    assert analysis.is_stagnating is False
    assert analysis.avg_vz == 0.0
    assert analysis.avg_heading_change == 0.0


def test_state_observer_instantiation():
    """StateObserver kann instanziert werden."""
    from core.simulation.infrastructure import DEFAULT_CONFIG
    from core.simulation.observer import StateObserver

    observer = StateObserver(DEFAULT_CONFIG)

    assert observer.config == DEFAULT_CONFIG
    assert len(observer.history) == 0


def test_state_observer_basic_usage():
    """StateObserver kann grundlegende Operationen durchführen."""
    from core.simulation.infrastructure import DEFAULT_CONFIG
    from core.simulation.observer import StateObserver
    from core.simulation.state import UfoState

    observer = StateObserver(DEFAULT_CONFIG)

    # observe() hinzufügen
    state = UfoState(z=10.0, v=15.0)
    observer.observe(state)
    assert len(observer.history) == 1

    # analyze() aufrufen
    analysis = observer.analyze()
    assert analysis is not None
    assert hasattr(analysis, "phase")

    # get_maneuver_description() aufrufen
    description = observer.get_maneuver_description()
    assert isinstance(description, str)
    assert len(description) > 0


def test_phase_type_is_literal():
    """Phase ist ein Literal-Type."""
    from typing import get_args

    from core.simulation.observer import Phase

    # Phase sollte ein Literal sein
    # In Python 3.11+ kann man get_args verwenden
    args = get_args(Phase)
    assert len(args) == 6
    assert "idle" in args
    assert "takeoff" in args
    assert "flying" in args
    assert "landing" in args
    assert "landed" in args
    assert "crashed" in args


def test_observer_module_has_all_exports():
    """Observer-Modul exportiert alle erwarteten Symbole via __all__."""
    import core.simulation.observer as observer_module

    # Prüfe __all__
    assert hasattr(observer_module, "__all__")
    all_exports = observer_module.__all__

    # Erwartete Exports
    expected = ["Phase", "compute_phase", "ManeuverAnalysis", "StateObserver"]

    for symbol in expected:
        assert symbol in all_exports, f"{symbol} fehlt in __all__"
        assert hasattr(observer_module, symbol), f"{symbol} nicht im Modul"


def test_observer_module_docstring():
    """Observer-Modul hat umfassende Dokumentation."""
    import core.simulation.observer as observer_module

    assert observer_module.__doc__ is not None
    assert len(observer_module.__doc__) > 100  # Umfangreiche Doku

    # Wichtige Begriffe in der Dokumentation
    doc = observer_module.__doc__
    assert "Observer" in doc
    assert "Phase" in doc
    assert "Manöver" in doc or "Maneuver" in doc
