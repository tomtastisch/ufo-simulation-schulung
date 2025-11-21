#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Observer-Modul für Phasen- und Manöver-Analyse der UFO-Simulation.

Modulzweck
----------
Dieses Modul stellt rein lesende Analyse-Funktionen für die UFO-Simulation bereit.
Es ermöglicht die Bestimmung der aktuellen Flugphase und die Erkennung von
Manövern aus dem Zustandsverlauf, ohne den State selbst zu modifizieren.

Strukturelle Verantwortlichkeiten
----------------------------------
Das Observer-Modul folgt diesen Architektur-Prinzipien:

1. **Rein lesende Operationen**: Keine Schreibzugriffe auf UfoState oder andere
   Simulationskomponenten. Der Observer ist ein passiver Beobachter.

2. **Clean Architecture**: Strikte Trennung zwischen Observation (lesend) und
   Steuerung (schreibend). Keine Abhängigkeiten zu Controller, Command oder View.

3. **Zustandslose Phasenbestimmung**: `compute_phase()` ist eine reine Funktion,
   die deterministisch aus einem UfoState die Phase ableitet.

4. **Historien-basierte Analyse**: StateObserver nutzt einen Ringpuffer für
   Trend-Erkennung (Steigen/Sinken, Drehung, Stagnation).

Modul-Bestandteile
------------------
observer.py:
    - Phase (Literal-Type): Definiert die 6 möglichen Flugphasen
    - compute_phase(): Leitet Phase aus aktuellem State ab
    - ManeuverAnalysis (Dataclass): Strukturierte Manöver-Beschreibung
    - StateObserver (Klasse): Historien-basierte Manöver-Erkennung

Erlaubte Abhängigkeiten
-----------------------
Das Observer-Modul darf NUR importieren:
    - SimulationConfig, DEFAULT_CONFIG (aus infrastructure)
    - UfoState (aus state.state)
    - numpy (für numerische Berechnungen)
    - collections.deque (für Ringpuffer)
    - dataclasses.replace (für State-Snapshots)
    - logging (für Diagnose-Ausgaben)

Verbotene Abhängigkeiten
------------------------
Das Observer-Modul darf NICHT importieren:
    - UfoSim (Controller-Schicht)
    - StateManager (State-Management-Schicht)
    - CommandQueue, CommandExecutor (Command-Schicht)
    - PhysicsEngine (Physik-Schicht)
    - View-Komponenten (View-Schicht)

Öffentliche API
---------------
Typen:
    - Phase: Literal["idle", "takeoff", "flying", "landing", "landed", "crashed"]

Funktionen:
    - compute_phase(state, config): Bestimmt Phase aus aktuellem Zustand

Klassen:
    - ManeuverAnalysis: Strukturierte Manöver-Beschreibung mit Flags
    - StateObserver: Historien-basierte Manöver-Erkennung

Verwendungsbeispiele
--------------------
Phasenbestimmung (zustandslos):
    >>> from core.simulation.observer import compute_phase
    >>> from core.simulation.state import UfoState
    >>> from core.simulation.infrastructure import DEFAULT_CONFIG
    >>>
    >>> state = UfoState(z=0.0, v=0.0, dist=0.0, ftime=0.0)
    >>> phase = compute_phase(state, DEFAULT_CONFIG)
    >>> print(phase)  # "idle"
    >>>
    >>> state2 = UfoState(z=10.0, v=15.0, ftime=0.0)
    >>> phase2 = compute_phase(state2, DEFAULT_CONFIG)
    >>> print(phase2)  # "takeoff"

Manöver-Analyse (historien-basiert):
    >>> from core.simulation.observer import StateObserver, ManeuverAnalysis
    >>> from core.simulation.state import UfoState
    >>> from core.simulation.infrastructure import DEFAULT_CONFIG
    >>>
    >>> observer = StateObserver(DEFAULT_CONFIG)
    >>>
    >>> # Zustände hinzufügen (z.B. aus Simulation)
    >>> for i in range(10):
    ...     state = UfoState(z=float(i), vz=1.0, v=10.0)
    ...     observer.observe(state)
    >>>
    >>> # Analyse abrufen
    >>> analysis = observer.analyze()
    >>> print(f"Phase: {analysis.phase}")
    >>> print(f"Steigend: {analysis.is_ascending}")
    >>> print(f"Durchschnittliche vz: {analysis.avg_vz:.2f} m/s")
    >>>
    >>> # Lesbare Beschreibung
    >>> description = observer.get_maneuver_description()
    >>> print(description)  # "Phase: flying, climbing, vz=1.00m/s"

Phasen-Prioritäten
------------------
Die Phase wird durch regelbasierte Evaluation mit Prioritätsreihenfolge bestimmt.
Erste erfüllte Bedingung gewinnt:

1. **crashed**: z < 0 (unter Boden, Crash-Marker)
2. **landed**: z == 0 und v == 0 und has_flown (erfolgreich gelandet)
3. **takeoff**: ftime == 0 und v > 0 und z > 0 (gerade abgehoben)
4. **landing**: v > 0 und vz < 0 und 0 < z <= landing_height (Landeanflug)
5. **flying**: v > 0 und z > 0 (normale Flugphase)
6. **idle**: Default-Fall (am Boden, noch nicht geflogen)

Manöver-Flags
-------------
StateObserver.analyze() ermittelt aus der Historie diese Flags:

- is_ascending: Durchschnittliche vz > climb_vz_threshold_ms
- is_descending: Durchschnittliche vz < descent_vz_threshold_ms
- is_turning: Durchschnittliche Heading-Änderung > turn_heading_threshold_deg
- is_stagnating: Bewegung < 50% der erwarteten Distanz (bei v > 0)

Alle Schwellenwerte sind in SimulationConfig konfigurierbar.

Thread-Sicherheit
-----------------
- compute_phase(): Thread-sicher (reine Funktion, zustandslos)
- StateObserver: NICHT thread-sicher. Aufrufer muss Synchronisation sicherstellen,
  wenn observe() und analyze() aus verschiedenen Threads aufgerufen werden.
  Empfehlung: Observer-Instanz pro Thread oder externe Synchronisation.

Performance-Hinweise
--------------------
- compute_phase(): O(1), sehr schnell, keine Allokationen
- StateObserver.observe(): O(1), fügt State zur deque hinzu
- StateObserver.analyze(): O(n) mit n = min(history_size, 10)
  - Berechnet Durchschnitte über max. 10 letzte Zustände
  - NumPy-Vektoroperationen für Distanzberechnungen

Erweiterbarkeit
---------------
Zukünftige Erweiterungen könnten sein:
    - metrics.py: Performance-Metriken (Flugeffizienz, Energieverbrauch)
    - trajectory.py: Trajektorien-Analyse und Vorhersage
    - anomaly.py: Anomalie-Erkennung (unerwartetes Verhalten)

Architektur-Prinzipien
----------------------
- Separation of Concerns: Observation vs. Control
- Single Responsibility: Nur Phasen- und Manöver-Analyse
- Open/Closed: Erweiterbar für neue Analysen, geschlossen für Änderungen
- Dependency Inversion: Abhängig von Abstraktionen (UfoState), nicht von Details
"""

from __future__ import annotations

from .observer import ManeuverAnalysis, Phase, StateObserver, compute_phase

__all__ = [
    # Typen
    "Phase",
    # Funktionen
    "compute_phase",
    # Klassen
    "ManeuverAnalysis",
    "StateObserver",
]
