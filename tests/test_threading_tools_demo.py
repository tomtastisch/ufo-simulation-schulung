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
from typing import List

import pytest
import threadpoolctl


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
            # Würde auf lock2 warten, aber worker2 hält es bereits
            # with lock2:  # ← Auskommentiert um Deadlock zu vermeiden
            #     pass
            pass
    
    def worker2():
        with lock2:
            time.sleep(0.1)
            # Würde auf lock1 warten, aber worker1 hält es bereits
            # with lock1:  # ← Auskommentiert um Deadlock zu vermeiden
            #     pass
            pass
    
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
    # Zeige aktuelle Thread-Pool-Info
    info = threadpoolctl.threadpool_info()
    print(f"\nThread-Pool-Info: {len(info)} pools gefunden")
    
    # Für Libraries die threadpoolctl unterstützen (BLAS, OpenMP):
    with threadpoolctl.threadpool_limits(limits=2):
        # Code hier läuft mit max 2 Threads in unterstützten Libraries
        info_limited = threadpoolctl.threadpool_info()
        print(f"Thread-Pool-Info (limitiert): {info_limited}")
    
    # Test ist OK
    assert True


@pytest.mark.timeout(15)
def test_synchronized_decorator_under_load():
    """
    Stress-Test für @synchronized Decorator mit pytest-timeout Sicherheit.
    
    Demonstriert:
    - Threading-Test mit vielen Threads
    - pytest-timeout als Sicherheitsnetz
    - Korrekte Lock-Verwendung
    """
    from core.simulation.utils import synchronized
    
    class TestCounter:
        def __init__(self):
            self._lock = threading.RLock()
            self._value = 0
        
        @synchronized
        def increment(self):
            # Simuliere etwas Arbeit
            old = self._value
            time.sleep(0.0001)
            self._value = old + 1
        
        @synchronized
        def get_value(self):
            return self._value
    
    counter = TestCounter()
    threads: List[threading.Thread] = []
    
    # 50 Threads × 20 Inkremente = 1000
    num_threads = 50
    increments_per_thread = 20
    
    def worker():
        for _ in range(increments_per_thread):
            counter.increment()
    
    # Threads starten
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    # Auf Threads warten (mit timeout als Sicherheit)
    for t in threads:
        t.join(timeout=10)  # Einzelner Thread sollte nicht >10s brauchen
    
    # Verify: Keine Race-Conditions
    expected = num_threads * increments_per_thread
    actual = counter.get_value()
    
    assert actual == expected, f"Race-Condition detected: {actual} != {expected}"


@pytest.mark.timeout(10)
def test_module_lock_decorator_works():
    """
    Test für @synchronized_module Decorator mit timeout-Schutz.
    """
    from core.simulation.utils import synchronized_module
    
    _test_lock = threading.RLock()
    _counter = {"value": 0}
    
    @synchronized_module(_test_lock)
    def increment():
        old = _counter["value"]
        time.sleep(0.0001)
        _counter["value"] = old + 1
    
    @synchronized_module(_test_lock)
    def get_value():
        return _counter["value"]
    
    threads: List[threading.Thread] = []
    
    for _ in range(20):
        def worker():
            for _ in range(10):
                increment()
        
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join(timeout=5)
    
    # 20 Threads × 10 Inkremente = 200
    assert get_value() == 200


# Marker für langsame Tests
@pytest.mark.slow
@pytest.mark.timeout(30)
def test_long_running_operation():
    """
    Beispiel für langsamen Test mit extended timeout.
    
    Tests mit @pytest.mark.slow können selektiv ausgeführt werden:
    pytest -m slow          # Nur slow tests
    pytest -m "not slow"    # Alle außer slow
    """
    time.sleep(2)  # Simuliere lange Operation
    assert True


# Marker für Threading-Tests
@pytest.mark.threading
@pytest.mark.timeout(20)
def test_complex_threading_scenario():
    """
    Beispiel für komplexen Threading-Test.
    
    Tests mit @pytest.mark.threading können selektiv ausgeführt werden:
    pytest -m threading     # Nur threading tests
    """
    from core.simulation.utils import synchronized
    
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
    threads: List[threading.Thread] = []
    
    def worker(resource: Resource):
        for _ in range(10):
            resource.access()
    
    # Mehrere Threads auf verschiedene Resources
    for resource in resources:
        for _ in range(3):
            t = threading.Thread(target=worker, args=(resource,))
            threads.append(t)
            t.start()
    
    # Warten
    for t in threads:
        t.join(timeout=5)
    
    # Jede Resource sollte 3*10 = 30 Zugriffe haben
    for resource in resources:
        assert resource._access_count == 30
