#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-Tests für das observer-Modul.

Prüft grundlegende Importierbarkeit, Instantiierung und Dependency-Einhaltung.
"""


def test_observer_module_import():
    """Observer-Modul kann standalone importiert werden."""
    from core.simulation.observer import (
        Phase,
        ManeuverAnalysis,
        compute_phase,
        StateObserver,
    )

    assert Phase is not None
    assert ManeuverAnalysis is not None
    assert compute_phase is not None
    assert StateObserver is not None


def test_phase_type_is_literal():
    """Phase ist ein Literal-Type mit den erwarteten Werten."""
    from core.simulation.observer import Phase
    from typing import get_args

    # Phase sollte ein Literal sein
    args = get_args(Phase)
    expected_phases = {"idle", "takeoff", "hovering", "flying", "landing", "landed", "crashed"}

    assert set(args) == expected_phases


def test_compute_phase_callable():
    """compute_phase ist aufrufbar."""
    from core.simulation.observer import compute_phase
    from core.simulation.state import UfoState

    assert callable(compute_phase)

    # Minimaler Aufruf sollte funktionieren
    state = UfoState()
    result = compute_phase(state)
    assert result in ["idle", "takeoff", "flying", "landing", "landed", "crashed"]


def test_maneuver_analysis_instantiation():
    """ManeuverAnalysis kann instantiiert werden."""
    from core.simulation.observer import ManeuverAnalysis

    # Minimale Instantiierung
    analysis = ManeuverAnalysis(phase="idle")
    assert analysis is not None
    assert analysis.phase == "idle"

    # Vollständige Instantiierung
    analysis_full = ManeuverAnalysis(
        phase="flying",
        is_ascending=True,
        is_descending=False,
        is_turning=True,
        is_stagnating=False,
        avg_vz=1.5,
        avg_heading_change=10.0,
    )
    assert analysis_full.phase == "flying"
    assert analysis_full.is_ascending is True


def test_state_observer_instantiation():
    """StateObserver kann ohne Dependencies instantiiert werden."""
    from core.simulation.observer import StateObserver

    # Default-Initialisierung
    observer = StateObserver()
    assert observer is not None

    # Mit Config
    from core.simulation.infrastructure import SimulationConfig

    config = SimulationConfig(observer_history_size=20)
    observer_with_config = StateObserver(config)
    assert observer_with_config is not None
    assert observer_with_config.config == config


def test_state_observer_has_required_methods():
    """StateObserver hat alle geforderten Methoden."""
    from core.simulation.observer import StateObserver

    observer = StateObserver()

    # Geforderte Methoden aus Spec
    assert hasattr(observer, "observe")
    assert hasattr(observer, "analyze")
    assert hasattr(observer, "get_maneuver_description")

    # Alle Methoden sollten aufrufbar sein
    assert callable(observer.observe)
    assert callable(observer.analyze)
    assert callable(observer.get_maneuver_description)


def test_state_observer_has_history():
    """StateObserver hat history-Attribut als deque."""
    from collections import deque

    from core.simulation.observer import StateObserver

    observer = StateObserver()

    assert hasattr(observer, "history")
    assert isinstance(observer.history, deque)


def test_observer_module_has_no_forbidden_dependencies():
    """Observer-Modul hat keine verbotenen Dependencies."""
    from core.simulation.observer import observer as observer_module

    # Observer-Modul laden
    module_source = observer_module.__file__

    # Verbotene Imports gemäß Spec (Sicherstellung)
    forbidden_imports = [
        "from ..state.manager",
        "from .state.manager",
        "import state.manager",
        "from ..physics",
        "from .physics",
        "import physics",
        "from ..command",
        "from .command",
        "import command",
        "from ..controller",
        "from .controller",
        "import controller",
        "from ..view",
        "from .view",
        "import view",
    ]

    # Modul-Quelltext überprüfen
    with open(module_source, "r", encoding="utf-8") as f:
        content = f.read()

    for forbidden in forbidden_imports:
        assert (
            forbidden not in content
        ), f"Observer sollte nicht '{forbidden}' verwenden"

    # Erlaubte Dependencies sollten vorhanden sein
    assert "from ..infrastructure import" in content
    assert "from ..state.state import UfoState" in content
    assert "from collections import deque" in content
    assert "import numpy" in content


def test_observer_module_exports():
    """Observer-Modul exportiert die erwarteten Symbole."""
    from core.simulation import observer as observer_module

    expected_exports = {
        "Phase",
        "ManeuverAnalysis",
        "compute_phase",
        "normalize_heading_delta",
        "StateObserver",
    }

    assert hasattr(observer_module, "__all__")
    assert set(observer_module.__all__) == expected_exports


def test_observer_integration_with_state():
    """Observer kann mit UfoState arbeiten."""
    from core.simulation.observer import StateObserver, compute_phase
    from core.simulation.state import UfoState

    # State erstellen
    state = UfoState(z=10.0, v=10.0, ftime=5.0, dist=20.0)

    # compute_phase sollte funktionieren
    phase = compute_phase(state)
    assert phase == "flying"

    # Observer sollte State akzeptieren
    observer = StateObserver()
    observer.observe(state)
    assert len(observer.history) == 1

    # Analyse sollte funktionieren
    analysis = observer.analyze()
    assert analysis.phase == "flying"


def test_observer_uses_config_thresholds():
    """Observer verwendet Config-Schwellenwerte korrekt."""
    from core.simulation.infrastructure import SimulationConfig
    from core.simulation.observer import StateObserver

    config = SimulationConfig(
        observer_history_size=100,
        climb_vz_threshold_ms=1.0,
        descent_vz_threshold_ms=-1.0,
        turn_heading_threshold_deg=10.0,
    )

    observer = StateObserver(config)

    # Config sollte gesetzt sein
    assert observer.config.observer_history_size == 100
    assert observer.config.climb_vz_threshold_ms == 1.0
    assert observer.config.descent_vz_threshold_ms == -1.0
    assert observer.config.turn_heading_threshold_deg == 10.0

    # History maxlen sollte von Config kommen
    assert observer.history.maxlen == 100

def test_observer_does_not_modify_state():
    """Observer modifiziert empfangene States nicht."""
    from core.simulation.observer import StateObserver
    from core.simulation.state import UfoState

    observer = StateObserver()

    # Originaler State
    original = UfoState(x=10.0, y=20.0, z=5.0, v=10.0)

    # Observer beobachtet
    observer.observe(original)

    # Observer erstellt Kopie
    observed = observer.history[0]

    # Werte sind gleich
    assert observed.x == original.x
    assert observed.y == original.y

    # Aber es sind unterschiedliche Objekte (defensive Kopie)
    # (frozen dataclass kann nicht modifiziert werden, aber Prinzip bleibt)
    assert observed is not original
