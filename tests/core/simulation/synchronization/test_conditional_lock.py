#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit-Tests für conditional Decorator."""

import threading
import time
import pytest
from pathlib import Path
import sys

# Stelle sicher, dass das repo root-Verzeichnis im sys.path ist (damit `import src` funktioniert)
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.simulation.synchronization.conditional_lock import conditional
from tests._helpers import run_threaded_workers


class TestConditionalDecorator:
    """Tests für @conditional Decorator."""

    def test_basic_locking(self):
        """@conditional sollte Methode unter Lock ausführen."""

        class TestClass:
            def __init__(self):
                self._lock = threading.RLock()
                self._condition = threading.Condition(self._lock)
                self.value = 0
                self.call_count = 0

            @conditional
            def increment(self):
                """Inkrementiert value unter Lock."""
                self.call_count += 1
                self.value += 1
                self._condition.notify_all()

        obj = TestClass()
        obj.increment()

        assert obj.value == 1
        assert obj.call_count == 1

    def test_notify_all_without_nested_lock(self):
        """@conditional sollte notify_all() ohne nested lock ermöglichen."""

        class Manager:
            def __init__(self):
                self._lock = threading.RLock()
                self._condition = threading.Condition(self._lock)
                self.state = 0

            @conditional
            def update(self, new_value):
                """Update mit Notification - kein nested lock."""
                self.state = new_value
                self._condition.notify_all()  # Sollte funktionieren
                return self.state

        manager = Manager()
        result = manager.update(42)

        assert result == 42
        assert manager.state == 42

    def test_thread_safety_concurrent_access(self):
        """@conditional sollte Thread-Safety garantieren."""

        class Counter:
            def __init__(self):
                self._lock = threading.RLock()
                self._condition = threading.Condition(self._lock)
                self.value = 0

            @conditional
            def increment(self):
                # Simuliere non-atomare Operation
                temp = self.value
                time.sleep(0.001)  # Kurze Verzögerung
                self.value = temp + 1
                self._condition.notify_all()

        counter = Counter()

        # 10 Threads inkrementieren je 10x
        def worker():
            for _ in range(10):
                counter.increment()

        run_threaded_workers(worker, num_threads=10, timeout_per_thread=5.0)

        # Sollte 100 sein (10 Threads * 10 Inkremente)
        assert counter.value == 100

    def test_exception_releases_lock(self):
        """@conditional sollte Lock auch bei Exception freigeben."""

        class ErrorClass:
            def __init__(self):
                self._lock = threading.RLock()
                self._condition = threading.Condition(self._lock)
                self.locked = False

            @conditional
            def failing_method(self):
                # Prüfe ob Lock acquired ist (ohne _is_owned zu verwenden)
                self.locked = not self._lock.acquire(blocking=False) or (self._lock.release() is None and True)
                raise ValueError("Test error")

            def check_lock_free(self):
                # Versuche Lock zu acquiren (sollte sofort möglich sein)
                acquired = self._lock.acquire(blocking=False)
                if acquired:
                    self._lock.release()
                return acquired

        obj = ErrorClass()

        with pytest.raises(ValueError):
            obj.failing_method()

        # Lock sollte freigegeben sein
        assert obj.check_lock_free() is True

    def test_return_value_preserved(self):
        """@conditional sollte Rückgabewerte korrekt durchreichen."""

        class Calculator:
            def __init__(self):
                self._lock = threading.RLock()
                self._condition = threading.Condition(self._lock)

            @conditional
            def add(self, a, b):
                return a + b

            @conditional
            def multiply(self, a, b):
                result = a * b
                self._condition.notify_all()
                return result

        calc = Calculator()

        assert calc.add(2, 3) == 5
        assert calc.multiply(4, 5) == 20

    def test_with_args_and_kwargs(self):
        """@conditional sollte mit verschiedenen Argument-Typen funktionieren."""

        class Accumulator:
            def __init__(self):
                self._lock = threading.RLock()
                self._condition = threading.Condition(self._lock)
                self.values = []

            @conditional
            def add_values(self, *args, **kwargs):
                self.values.extend(args)
                self.values.extend(kwargs.values())
                self._condition.notify_all()
                return len(self.values)

        acc = Accumulator()

        count = acc.add_values(1, 2, 3, x=10, y=20)

        assert count == 5
        assert set(acc.values) == {1, 2, 3, 10, 20}

    def test_missing_condition_raises_error(self):
        """@conditional sollte AttributeError werfen wenn _condition fehlt."""

        class BadClass:
            def __init__(self):
                pass  # Kein self._condition!

            @conditional
            def method(self):
                pass

        obj = BadClass()

        with pytest.raises(AttributeError):
            obj.method()

    def test_compatible_with_rlocks(self):
        """@conditional sollte mit RLocks wiedereintrittsfähig sein."""

        class Reentrant:
            def __init__(self):
                self._lock = threading.RLock()  # RLock!
                self._condition = threading.Condition(self._lock)
                self.depth = 0

            @conditional
            def outer(self):
                self.depth += 1
                if self.depth < 3:
                    self.inner()  # Rekursiver Aufruf
                return self.depth

            @conditional
            def inner(self):
                self.depth += 1
                if self.depth < 3:
                    self.outer()  # Rekursiver Aufruf

        obj = Reentrant()
        result = obj.outer()

        # Sollte funktionieren wegen RLock
        assert result == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
