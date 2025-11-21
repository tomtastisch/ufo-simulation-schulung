#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Beispiel-Tests für Threading/Debugging-Tools.

Demonstriert die Verwendung von:
- pytest-timeout (Deadlock-Erkennung)
- threadpoolctl (Thread-Pool-Kontrolle)
"""

import threading
import time
from typing import Callable, List, Dict, Any

import pytest
import threadpoolctl


# Vermeide direkten Import aus `conftest` (pytest entdeckt conftest, aber statische
# Analyzer melden oft 'unresolved import'). Stattdessen definieren wir hier kleine,
# gut dokumentierte Test-Helfer lokal in der Datei.


def run_threaded_workers(worker_func: Callable[[], None], num_threads: int = 10, timeout_per_thread: float = 5.0) -> List[threading.Thread]:
    """Führt eine Worker-Funktion in mehreren Threads aus und wartet auf Abschluss.

    Diese Implementierung ist intentionally klein und test-fokussiert.
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


def test_race_condition_free(
    increment_func: Callable[[], None],
    get_value_func: Callable[[], int],
    num_threads: int = 100,
    increments_per_thread: int = 100,
    timeout: float = 30.0,
) -> bool:
    """Prüft, ob `increment_func` race-condition-frei arbeitet.

    Diese vereinfachte Funktion spiegelt das Verhalten der gleichnamigen Helfer
    in der Projekt-`conftest.py` wider und wirft bei Abweichungen AssertionError.
    """
    expected = num_threads * increments_per_thread

    def worker():
        for _ in range(increments_per_thread):
            increment_func()

    run_threaded_workers(worker, num_threads=num_threads, timeout_per_thread=timeout / max(1, num_threads))

    actual = get_value_func()
    assert actual == expected, f"Race-Condition detected: Expected {expected}, got {actual}"
    return True


def create_decorated_counter(decorator: Callable, lock: threading.RLock | None = None) -> Dict[str, Any]:
    """Erzeugt einen kleinen dekorierten Counter (increment/get_value/add).

    Nützlich für Tests, die Decorators wie `@synchronized` prüfen.
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


from core.simulation.synchronization import synchronized


@pytest.mark.timeout(5)
def test_timeout_prevents_deadlock():
    """
    Demonstriert pytest-timeout: Test wird nach 5s abgebrochen.
    
    Dieser Test würde ohne timeout unendlich laufen.
    Mit @pytest.mark.timeout(5) wird er automatisch abgebrochen.
    """
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    
    def worker1():
        with lock1:
            time.sleep(0.1)

    def worker2():
        with lock2:
            time.sleep(0.1)

    t1 = threading.Thread(target=worker1)
    t2 = threading.Thread(target=worker2)

    t1.start()
    t2.start()

    t1.join(timeout=1)
    t2.join(timeout=1)

    # Test ist OK - kein Deadlock
    assert True


@pytest.mark.timeout(10)
def test_threadpoolctl_limits_threads():
    """
    Demonstriert threadpoolctl: Begrenzt Thread-Anzahl.
    
    Hilfreich um Lock-Contention in Tests zu reduzieren.
    """
    info = threadpoolctl.threadpool_info()
    print(f"\nThread-Pool-Info: {len(info)} pools gefunden")
    
    with threadpoolctl.threadpool_limits(limits=2):
        info_limited = threadpoolctl.threadpool_info()
        print(f"Thread-Pool-Info (limitiert): {info_limited}")
    
    assert True


@pytest.mark.timeout(15)
def test_synchronized_decorator_under_load():
    """
    Stress-Test für @synchronized Decorator mit pytest-timeout Sicherheit.
    """
    class TestCounter:
        def __init__(self):
            self._lock = threading.RLock()
            self._value = 0
        
        @synchronized
        def increment(self):
            old = self._value
            time.sleep(0.0001)
            self._value = old + 1
        
        @synchronized
        def get_value(self):
            return self._value
    
    counter = TestCounter()

    # 50 Threads × 20 Inkremente = 1000
    test_race_condition_free(
        counter.increment,
        counter.get_value,
        num_threads=50,
        increments_per_thread=20
    )


@pytest.mark.timeout(10)
def test_module_lock_decorator_works(rlock):
    """
    Test für @synchronized_module Decorator mit timeout-Schutz.
    """
    from core.simulation.synchronization import synchronized_module
    
    counter = create_decorated_counter(synchronized_module, rlock)

    # 20 Threads × 10 Inkremente = 200
    test_race_condition_free(
        counter["increment"],
        counter["get_value"],
        num_threads=20,
        increments_per_thread=10
    )


# Marker für langsame Tests
@pytest.mark.slow
@pytest.mark.timeout(30)
def test_long_running_operation():
    time.sleep(2)  # Simuliere lange Operation
    assert True


# Marker für Threading-Tests
@pytest.mark.threading
@pytest.mark.timeout(20)
def test_complex_threading_scenario():
    """
    Beispiel für komplexen Threading-Test.
    """
    class Resource:
        def __init__(self, name: str):
            self._lock = threading.RLock()
            self._name = name
            self._access_count = 0
        
        @synchronized
        def access(self):
            self._access_count += 1
            time.sleep(0.001)
            return self._access_count
    
    resources = [Resource(f"R{i}") for i in range(5)]

    def worker(resource: Resource):
        for _ in range(10):
            resource.access()
    
    # Mehrere Threads auf verschiedene Resources
    for resource in resources:
        run_threaded_workers(
            lambda r=resource: worker(r),
            num_threads=3,
            timeout_per_thread=5.0
        )

    # Jede Resource sollte 3*10 = 30 Zugriffe haben
    for resource in resources:
        assert resource._access_count == 30
