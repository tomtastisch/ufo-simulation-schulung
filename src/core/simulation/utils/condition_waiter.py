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
    Utility für event-basiertes Warten auf Bedingungen.

    Stateless: Nur statische Methoden. Thread-sicher mit Condition Variables.
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

        Returns:
            True wenn Prädikat erfüllt, False bei Timeout
        """
        with condition_var:
            end_time = None if timeout is None else time.time() + timeout

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

