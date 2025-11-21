#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kleine Test-Helfer, damit Tests zuverlässig ohne `conftest`-Imports laufen.

Enthält:
- run_threaded_workers: startet mehrere Threads und wartet auf Abschluss
- assert_race_condition_free: prüft auf Race-Conditions
- create_decorated_counter: Hilfs-Factory für decorator-Tests
- run_manual_tests: einfacher Runner für `if __name__ == '__main__'`
"""
from __future__ import annotations

import threading
import time
from typing import Callable, List, Dict, Any, Optional


def run_threaded_workers(worker_func: Callable[[], None], num_threads: int = 10, timeout_per_thread: float = 10.0) -> List[threading.Thread]:
    """Führt eine Worker-Funktion in mehreren Threads aus und wartet auf Abschluss.

    Raises TimeoutError, wenn Threads nicht rechtzeitig fertig werden.
    """
    threads: List[threading.Thread] = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker_func, daemon=False)
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=timeout_per_thread)
        if t.is_alive():
            raise TimeoutError(f"Thread did not complete within {timeout_per_thread}s")

    return threads


def assert_race_condition_free(
    increment_func: Callable[[], None],
    get_value_func: Callable[[], int],
    num_threads: int = 100,
    increments_per_thread: int = 100,
    timeout: float = 30.0,
) -> bool:
    """Helper: Erwartet num_threads*increments_per_thread am Ende.

    Wirft AssertionError bei Abweichung.
    """
    expected = num_threads * increments_per_thread

    def worker():
        for _ in range(increments_per_thread):
            increment_func()

    run_threaded_workers(worker, num_threads=num_threads, timeout_per_thread=timeout)

    actual = get_value_func()
    assert actual == expected, f"Race-Condition detected: Expected {expected}, got {actual}"
    return True


def create_decorated_counter(decorator: Callable, lock: Optional[threading.RLock] = None) -> Dict[str, Any]:
    """Erstellt increment/get_value/add mit Dekorator angewendet.

    Nützlich für tests von synchronized/synchronized_module.
    """
    data: Dict[str, int] = {"value": 0}

    if lock is not None:
        @decorator(lock)
        def increment():
            old = data["value"]
            time.sleep(0.0001)
            data["value"] = old + 1

        @decorator(lock)
        def get_value():
            return data["value"]

        @decorator(lock)
        def add(amount: int):
            old = data["value"]
            time.sleep(0.0001)
            data["value"] = old + amount
            return data["value"]
    else:
        @decorator
        def increment():
            old = data["value"]
            time.sleep(0.0001)
            data["value"] = old + 1

        @decorator
        def get_value():
            return data["value"]

        @decorator
        def add(amount: int):
            old = data["value"]
            time.sleep(0.0001)
            data["value"] = old + amount
            return data["value"]

    return {"increment": increment, "get_value": get_value, "add": add, "data": data}


def run_manual_tests(module_name: str, tests: list[Callable[[], None]]) -> None:
    failures = 0
    for t in tests:
        try:
            t()
            print(f"OK: {t.__name__}")
        except Exception as e:
            failures += 1
            print(f"FAIL: {t.__name__}: {e}")
    if failures:
        raise SystemExit(1)
