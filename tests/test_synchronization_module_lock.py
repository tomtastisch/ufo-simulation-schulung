#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests für core.simulation.synchronization.module_lock.

Diese Tests prüfen:
1. Smoke-Test: Modul kann ohne Fehler importiert werden
2. Funktionalität: @synchronized_module Decorator funktioniert korrekt
3. Thread-Safety: Keine Race-Conditions bei parallelen Zugriffen
4. Kompatibilität: Funktioniert mit Lock und RLock
"""

import threading
import time
from typing import List

import pytest

from core.simulation.synchronization.module_lock import synchronized_module


def test_module_lock_module_import():
    """
    Smoke-Test: Modul kann importiert werden.
    
    Prüft, dass keine Import-, Lazy-Loading- oder Initialisierungsfehler auftreten.
    """
    from core.simulation.synchronization import module_lock
    assert module_lock is not None
    assert hasattr(module_lock, 'synchronized_module')


def test_synchronized_module_decorator_exists():
    """Prüft, dass der synchronized_module Decorator existiert und aufrufbar ist."""
    assert callable(synchronized_module)


def test_synchronized_module_basic_functionality():
    """
    Prüft Basisfunktionalität des @synchronized_module Decorators.
    
    Testet:
    - Decorator kann auf Funktion angewendet werden
    - Dekorierte Funktion funktioniert korrekt
    - Rückgabewerte bleiben erhalten
    - Parameter werden korrekt durchgereicht
    """
    
    lock = threading.RLock()
    counter = {"value": 0}
    
    @synchronized_module(lock)
    def increment():
        counter["value"] += 1
    
    @synchronized_module(lock)
    def get_value():
        return counter["value"]
    
    @synchronized_module(lock)
    def add(amount: int):
        counter["value"] += amount
        return counter["value"]
    
    assert get_value() == 0
    
    increment()
    assert get_value() == 1
    
    result = add(5)
    assert result == 6
    assert get_value() == 6


def test_synchronized_module_with_lock():
    """
    Prüft, dass @synchronized_module mit threading.Lock funktioniert.
    """
    
    lock = threading.Lock()
    counter = {"value": 0}
    
    @synchronized_module(lock)
    def increment():
        counter["value"] += 1
    
    @synchronized_module(lock)
    def get_value():
        return counter["value"]
    
    increment()
    assert get_value() == 1


@pytest.mark.threading
@pytest.mark.timeout(30)
def test_synchronized_module_thread_safety_no_race_conditions():
    """
    Multithread-Test: Prüft, dass keine Race-Conditions bei parallelen Zugriffen auftreten.
    
    Testet:
    - 100 Threads führen jeweils 100 Inkremente durch
    - Erwartetes Ergebnis: 10.000 (keine Race-Conditions)
    - Ohne @synchronized_module würde das Ergebnis typischerweise < 10.000 sein
    """
    
    lock = threading.RLock()
    counter = {"value": 0}
    
    @synchronized_module(lock)
    def increment():
        # Simuliere kritischen Abschnitt mit Read-Modify-Write
        old_value = counter["value"]
        time.sleep(0.0001)  # Kurze Verzögerung um Race-Conditions zu provozieren
        counter["value"] = old_value + 1
    
    @synchronized_module(lock)
    def get_value():
        return counter["value"]
    
    threads: List[threading.Thread] = []
    
    num_threads = 100
    increments_per_thread = 100
    expected_result = num_threads * increments_per_thread
    
    # Starte Threads
    for _ in range(num_threads):
        def worker():
            for _ in range(increments_per_thread):
                increment()
        
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
    
    # Warte auf Abschluss
    for thread in threads:
        thread.join()
    
    # Prüfe Ergebnis
    assert get_value() == expected_result, \
        f"Race-Condition detected: Expected {expected_result}, got {get_value()}"


@pytest.mark.threading
@pytest.mark.timeout(10)
def test_synchronized_module_reentrant_with_rlock():
    """
    Prüft Wiedereintrittsfähigkeit bei RLock.
    
    Testet, dass derselbe Thread die Funktion mehrfach betreten kann
    (wichtig für verschachtelte Aufrufe).
    """
    
    lock = threading.RLock()
    counter = {"value": 0}
    
    @synchronized_module(lock)
    def increment():
        counter["value"] += 1
    
    @synchronized_module(lock)
    def increment_twice():
        # Ruft eine andere synchronisierte Funktion auf
        increment()
        increment()
    
    @synchronized_module(lock)
    def get_value():
        return counter["value"]
    
    increment_twice()  # Sollte nicht deadlocken
    assert get_value() == 2


def test_synchronized_module_preserves_exceptions():
    """
    Prüft, dass Exceptions aus dekorierten Funktionen korrekt durchgereicht werden
    und das Lock trotzdem freigegeben wird.
    """
    
    lock = threading.RLock()
    
    @synchronized_module(lock)
    def throw_error():
        raise ValueError("Test exception")
    
    @synchronized_module(lock)
    def check_lock_free():
        # Wenn Lock nicht freigegeben wurde, würde dies blockieren
        return True
    
    # Exception sollte durchgereicht werden
    with pytest.raises(ValueError, match="Test exception"):
        throw_error()
    
    # Lock sollte trotzdem freigegeben worden sein
    assert check_lock_free() is True


def test_synchronized_module_preserves_function_signature():
    """
    Prüft, dass der Decorator die Funktionssignatur erhält.
    
    Dies ist wichtig für Introspection, Dokumentation und IDE-Support.
    """
    
    lock = threading.RLock()
    
    @synchronized_module(lock)
    def documented_function(x: int, y: str) -> str:
        """Eine gut dokumentierte Funktion."""
        return f"{y}: {x}"
    
    # Prüfe, dass __name__ und __doc__ erhalten bleiben (via @wraps)
    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "Eine gut dokumentierte Funktion."
    
    # Prüfe Funktionalität
    result = documented_function(42, "Answer")
    assert result == "Answer: 42"


def test_synchronized_module_with_kwargs():
    """
    Prüft, dass @synchronized_module mit Keyword-Argumenten funktioniert.
    """
    
    lock = threading.RLock()
    
    @synchronized_module(lock)
    def flexible_function(a: int, b: int = 10, c: int = 20) -> int:
        return a + b + c
    
    assert flexible_function(1) == 31
    assert flexible_function(1, b=5) == 26
    assert flexible_function(1, c=100) == 111
    assert flexible_function(1, b=2, c=3) == 6


@pytest.mark.threading
@pytest.mark.timeout(15)
def test_synchronized_module_multiple_locks():
    """
    Prüft, dass verschiedene Locks unabhängig voneinander funktionieren.
    """
    
    lock1 = threading.RLock()
    lock2 = threading.RLock()
    
    counter1 = {"value": 0}
    counter2 = {"value": 0}
    
    @synchronized_module(lock1)
    def increment1():
        old = counter1["value"]
        time.sleep(0.001)
        counter1["value"] = old + 1
    
    @synchronized_module(lock2)
    def increment2():
        old = counter2["value"]
        time.sleep(0.001)
        counter2["value"] = old + 1
    
    @synchronized_module(lock1)
    def get_value1():
        return counter1["value"]
    
    @synchronized_module(lock2)
    def get_value2():
        return counter2["value"]
    
    # Parallele Zugriffe auf unterschiedliche Locks
    threads = []
    
    for _ in range(10):
        t1 = threading.Thread(target=increment1)
        t2 = threading.Thread(target=increment2)
        threads.extend([t1, t2])
        t1.start()
        t2.start()
    
    for thread in threads:
        thread.join()
    
    # Beide Counter sollten korrekt sein (unabhängig voneinander)
    assert get_value1() == 10
    assert get_value2() == 10


def test_synchronized_module_with_args_and_kwargs():
    """
    Prüft komplexe Parameterkombinationen.
    """
    
    lock = threading.RLock()
    
    @synchronized_module(lock)
    def complex_function(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}
    
    result = complex_function(1, 2, 3, a=4, b=5)
    assert result == {"args": (1, 2, 3), "kwargs": {"a": 4, "b": 5}}
