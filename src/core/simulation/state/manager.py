#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thread-sicherer State-Manager für UFO-Zustandsverwaltung."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import replace as dataclass_replace
from typing import Callable, List, Optional

from .state import UfoState
from ..utils.threads import synchronized

logger = logging.getLogger(__name__)


class StateManager:
    """
    Thread-sicherer Manager für UFO-Zustand.

    Kapselt Zugriff auf UfoState und bietet Event-System für Änderungsbenachrichtigungen.
    Implementiert Observer-Pattern für Listener-Registrierung.

    Refactored für frozen UfoState: update_state() akzeptiert Funktionen, die neuen State zurückgeben.

    Architektur-Prinzipien
    ----------------------
    - **Single Responsibility**: Verwaltet ausschließlich State-Zugriff und Observer-Benachrichtigungen
    - **Thread-Safety**: Alle öffentlichen Methoden sind thread-sicher via @synchronized
    - **Event-basiert**: Condition Variables statt Busy-Waiting für wait_for_condition
    - **Observer-Pattern**: Registrierung mehrerer Listener für State-Änderungen
    - **Defensive Copies**: get_snapshot() liefert immutable Kopien zur Verhinderung von Race Conditions

    Abhängigkeiten
    --------------
    - UfoState: Immutable Dataclass für physikalischen Zustand
    - threading: RLock und Condition für Thread-Synchronisation
    - dataclasses.replace: Erstellung modifizierter State-Kopien
    - @synchronized: Decorator aus utils.threads für automatisches Locking

    KEINE Abhängigkeiten von
    ------------------------
    - PhysicsEngine: StateManager kennt keine Physik-Logik
    - CommandExecutor: StateManager verarbeitet keine Commands
    - UfoSim: StateManager ist unabhängig vom Controller
    - View-Komponenten: StateManager ist UI-agnostisch

    Thread-Safety Garantien
    -----------------------
    1. Atomare Updates: update_state() ist atomar - entweder komplette Änderung oder keine
    2. Konsistente Snapshots: get_snapshot() liefert immer konsistenten Zustand
    3. Exception-sicher: Observer-Fehler beeinflussen nicht andere Observer
    4. Deadlock-frei: Keine nested Locks, Observer werden außerhalb Lock benachrichtigt
    5. Event-basiert: wait_for_condition() nutzt Condition Variables (kein Busy-Waiting)

    Verwendung
    ----------
    Initialisierung:
        >>> manager = StateManager()  # Mit Default-State
        >>> manager = StateManager(initial_state=custom_state)  # Mit Custom-State

    State-Updates (immutable Pattern):
        >>> def move_up(state: UfoState) -> UfoState:
        ...     return dataclass_replace(state, z=state.z + 10.0)
        >>> manager.update_state(move_up)

    Snapshots (defensive Kopien):
        >>> snapshot = manager.get_snapshot()
        >>> print(f"Höhe: {snapshot.z}m")

    Observer-Registrierung:
        >>> def on_state_changed(state: UfoState) -> None:
        ...     print(f"State changed: z={state.z}m")
        >>> manager.register_observer(on_state_changed)

    Event-basiertes Warten:
        >>> # Warte bis UFO Höhe >= 50m erreicht
        >>> success = manager.wait_for_condition(
        ...     lambda s: s.z >= 50.0,
        ...     timeout=10.0
        ... )
        >>> if success:
        ...     print("Ziel-Höhe erreicht!")
        ... else:
        ...     print("Timeout - Höhe nicht erreicht")

    Attributes:
        _state: Aktueller UfoState (protected, nur via update_state ändern)
        _lock: RLock für thread-sichere Zugriffe
        _condition: Condition Variable für event-basiertes Warten
        _observers: Liste registrierter Observer-Callbacks
    """

    def __init__(self, initial_state: Optional[UfoState] = None) -> None:
        """
        Initialisiert StateManager mit optionalem Anfangszustand.

        Args:
            initial_state: Optionaler initialer Zustand (Standard: neuer UfoState())
        """
        self._state: UfoState = initial_state if initial_state is not None else UfoState()
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._observers: List[Callable[[UfoState], None]] = []
        logger.debug("StateManager initialized")

    @synchronized
    def get_snapshot(self) -> UfoState:
        """
        Gibt thread-sicheren Snapshot des aktuellen Zustands zurück.

        Liefert eine defensive Kopie des internen State, um Race Conditions
        bei lesenden Zugriffen zu verhindern. Der zurückgegebene State ist
        immutable (frozen dataclass).

        Returns:
            Kopie des aktuellen UfoState

        Thread-Safety:
            Diese Methode ist thread-sicher und kann parallel zu Updates aufgerufen werden.
        """
        return dataclass_replace(self._state)

    def update_state(self, update_func: Callable[[UfoState], UfoState]) -> None:
        """
        Führt atomare State-Aktualisierung aus und benachrichtigt Observer.

        Wendet die übergebene Funktion auf den aktuellen State an und speichert
        das Ergebnis. Benachrichtigt anschließend alle registrierten Observer
        mit einem Snapshot des neuen Zustands.

        Args:
            update_func: Funktion die neuen State zurückgibt (immutable Pattern).
                        Signatur: (current_state: UfoState) -> UfoState

        Thread-Safety:
            - Atomare Ausführung: Update ist atomar unter Lock
            - Observer werden außerhalb des Locks benachrichtigt (Deadlock-Vermeidung)
            - Exception in Observer beeinflussen nicht andere Observer

        Example:
            >>> # Einfaches Update
            >>> manager.update_state(lambda s: dataclass_replace(s, z=s.z + 1.0))
            >>>
            >>> # Komplexes Update
            >>> def apply_physics(state: UfoState) -> UfoState:
            ...     new_z = state.z + state.vz * dt
            ...     return dataclass_replace(state, z=new_z)
            >>> manager.update_state(apply_physics)
        """
        # Kritischer Abschnitt: State-Update, Snapshot-Erstellung und Observer-Liste kopieren
        with self._lock:
            self._state = update_func(self._state)
            self._condition.notify_all()
            snapshot = dataclass_replace(self._state)
            observers_snapshot = list(self._observers)  # Kopie für thread-sichere Iteration
        
        # Observer außerhalb Lock benachrichtigen (nicht-kritischer Abschnitt)
        self._notify_observers(snapshot, observers_snapshot)

    def _notify_observers(self, snapshot: UfoState, observers: List[Callable[[UfoState], None]]) -> None:
        """
        Benachrichtigt alle registrierten Observer über State-Änderung.

        Diese Methode wird automatisch von update_state() und reset() aufgerufen.
        Exceptions in einzelnen Observern werden geloggt, beeinflussen
        aber nicht die Benachrichtigung anderer Observer.

        Args:
            snapshot: Snapshot des neuen Zustands
            observers: Kopie der Observer-Liste (für thread-sichere Iteration)

        Thread-Safety:
            Diese Methode wird außerhalb des Locks aufgerufen, um Deadlocks
            zu vermeiden (Observer könnten selbst auf StateManager zugreifen).
            Die Observer-Liste wird als Kopie übergeben, um Race Conditions
            bei gleichzeitiger Registrierung/Deregistrierung zu vermeiden.
        """
        for observer in observers:
            try:
                observer(snapshot)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")

    @synchronized
    def register_observer(self, observer: Callable[[UfoState], None]) -> None:
        """
        Registriert Observer für State-Änderungen.

        Der Observer wird bei jedem update_state()-Aufruf mit einem Snapshot
        des neuen Zustands benachrichtigt. Mehrfache Registrierung desselben
        Observers wird ignoriert.

        Args:
            observer: Callable das bei jeder Änderung aufgerufen wird.
                     Signatur: (state: UfoState) -> None

        Thread-Safety:
            Diese Methode ist thread-sicher und kann jederzeit aufgerufen werden.

        Example:
            >>> def log_altitude(state: UfoState) -> None:
            ...     print(f"Altitude: {state.z}m")
            >>> manager.register_observer(log_altitude)
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observer registered, total: {len(self._observers)}")

    @synchronized
    def unregister_observer(self, observer: Callable[[UfoState], None]) -> None:
        """
        Entfernt Observer aus Benachrichtigungsliste.

        Args:
            observer: Zu entfernender Observer

        Thread-Safety:
            Diese Methode ist thread-sicher und kann jederzeit aufgerufen werden.

        Example:
            >>> manager.unregister_observer(log_altitude)
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"Observer unregistered, remaining: {len(self._observers)}")

    def wait_for_condition(
        self, condition: Callable[[UfoState], bool], timeout: Optional[float] = None
    ) -> bool:
        """
        Wartet bis Bedingung erfüllt ist (event-basiert, kein Busy-Waiting).

        Nutzt Condition Variables für effizientes Warten. Der aufrufende Thread
        wird blockiert, bis entweder:
        1. Die Bedingung erfüllt ist (Return: True)
        2. Das Timeout abläuft (Return: False)

        Args:
            condition: Bedingung die State prüft. Signatur: (state: UfoState) -> bool
            timeout: Optionales Timeout in Sekunden. None = unbegrenztes Warten

        Returns:
            True wenn Bedingung erfüllt, False bei Timeout

        Thread-Safety:
            - Event-basiert: Kein Busy-Waiting, CPU-schonend
            - Interrupt-sicher: Kann jederzeit abgebrochen werden
            - Deadlock-frei: Nutzt Condition Variables korrekt

        Example:
            >>> # Warte bis Landung (mit Timeout)
            >>> landed = manager.wait_for_condition(
            ...     lambda s: s.z <= 0.1,
            ...     timeout=30.0
            ... )
            >>> if landed:
            ...     print("Gelandet!")
            >>> else:
            ...     print("Landung dauert zu lange")
            >>>
            >>> # Warte unbegrenzt bis Ziel-Höhe
            >>> manager.wait_for_condition(lambda s: s.z >= 100.0)
        """
        with self._condition:
            end_time = None if timeout is None else time.time() + timeout

            while True:
                if condition(self._state):
                    return True

                if end_time is not None:
                    remaining = end_time - time.time()
                    if remaining <= 0:
                        return False
                    wait_timeout = remaining
                else:
                    wait_timeout = None

                self._condition.wait(timeout=wait_timeout)

    def reset(self) -> None:
        """
        Setzt State auf Ausgangszustand zurück.

        Erstellt einen neuen Default-UfoState und benachrichtigt alle Observer.
        Alle wartenden Threads werden aufgeweckt (via notify_all).

        Thread-Safety:
            Diese Methode ist thread-sicher und atomar.

        Example:
            >>> manager.reset()  # State zurück auf Startposition
        """
        # Kritischer Abschnitt: State-Reset, Snapshot-Erstellung und Observer-Liste kopieren
        with self._lock:
            self._state = UfoState()
            self._condition.notify_all()
            snapshot = dataclass_replace(self._state)
            observers_snapshot = list(self._observers)  # Kopie für thread-sichere Iteration
            logger.debug("State reset")
        
        # Observer außerhalb Lock benachrichtigen (nicht-kritischer Abschnitt)
        self._notify_observers(snapshot, observers_snapshot)

    @property
    def state(self) -> UfoState:
        """
        Direkter Zugriff auf internen State (NICHT thread-sicher!).

        Nur für Legacy-Kompatibilität. Verwende get_snapshot() oder update_state().

        Warning:
            Dieser direkte Zugriff ist NICHT thread-sicher und sollte nur in
            Single-Threaded-Kontexten verwendet werden. Für produktiven Code
            immer get_snapshot() verwenden!

        Returns:
            Direkter Zugriff auf _state (ohne Kopie, ohne Lock)
        """
        return self._state
