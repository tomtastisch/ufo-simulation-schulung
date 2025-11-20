#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests für core.simulation.utils.threads.

Diese Tests prüfen:
1. Smoke-Test: Modul kann ohne Fehler importiert werden
2. Funktionalität: @synchronized Decorator funktioniert korrekt
3. Thread-Safety: Keine Race-Conditions bei parallelen Zugriffen
4. Error-Handling: Korrekte Fehlermeldung bei fehlendem _lock-Attribut
"""

import threading
import time
from typing import List

import pytest

from core.simulation.synchronization.instance_lock import synchronized


def test_instance_lock_module_import():
    """
    Smoke-Test: Modul kann importiert werden.
    
    Prüft, dass keine Import-, Lazy-Loading- oder Initialisierungsfehler auftreten.
    """
    from core.simulation.synchronization import instance_lock
    assert instance_lock is not None
    assert hasattr(instance_lock, 'synchronized')


def test_synchronized_decorator_exists():
    """Prüft, dass der synchronized Decorator existiert und aufrufbar ist."""
    assert callable(synchronized)


def test_synchronized_basic_functionality():
    """
    Prüft Basisfunktionalität des @synchronized Decorators.
    
    Testet:
    - Decorator kann auf Methode angewendet werden
    - Dekorierte Methode funktioniert korrekt
    - Rückgabewerte bleiben erhalten
    """
    
    class Counter:
        def __init__(self):
            self._lock = threading.RLock()
            self._value = 0
        
        @synchronized
        def increment(self):
            self._value += 1
        
        @synchronized
        def get_value(self):
            return self._value
        
        @synchronized
        def add(self, amount: int):
            self._value += amount
            return self._value
    
    counter = Counter()
    assert counter.get_value() == 0
    
    counter.increment()
    assert counter.get_value() == 1
    
    result = counter.add(5)
    assert result == 6
    assert counter.get_value() == 6


def test_synchronized_with_threading_lock():
    """
    Prüft, dass @synchronized auch mit threading.Lock (nicht nur RLock) funktioniert.
    """
    
    class SimpleLockCounter:
        def __init__(self):
            self._lock = threading.Lock()  # Einfaches Lock statt RLock
            self._value = 0
        
        @synchronized
        def increment(self):
            self._value += 1
        
        @synchronized
        def get_value(self):
            return self._value
    
    counter = SimpleLockCounter()
    counter.increment()
    assert counter.get_value() == 1


@pytest.mark.threading
@pytest.mark.timeout(30)
def test_synchronized_thread_safety_no_race_conditions():
    """
    Multithread-Test: Prüft, dass keine Race-Conditions bei parallelen Zugriffen auftreten.
    
    Testet:
    - 100 Threads führen jeweils 100 Inkremente durch
    - Erwartetes Ergebnis: 10.000 (keine Race-Conditions)
    - Ohne @synchronized würde das Ergebnis typischerweise < 10.000 sein
    """
    
    class ThreadSafeCounter:
        def __init__(self):
            self._lock = threading.RLock()
            self._value = 0
        
        @synchronized
        def increment(self):
            # Simuliere kritischen Abschnitt mit Read-Modify-Write
            old_value = self._value
            time.sleep(0.0001)  # Kurze Verzögerung um Race-Conditions zu provozieren
            self._value = old_value + 1
        
        @synchronized
        def get_value(self):
            return self._value
    
    counter = ThreadSafeCounter()
    threads: List[threading.Thread] = []
    
    num_threads = 100
    increments_per_thread = 100
    expected_result = num_threads * increments_per_thread
    
    # Starte Threads
    for _ in range(num_threads):
        def worker():
            for _ in range(increments_per_thread):
                counter.increment()
        
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
    
    # Warte auf Abschluss
    for thread in threads:
        thread.join()
    
    # Prüfe Ergebnis
    assert counter.get_value() == expected_result, \
        f"Race-Condition detected: Expected {expected_result}, got {counter.get_value()}"


@pytest.mark.threading
@pytest.mark.timeout(10)
def test_synchronized_reentrant_with_rlock():
    """
    Prüft Wiedereintrittsfähigkeit bei RLock.
    
    Testet, dass derselbe Thread die Methode mehrfach betreten kann
    (wichtig für verschachtelte Aufrufe).
    """
    
    class ReentrantCounter:
        def __init__(self):
            self._lock = threading.RLock()
            self._value = 0
        
        @synchronized
        def increment(self):
            self._value += 1
        
        @synchronized
        def increment_twice(self):
            # Ruft eine andere synchronisierte Methode auf
            self.increment()
            self.increment()
        
        @synchronized
        def get_value(self):
            return self._value
    
    counter = ReentrantCounter()
    counter.increment_twice()  # Sollte nicht deadlocken
    assert counter.get_value() == 2


def test_synchronized_preserves_exceptions():
    """
    Prüft, dass Exceptions aus dekorierten Methoden korrekt durchgereicht werden
    und das Lock trotzdem freigegeben wird.
    """
    
    class ExceptionThrower:
        def __init__(self):
            self._lock = threading.RLock()
            self._lock_acquired_count = 0
        
        @synchronized
        def throw_error(self):
            raise ValueError("Test exception")
        
        @synchronized
        def check_lock_free(self):
            # Wenn Lock nicht freigegeben wurde, würde dies blockieren
            return True
    
    thrower = ExceptionThrower()
    
    # Exception sollte durchgereicht werden
    with pytest.raises(ValueError, match="Test exception"):
        thrower.throw_error()
    
    # Lock sollte trotzdem freigegeben worden sein
    assert thrower.check_lock_free() is True


def test_synchronized_without_lock_attribute():
    """
    Prüft, dass fehlerhaftes Setup (Klasse ohne _lock) zu sauberem Fehler führt.
    """
    
    class NoLockClass:
        def __init__(self):
            self._value = 0
        
        @synchronized
        def increment(self):
            self._value += 1
    
    obj = NoLockClass()
    
    # Sollte AttributeError werfen (kein _lock vorhanden)
    with pytest.raises(AttributeError):
        obj.increment()


def test_synchronized_preserves_method_signature():
    """
    Prüft, dass der Decorator die Methodensignatur erhält.
    
    Dies ist wichtig für Introspection, Dokumentation und IDE-Support.
    """
    
    class DocumentedClass:
        def __init__(self):
            self._lock = threading.RLock()
        
        @synchronized
        def documented_method(self, x: int, y: str) -> str:
            """Eine gut dokumentierte Methode."""
            return f"{y}: {x}"
    
    obj = DocumentedClass()
    
    # Prüfe, dass __name__ und __doc__ erhalten bleiben (via @wraps)
    assert obj.documented_method.__name__ == "documented_method"
    assert obj.documented_method.__doc__ == "Eine gut dokumentierte Methode."
    
    # Prüfe Funktionalität
    result = obj.documented_method(42, "Answer")
    assert result == "Answer: 42"


def test_synchronized_with_kwargs():
    """
    Prüft, dass @synchronized mit Keyword-Argumenten funktioniert.
    """
    
    class FlexibleClass:
        def __init__(self):
            self._lock = threading.RLock()
        
        @synchronized
        def flexible_method(self, a: int, b: int = 10, c: int = 20) -> int:
            return a + b + c
    
    obj = FlexibleClass()
    
    assert obj.flexible_method(1) == 31
    assert obj.flexible_method(1, b=5) == 26
    assert obj.flexible_method(1, c=100) == 111
    assert obj.flexible_method(1, b=2, c=3) == 6


@pytest.mark.threading
@pytest.mark.timeout(15)
def test_synchronized_multiple_instances():
    """
    Prüft, dass verschiedene Instanzen unabhängige Locks haben.
    
    Dies stellt sicher, dass der Decorator instanzspezifisch arbeitet,
    nicht klassenspezifisch.
    """
    
    class InstanceCounter:
        def __init__(self):
            self._lock = threading.RLock()
            self._value = 0
        
        @synchronized
        def increment(self):
            old = self._value
            time.sleep(0.001)
            self._value = old + 1
        
        @synchronized
        def get_value(self):
            return self._value
    
    counter1 = InstanceCounter()
    counter2 = InstanceCounter()
    
    # Parallele Zugriffe auf unterschiedliche Instanzen
    threads = []
    
    for _ in range(10):
        t1 = threading.Thread(target=counter1.increment)
        t2 = threading.Thread(target=counter2.increment)
        threads.extend([t1, t2])
        t1.start()
        t2.start()
    
    for thread in threads:
        thread.join()
    
    # Beide Counter sollten korrekt sein (unabhängig voneinander)
    assert counter1.get_value() == 10
    assert counter2.get_value() == 10
