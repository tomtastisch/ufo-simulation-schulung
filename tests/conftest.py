#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemeinsame Test-Fixtures und Hilfsfunktionen für alle Tests.

Enthält wiederverwendbare Komponenten für:
- Threading-Tests (Counter, Worker-Patterns)
- Lock-Tests (Race-Condition-Detection)
- Synchronization-Tests (Decorator-Testing)
"""

from __future__ import annotations

import threading
import time
from typing import Dict, Any, Union
from pathlib import Path
import sys

import pytest

# Make project root importable so `import tests._helpers` works in all contexts.
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tests._helpers import (
    run_threaded_workers,
    assert_race_condition_free,
    create_decorated_counter,
    run_manual_tests,
)

# Re-exports: sichtbar machen für statische Analyzer und externe Importe
__all__ = [
    "run_threaded_workers",
    "assert_race_condition_free",
    "create_decorated_counter",
    "run_manual_tests",
]


# =============================================================================
# Threading Test Helpers
# =============================================================================

class ThreadSafeCounter:
    """
    Thread-sicherer Counter für Tests.

    Kann mit oder ohne Lock verwendet werden, um Race-Conditions zu testen.
    """

    def __init__(self, use_lock: bool = False):
        """
        Initialisiert den Counter.

        Args:
            use_lock: Wenn True, wird ein RLock für Thread-Safety verwendet.
        """
        self._value = 0
        self._lock = threading.RLock() if use_lock else None

    def increment(self, delay: float = 0.0001):
        """
        Inkrementiert den Counter (mit optionaler Verzögerung für Race-Condition-Tests).

        Args:
            delay: Verzögerung in Sekunden zwischen Read und Write (default: 0.0001).
        """
        if self._lock:
            with self._lock:
                old_value = self._value
                if delay > 0:
                    time.sleep(delay)
                self._value = old_value + 1
        else:
            old_value = self._value
            if delay > 0:
                time.sleep(delay)
            self._value = old_value + 1

    def add(self, amount: int, delay: float = 0.0001):
        """
        Addiert einen Betrag zum Counter.

        Args:
            amount: Zu addierender Betrag.
            delay: Verzögerung in Sekunden zwischen Read und Write.

        Returns:
            Der neue Wert nach der Addition.
        """
        if self._lock:
            with self._lock:
                old_value = self._value
                if delay > 0:
                    time.sleep(delay)
                self._value = old_value + amount
                return self._value
        else:
            old_value = self._value
            if delay > 0:
                time.sleep(delay)
            self._value = old_value + amount
            return self._value

    def get_value(self):
        """Gibt den aktuellen Wert zurück."""
        if self._lock:
            with self._lock:
                return self._value
        else:
            return self._value

    @property
    def value(self):
        """Property-Zugriff auf den Wert."""
        return self.get_value()


# =============================================================================
# Lock Test Helpers
# =============================================================================

class LockTestHelper:
    """
    Hilfsfunktionen für Lock-Tests.
    """

    @staticmethod
    def create_deadlock_scenario(
        lock1: threading.Lock,
        lock2: threading.Lock,
        delay: float = 0.1
    ) -> tuple[threading.Thread, threading.Thread]:
        """
        Erstellt ein Deadlock-Szenario mit zwei Locks (aber führt es NICHT aus).

        WARNUNG: Diese Funktion ist nur für Tests gedacht, die Deadlock-Detection
        testen. Die zurückgegebenen Threads sind NICHT gestartet.

        Args:
            lock1: Erster Lock.
            lock2: Zweiter Lock.
            delay: Verzögerung zwischen Lock-Akquisitionen.

        Returns:
            Tuple von zwei Thread-Objekten (nicht gestartet).
        """

        def worker1():
            with lock1:
                time.sleep(delay)
                with lock2:
                    pass

        def worker2():
            with lock2:
                time.sleep(delay)
                with lock1:
                    pass

        t1 = threading.Thread(target=worker1, daemon=True)
        t2 = threading.Thread(target=worker2, daemon=True)

        return t1, t2

    @staticmethod
    def test_lock_prevents_race_condition(
        lock: Union[threading.Lock, threading.RLock],
        shared_data: Dict[str, Any],
        num_threads: int = 50,
        operations_per_thread: int = 20
    ) -> bool:
        """
        Testet, ob ein Lock Race-Conditions verhindert.
        """

        def increment_with_lock():
            with lock:
                old = shared_data["value"]
                time.sleep(0.0001)
                shared_data["value"] = old + 1

        def get_value():
            with lock:
                return shared_data["value"]

        return assert_race_condition_free(
            increment_with_lock,
            get_value,
            num_threads=num_threads,
            increments_per_thread=operations_per_thread
        )


# =============================================================================
# Decorator Test Helpers
# =============================================================================

# create_decorated_counter wird aus tests._helpers importiert (siehe oben)


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def thread_safe_counter():
    """Fixture für einen thread-sicheren Counter."""
    return ThreadSafeCounter(use_lock=True)


@pytest.fixture
def unsafe_counter():
    """Fixture für einen NICHT thread-sicheren Counter (für Race-Condition-Tests)."""
    return ThreadSafeCounter(use_lock=False)


@pytest.fixture
def rlock():
    """Fixture für einen RLock."""
    return threading.RLock()


@pytest.fixture
def lock():
    """Fixture für einen Lock."""
    return threading.Lock()


@pytest.fixture
def shared_counter_data():
    """Fixture für gemeinsam genutzte Counter-Daten."""
    return {"value": 0}
