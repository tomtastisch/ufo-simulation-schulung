#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thread-sicherer State-Manager für UFO-Zustandsverwaltung."""

from __future__ import annotations

import logging
import threading
from dataclasses import replace as dataclass_replace
from typing import Callable, List, Optional

from .state import UfoState
from ..synchronization import conditional
from ..utils.threads import synchronized

logger = logging.getLogger(__name__)


class StateManager:
    """
    Thread-sicherer Manager für UFO-Zustand mit Observer-Pattern.

    Verwaltet atomare Updates auf immutable UfoState und benachrichtigt
    registrierte Observer bei Zustandsänderungen. Event-basiertes Warten
    via Condition Variables.
    """

    def __init__(self, initial_state: Optional[UfoState] = None) -> None:
        """Initialisiert StateManager mit optionalem Anfangszustand."""
        self._state: UfoState = initial_state if initial_state is not None else UfoState()
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._observers: List[Callable[[UfoState], None]] = []
        logger.debug("StateManager initialized")

    @synchronized
    def get_snapshot(self) -> UfoState:
        """Gibt thread-sicheren Snapshot des aktuellen Zustands zurück."""
        return dataclass_replace(self._state)

    def update_state(self, update_func: Callable[[UfoState], UfoState]) -> None:
        """
        Führt atomare State-Aktualisierung aus und benachrichtigt Observer.

        update_func erhält aktuellen State und gibt neuen State zurück (immutable Pattern).
        """
        # Kritischer Abschnitt unter @conditional Lock
        snapshot, observers = self._update_state_atomic(update_func)

        # Observer außerhalb Lock benachrichtigen (Deadlock-Vermeidung)
        self._notify_observers(snapshot, observers)

    @conditional
    def _update_state_atomic(
        self,
        update_func: Callable[[UfoState], UfoState]
    ) -> tuple[UfoState, List[Callable[[UfoState], None]]]:
        """Atomarer State-Update unter Condition-Lock (private Methode)."""
        self._state = update_func(self._state)
        self._condition.notify_all()
        snapshot = dataclass_replace(self._state)
        observers_snapshot = list(self._observers)
        return snapshot, observers_snapshot

    @staticmethod
    def _notify_observers(snapshot: UfoState, observers: List[Callable[[UfoState], None]]) -> None:
        """
        Benachrichtigt alle registrierten Observer über State-Änderung.

        Observer-Exceptions werden geloggt, beeinflussen andere Observer nicht.
        """
        for observer in observers:
            try:
                observer(snapshot)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")

    @synchronized
    def register_observer(self, observer: Callable[[UfoState], None]) -> None:
        """Registriert Observer für State-Änderungen."""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observer registered, total: {len(self._observers)}")

    @synchronized
    def unregister_observer(self, observer: Callable[[UfoState], None]) -> None:
        """Entfernt Observer aus Benachrichtigungsliste."""
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"Observer unregistered, remaining: {len(self._observers)}")

    def wait_for_condition(
        self, condition: Callable[[UfoState], bool], timeout: Optional[float] = None
    ) -> bool:
        """Wartet bis Bedingung erfüllt ist (event-basiert, kein Busy-Waiting).

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

        Example::

            # Warte bis Landung (mit Timeout)
            landed = manager.wait_for_condition(
                lambda s: s.z <= 0.1,
                timeout=30.0
            )
            if landed:
                print("Gelandet!")

            # Warte unbegrenzt bis Ziel-Höhe
            manager.wait_for_condition(lambda s: s.z >= 100.0)
        """
        # Delegation an zentrale ConditionWaiter-Utility
        from ..utils.condition_waiter import ConditionWaiter

        return ConditionWaiter.wait_for_condition(
            condition_var=self._condition,
            predicate=condition,
            state_getter=lambda: self._state,
            timeout=timeout
        )



    def reset(self) -> None:
        """
        Setzt State auf Ausgangszustand zurück.

        Erstellt einen neuen Default-UfoState und benachrichtigt alle Observer.
        Alle wartenden Threads werden aufgeweckt (via notify_all).

        Thread-Safety:
            Diese Methode ist thread-sicher und atomar via @conditional.

        Example::

            manager.reset()  # State zurück auf Startposition
        """
        # Kritischer Abschnitt unter @conditional Lock
        snapshot, observers = self._reset_atomic()

        # Observer außerhalb Lock benachrichtigen
        self._notify_observers(snapshot, observers)

    @conditional
    def _reset_atomic(self) -> tuple[UfoState, List[Callable[[UfoState], None]]]:
        """
        Atomarer State-Reset unter Condition-Lock (private Methode).

        Diese Methode ist mit @conditional dekoriert und führt den kritischen
        Abschnitt aus: State-Reset, Notification und Snapshot-Erstellung.

        Returns:
            Tuple aus (snapshot, observers_list) für externe Benachrichtigung
        """
        self._state = UfoState()
        self._condition.notify_all()  # Kein nested lock dank @conditional
        snapshot = dataclass_replace(self._state)
        observers_snapshot = list(self._observers)
        logger.debug("State reset")
        return snapshot, observers_snapshot

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
