#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit-Tests für zentrale Lock-Wrapper-Utilities."""

import threading
import time
import pytest
from typing import Callable, List
from pathlib import Path
import sys


# add repo root to sys.path so `import src` works
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.simulation.synchronization.lock_wrapper import (
    acquire_lock,
    create_lock_wrapper,
)


def run_threaded_workers(worker: Callable[[], None], *, num_threads: int = 10, timeout_per_thread: float = 5.0) -> None:
    """Hilfsfunktion für Tests: Führt `worker` in mehreren Threads aus und wartet auf Abschluss.

    Args:
        worker: Callable ohne Parameter, das in jedem Thread ausgeführt wird.
        num_threads: Anzahl gleichzeitiger Threads.
        timeout_per_thread: maximale Wartezeit pro Thread in Sekunden.

    Raises:
        RuntimeError: Falls ein oder mehrere Threads nach Ablauf des Timeouts noch laufen.
    """
    threads: List[threading.Thread] = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=timeout_per_thread)

    alive = [t for t in threads if t.is_alive()]
    if alive:
        raise RuntimeError(f"{len(alive)} Thread(s) laufen nach Timeout noch.")


class TestAcquireLock:
    """Tests für acquire_lock Context Manager."""

    def test_acquire_release_rlock(self):
        """acquire_lock sollte RLock korrekt acquiren und releasen."""
        lock = threading.RLock()

        with acquire_lock(lock):
            # Lock sollte acquired sein
            # Versuche zweites Acquire (sollte bei RLock funktionieren)
            acquired = lock.acquire(blocking=False)
            assert acquired is True
            lock.release()

        # Nach Context Manager sollte Lock frei sein
        acquired = lock.acquire(blocking=False)
        assert acquired is True
        lock.release()

    def test_acquire_release_lock(self):
        """acquire_lock sollte Lock korrekt acquiren und releasen."""
        lock = threading.Lock()

        with acquire_lock(lock):
            # Lock ist acquired, zweites Acquire sollte blockieren
            acquired = lock.acquire(blocking=False)
            assert acquired is False

        # Nach Context Manager sollte Lock frei sein
        acquired = lock.acquire(blocking=False)
        assert acquired is True
        lock.release()

    def test_acquire_release_condition(self):
        """acquire_lock sollte Condition korrekt acquiren und releasen."""
        condition = threading.Condition()

        with acquire_lock(condition):
            # Condition ist acquired
            pass  # Keine direkte Prüfung möglich

        # Nach Context Manager sollte frei sein
        acquired = condition.acquire(blocking=False)
        assert acquired is True
        condition.release()

    def test_exception_releases_lock(self):
        """acquire_lock sollte Lock auch bei Exception freigeben."""
        lock = threading.RLock()

        with pytest.raises(ValueError):
            with acquire_lock(lock):
                raise ValueError("Test exception")

        # Lock sollte trotz Exception freigegeben sein
        acquired = lock.acquire(blocking=False)
        assert acquired is True
        lock.release()


class TestCreateLockWrapper:
    """Tests für create_lock_wrapper Factory."""

    def test_wrapper_with_instance_lock(self):
        """create_lock_wrapper sollte für Instanz-Locks funktionieren."""

        class Counter:
            def __init__(self):
                self._lock = threading.RLock()
                self.value = 0

            @create_lock_wrapper(lambda self, *args, **kwargs: self._lock)
            def increment(self):
                self.value += 1

        counter = Counter()
        counter.increment()
        assert counter.value == 1

    def test_wrapper_with_module_lock(self):
        """create_lock_wrapper sollte für Modul-Locks funktionieren."""
        _module_lock = threading.RLock()
        state = {"value": 0}

        @create_lock_wrapper(lambda *args, **kwargs: _module_lock)
        def increment():
            state["value"] += 1

        increment()
        assert state["value"] == 1

    def test_wrapper_with_condition(self):
        """create_lock_wrapper sollte für Condition-Variables funktionieren."""

        class Manager:
            def __init__(self):
                self._lock = threading.RLock()
                self._condition = threading.Condition(self._lock)
                self.state = 0

            @create_lock_wrapper(lambda self, *args, **kwargs: self._condition)
            def update(self, value):
                self.state = value
                self._condition.notify_all()

        manager = Manager()
        manager.update(42)
        assert manager.state == 42

    def test_wrapper_thread_safety(self):
        """create_lock_wrapper sollte Thread-Safety garantieren."""

        class Counter:
            def __init__(self):
                self._lock = threading.RLock()
                self.value = 0

            @create_lock_wrapper(lambda self, *args, **kwargs: self._lock)
            def increment(self):
                # Simuliere non-atomare Operation
                temp = self.value
                time.sleep(0.001)
                self.value = temp + 1

        counter = Counter()

        def worker():
            for _ in range(10):
                counter.increment()

        run_threaded_workers(worker, num_threads=10, timeout_per_thread=5.0)

        assert counter.value == 100

    def test_wrapper_preserves_return_value(self):
        """create_lock_wrapper sollte Rückgabewerte preservieren."""

        class Calculator:
            def __init__(self):
                self._lock = threading.RLock()

            @create_lock_wrapper(lambda self, *args, **kwargs: self._lock)
            def add(self, a, b):
                return a + b

        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5

    def test_wrapper_preserves_args_kwargs(self):
        """create_lock_wrapper sollte Args und Kwargs korrekt durchreichen."""

        class Accumulator:
            def __init__(self):
                self._lock = threading.RLock()
                self.values = []

            @create_lock_wrapper(lambda self, *args, **kwargs: self._lock)
            def add_values(self, *args, **kwargs):
                self.values.extend(args)
                self.values.extend(kwargs.values())
                return len(self.values)

        acc = Accumulator()
        count = acc.add_values(1, 2, 3, x=10, y=20)

        assert count == 5
        assert set(acc.values) == {1, 2, 3, 10, 20}

    def test_wrapper_exception_safety(self):
        """create_lock_wrapper sollte Lock bei Exception freigeben."""

        class ErrorClass:
            def __init__(self):
                self._lock = threading.RLock()

            @create_lock_wrapper(lambda self, *args, **kwargs: self._lock)
            def failing_method(self):
                raise ValueError("Test error")

            def check_lock_free(self):
                acquired = self._lock.acquire(blocking=False)
                if acquired:
                    self._lock.release()
                return acquired

        obj = ErrorClass()

        with pytest.raises(ValueError):
            obj.failing_method()

        # Lock sollte freigegeben sein
        assert obj.check_lock_free() is True

    def test_wrapper_with_different_lock_types(self):
        """create_lock_wrapper sollte mit verschiedenen Lock-Typen funktionieren."""

        # Test mit Lock
        class WithLock:
            def __init__(self):
                self._lock = threading.Lock()
                self.value = 0

            @create_lock_wrapper(lambda self, *args, **kwargs: self._lock)
            def increment(self):
                self.value += 1

        obj1 = WithLock()
        obj1.increment()
        assert obj1.value == 1

        # Test mit RLock
        class WithRLock:
            def __init__(self):
                self._lock = threading.RLock()
                self.value = 0

            @create_lock_wrapper(lambda self, *args, **kwargs: self._lock)
            def increment(self):
                self.value += 1

        obj2 = WithRLock()
        obj2.increment()
        assert obj2.value == 1

        # Test mit Condition
        class WithCondition:
            def __init__(self):
                self._condition = threading.Condition()
                self.value = 0

            @create_lock_wrapper(lambda self, *args, **kwargs: self._condition)
            def increment(self):
                self.value += 1

        obj3 = WithCondition()
        obj3.increment()
        assert obj3.value == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
