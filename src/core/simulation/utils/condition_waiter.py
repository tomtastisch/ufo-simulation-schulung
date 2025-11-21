#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zentrale Utility für Condition-basiertes Warten ohne Busy-Waiting."""

from __future__ import annotations

import threading
import time
from typing import Callable, Optional, TypeVar

T = TypeVar('T')


class ConditionWaiter:
    """
    Zentrale Utility-Klasse für event-basiertes Warten auf Bedingungen.

    Bietet wiederverwendbare Logik für Condition-Variable-basiertes Warten
    ohne Busy-Waiting. Verwendet von StateManager, UfoSim und anderen Klassen.

    Design:
        - Stateless: Keine Instanz-Variablen, nur statische Methoden
        - Generisch: Funktioniert mit beliebigen State-Typen
        - Thread-sicher: Korrektes Condition-Variable-Handling
        - Timeout-aware: Präzise Timeout-Berechnung ohne Race Conditions

    Example:
        >>> condition_var = threading.Condition()
        >>> state = {"value": 0}
        >>>
        >>> def check_value(s):
        ...     return s["value"] >= 10
        >>>
        >>> # In anderem Thread: state["value"] wird erhöht und notify_all() aufgerufen
        >>>
        >>> result = ConditionWaiter.wait_for_condition(
        ...     condition_var=condition_var,
        ...     predicate=check_value,
        ...     state_getter=lambda: state,
        ...     timeout=5.0
        ... )
    """

    @staticmethod
    def wait_for_condition(
        condition_var: threading.Condition,
        predicate: Callable[[T], bool],
        state_getter: Callable[[], T],
        timeout: Optional[float] = None
    ) -> bool:
        """
        Wartet event-basiert bis Prädikat erfüllt ist (kein Busy-Waiting).

        Nutzt Condition Variables für CPU-schonendes Warten. Der aufrufende
        Thread wird blockiert, bis entweder:
        1. Das Prädikat erfüllt ist (Return: True)
        2. Das Timeout abläuft (Return: False)

        Args:
            condition_var: Threading Condition Variable für Synchronisation
            predicate: Funktion die State prüft. Signatur: (state: T) -> bool
            state_getter: Funktion die aktuellen State liefert. Signatur: () -> T
            timeout: Optionales Timeout in Sekunden. None = unbegrenztes Warten

        Returns:
            True wenn Prädikat erfüllt, False bei Timeout

        Thread-Safety:
            - Context Manager: Automatisches Lock-Management via 'with'
            - Spurious Wakeups: Prädikat wird nach jedem Aufwachen neu geprüft
            - Timeout-Precision: Verbleibende Zeit wird bei jedem Wake-Up neu berechnet
            - Deadlock-frei: Condition-Variable wird korrekt verwendet

        Implementation Notes:
            - While-Loop gegen spurious wakeups (POSIX Condition-Variable-Standard)
            - Timeout-Berechnung: end_time fixiert, remaining dynamisch
            - State-Getter wird unter Lock aufgerufen (atomare Prüfung)

        Example::

            # Mit Timeout
            success = ConditionWaiter.wait_for_condition(
                condition_var=my_condition,
                predicate=lambda s: s.z <= 0.0,
                state_getter=lambda: my_state,
                timeout=30.0
            )

            # Unbegrenzt warten
            ConditionWaiter.wait_for_condition(
                condition_var=my_condition,
                predicate=lambda s: s.ready,
                state_getter=lambda: my_state
            )
        """
        with condition_var:
            # Timeout-Endzeit berechnen (None wenn unbegrenzt)
            end_time = None if timeout is None else time.time() + timeout

            # While-Loop: Schutz gegen spurious wakeups
            while True:
                # Prädikat prüfen (state_getter wird unter Lock aufgerufen)
                current_state = state_getter()
                if predicate(current_state):
                    return True

                # Timeout-Handling
                if end_time is not None:
                    remaining = end_time - time.time()
                    if remaining <= 0:
                        # Timeout abgelaufen
                        return False
                    wait_timeout = remaining
                else:
                    # Unbegrenztes Warten
                    wait_timeout = None

                # Warten auf Notification (gibt Lock temporär frei)
                condition_var.wait(timeout=wait_timeout)

