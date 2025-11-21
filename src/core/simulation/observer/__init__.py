#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Observer-Modul für Phasenbestimmung und Manöveranalyse.

=== ZWECK ===

Das observer-Modul implementiert die rein lesende Analyse-Logik für UFO-Zustände.
Es erkennt Flugphasen und Manöver deterministisch aus dem aktuellen Zustand bzw.
aus einer Historie von Zuständen, ohne selbst Schreibzugriffe vorzunehmen.

Dieses Modul folgt dem Observer-Pattern und ist vollständig entkoppelt von der
Simulationssteuerung, Physik-Engine und View-Layer.

=== BESTANDTEILE ===

1. **Phase (Type Alias)**
   - Literal-Type für die sechs möglichen Flugphasen
   - Typen: "idle", "takeoff", "flying", "landing", "landed", "crashed"
   - Wird von compute_phase() zurückgegeben

2. **compute_phase() (Funktion)**
   - Regelbasierte Phasenbestimmung aus einem einzelnen UfoState
   - Deterministisch und threadsicher (zustandslos)
   - Prioritätsbasierte Auswertung (crashed > landed > takeoff > landing > flying > idle)
   - Verwendet Config-basierte Schwellenwerte (keine Magic Numbers)

3. **ManeuverAnalysis (Dataclass)**
   - Strukturierte Ergebnis-Datenklasse der Manöveranalyse
   - Felder: phase, is_ascending, is_descending, is_turning, is_stagnating
   - Zusätzliche Metriken: avg_vz, avg_heading_change
   - Wird von StateObserver.analyze() erzeugt

4. **StateObserver (Klasse)**
   - Historie-basierte Manöver-Erkennung
   - Verwendet collections.deque als Ringpuffer für die letzten N Zustände
   - Methoden:
     * observe(state): Fügt Zustand zur Historie hinzu
     * analyze(): Berechnet ManeuverAnalysis aus Historie
     * get_maneuver_description(): Liefert lesbare String-Beschreibung
   - Erkennt Trends: Steigflug, Sinkflug, Kurven, Stagnation
   - Rein lesend - keine Modifikation von Zuständen

=== VERANTWORTLICHKEITEN ===

**Zuständig für:**
- Phasen-Erkennung aus Zustandswerten
- Trend-Analyse aus Zustandshistorie
- Manöver-Klassifikation (ascending, descending, turning, stagnating)
- Lesbare Ausgabe von Manöver-Beschreibungen

**NICHT zuständig für:**
- Zustandsänderungen (StateManager ist verantwortlich)
- Physikalische Berechnungen (PhysicsEngine ist verantwortlich)
- Command-Verarbeitung (CommandExecutor ist verantwortlich)
- Visualisierung (View-Layer ist verantwortlich)

=== DEPENDENCY-REGELN ===

Das observer-Modul darf NUR folgende Abhängigkeiten haben:
- infrastructure (SimulationConfig, DEFAULT_CONFIG, Logging)
- state.state (UfoState - nur lesen!)
- collections.deque (für Ringpuffer)
- dataclasses.replace (für defensive Kopien)
- numpy (für Vektorberechnungen)
- typing (für Type Hints)

VERBOTEN sind Abhängigkeiten zu:
- state.manager (Zirkel-Gefahr)
- physics (Trennung der Concerns)
- command (Observer kennt keine Commands)
- controller (Observer ist Teil der Domäne, nicht der Steuerung)
- view (strikte Trennung Domäne/UI)

=== STRUKTUR ===

src/core/simulation/observer/
├── __init__.py          # Dieses Modul - Exports und Dokumentation
└── observer.py          # Implementierung aller Komponenten

Öffentliche API (exportiert über __all__):
- Phase
- ManeuverAnalysis
- compute_phase
- StateObserver

=== VERWENDUNG ===

Beispiel - Einfache Phasen-Erkennung:
    >>> from core.simulation.observer import compute_phase
    >>> from core.simulation.state import UfoState
    >>> state = UfoState(z=10.0, v=5.0, vz=1.0)
    >>> phase = compute_phase(state)
    >>> print(phase)
    'flying'

Beispiel - Historie-basierte Analyse:
    >>> from core.simulation.observer import StateObserver
    >>> from core.simulation.infrastructure import DEFAULT_CONFIG
    >>> observer = StateObserver(DEFAULT_CONFIG)
    >>> observer.observe(state1)
    >>> observer.observe(state2)
    >>> analysis = observer.analyze()
    >>> print(f"Phase: {analysis.phase}, Ascending: {analysis.is_ascending}")

Beispiel - Integration mit StateManager:
    >>> from core.simulation.state import StateManager
    >>> from core.simulation.observer import StateObserver
    >>> manager = StateManager()
    >>> observer = StateObserver()
    >>> manager.register_observer(observer.observe)
    >>> # Observer wird nun bei jedem State-Update automatisch benachrichtigt

=== DESIGN-PRINZIPIEN ===

1. **Reine Funktionen**: compute_phase() ist zustandslos und deterministisch
2. **Immutability**: Observer kopiert empfangene States (dataclass_replace)
3. **Trennung der Concerns**: Nur Lese-Logik, keine Schreibzugriffe
4. **Config-driven**: Alle Schwellenwerte aus SimulationConfig
5. **Testbarkeit**: Vollständig unit-testbar ohne I/O oder Threading
6. **Thread-Safety**: Durch Verwendung von Snapshots (keine Locks nötig)

=== VERSION ===

Version: 5.2.0 (Teil des Phase 4.2 Refactorings)
Erstellt: 2025-11-21
Ticket: T9 - Abschnitt 4.2
"""

from .observer import (
    Phase,
    ManeuverAnalysis,
    compute_phase,
    StateObserver,
)

__all__ = [
    "Phase",
    "ManeuverAnalysis",
    "compute_phase",
    "StateObserver",
]
