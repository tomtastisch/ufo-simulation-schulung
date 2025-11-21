#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit-Tests für zentrale Lock-Wrapper-Utilities."""

import threading
import time
import pytest

from src.core.simulation.synchronization._lock_wrapper import (
    _acquire_lock,
    create_lock_wrapper,
)


class TestAcquireLock:
    """Tests für _acquire_lock Context Manager."""

    def test_acquire_release_rlock(self):
        """_acquire_lock sollte RLock korrekt acquiren und releasen."""
        lock = threading.RLock()

        with _acquire_lock(lock):
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
        """_acquire_lock sollte Lock korrekt acquiren und releasen."""
        lock = threading.Lock()

        with _acquire_lock(lock):
            # Lock ist acquired, zweites Acquire sollte blockieren
            acquired = lock.acquire(blocking=False)
            assert acquired is False

        # Nach Context Manager sollte Lock frei sein
        acquired = lock.acquire(blocking=False)
        assert acquired is True
        lock.release()

    def test_acquire_release_condition(self):
        """_acquire_lock sollte Condition korrekt acquiren und releasen."""
        condition = threading.Condition()

        with _acquire_lock(condition):
            # Condition ist acquired
            pass  # Keine direkte Prüfung möglich

        # Nach Context Manager sollte frei sein
        acquired = condition.acquire(blocking=False)
        assert acquired is True
        condition.release()

    def test_exception_releases_lock(self):
        """_acquire_lock sollte Lock auch bei Exception freigeben."""
        lock = threading.RLock()

        with pytest.raises(ValueError):
            with _acquire_lock(lock):
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
        threads = []

        for _ in range(10):
            t = threading.Thread(
                target=lambda: [counter.increment() for _ in range(10)],
                daemon=True
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=5.0)

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

