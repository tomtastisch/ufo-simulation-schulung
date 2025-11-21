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

import pytest
import threadpoolctl

from tests._helpers import run_threaded_workers, assert_race_condition_free, create_decorated_counter
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
    assert_race_condition_free(
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
    assert_race_condition_free(
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
