#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread-Synchronisations-Modul für die UFO-Simulation.

Modulzweck
----------
Dieses Modul stellt wiederverwendbare Decorators für Thread-Sicherheit bereit,
die keine direkten Abhängigkeiten zu den Simulationsklassen haben. Es kapselt
Thread-Synchronisationslogik in einer generischen, projektübergreifend nutzbaren Form.

Strukturelle Verantwortlichkeiten
----------------------------------
Das Synchronization-Modul folgt diesen Architektur-Prinzipien:

1. **Generische Wiederverwendbarkeit**: Keine Abhängigkeiten zu spezifischen
   Simulationsklassen. Die Decorators können in beliebigen Python-Projekten
   verwendet werden.

2. **Zwei Synchronisationsebenen**:
   - Instanz-Level (synchronized): Für Methoden mit self._lock
   - Modul-Level (synchronized_module): Für Funktionen mit explizitem Lock

3. **Exception-Sicherheit**: Locks werden auch bei Exceptions korrekt freigegeben
   durch Verwendung von context managers (with-Statement).

4. **Typ-Erhaltung**: Decorators erhalten die Original-Signatur der dekorierten
   Funktionen/Methoden für korrekte Type-Checking-Unterstützung.

Modul-Bestandteile
------------------
_lock_wrapper.py:
    Zentrale Lock-Wrapper-Utilities zur Vermeidung von Code-Duplikation.
    Enthält `create_lock_wrapper()` Factory-Funktion die von allen Decorators genutzt wird.
    NICHT Teil der öffentlichen API (private Modul, prefix `_`).

instance_lock.py:
    Decorator `@synchronized` für Instanzmethoden, die automatisch das
    self._lock-Attribut der Klasse verwenden.

module_lock.py:
    Decorator-Factory `@synchronized_module(lock)` für Modul-Level-Funktionen
    mit explizit übergebenem Lock-Objekt.

conditional_lock.py:
    Decorator `@conditional` für Methoden die mit threading.Condition arbeiten.
    Nutzt das Lock der Condition Variable, verhindert nested locks.

lock_wrapper.py:
    Öffentliche API-Exportierung der Lock-Wrapper-Utilities.
    Stellt `acquire_lock` (Context Manager) und `create_lock_wrapper` (Factory)
    für externe Verwendung und Tests bereit.

Öffentliche API
---------------
synchronized:
    Decorator für Instanzmethoden. Erwartet self._lock auf der Klasseninstanz.
    Serialisiert Zugriffe auf die dekorierte Methode pro Instanz.

synchronized_module(lock):
    Decorator-Factory für Modul-Level-Funktionen. Benötigt explizites Lock
    als Parameter. Serialisiert Zugriffe auf die dekorierte Funktion global.

conditional:
    Decorator für Methoden mit Condition-Variable. Erwartet self._condition
    auf der Klasseninstanz. Verhindert nested locks bei notify_all() Calls.

acquire_lock(lock):
    Context Manager für explizite Lock-Acquisition. Unterstützt Lock, RLock
    und Condition. Garantiert exception-sichere Freigabe.

create_lock_wrapper(lock_getter):
    Factory-Funktion für eigene Lock-basierte Decorators. Ermöglicht die
    Erstellung benutzerdefinierter Synchronisations-Patterns.

Verwendungsbeispiele
--------------------
Instanzmethoden (synchronized):
    >>> from core.simulation.synchronization import synchronized
    >>> import threading
    >>>
    >>> class SafeCounter:
    ...     def __init__(self):
    ...         self._lock = threading.RLock()  # Erforderlich!
    ...         self._value = 0
    ...
    ...     @synchronized
    ...     def increment(self):
    ...         self._value += 1
    ...
    ...     @synchronized
    ...     def get_value(self):
    ...         return self._value
    >>>
    >>> counter = SafeCounter()
    >>> counter.increment()  # Thread-sicher

Modul-Level-Funktionen (synchronized_module):
    >>> from core.simulation.synchronization import synchronized_module
    >>> import threading
    >>>
    >>> _global_lock = threading.RLock()
    >>> _shared_state = {"count": 0}
    >>>
    >>> @synchronized_module(_global_lock)
    >>> def increment_global():
    ...     _shared_state["count"] += 1
    >>>
    >>> @synchronized_module(_global_lock)
    >>> def get_global_count():
    ...     return _shared_state["count"]

Explizite Lock-Verwendung (acquire_lock):
    >>> from core.simulation.synchronization import acquire_lock
    >>> import threading
    >>>
    >>> lock = threading.RLock()
    >>> shared_data = []
    >>>
    >>> def safe_append(item):
    ...     with acquire_lock(lock):
    ...         shared_data.append(item)

Eigene Decorators erstellen (create_lock_wrapper):
    >>> from core.simulation.synchronization import create_lock_wrapper
    >>> import threading
    >>>
    >>> _custom_lock = threading.RLock()
    >>>
    >>> def my_synchronized(func):
    ...     return create_lock_wrapper(lambda *args, **kwargs: _custom_lock)(func)
    >>>
    >>> @my_synchronized
    >>> def protected_function():
    ...     # Thread-sicher durch custom decorator
    ...     pass

Kombination mit anderen Modulen:
    >>> from core.simulation.infrastructure import get_logger
    >>> from core.simulation.synchronization import synchronized
    >>> import threading
    >>>
    >>> logger = get_logger(__name__)
    >>>
    >>> class ThreadSafeSimulation:
    ...     def __init__(self):
    ...         self._lock = threading.RLock()
    ...         self._running = False
    ...
    ...     @synchronized
    ...     def start(self):
    ...         if not self._running:
    ...             self._running = True
    ...             logger.info("Simulation gestartet")
    ...
    ...     @synchronized
    ...     def stop(self):
    ...         if self._running:
    ...             self._running = False
    ...             logger.info("Simulation gestoppt")

Thread-Safety-Garantien
------------------------
- Serialisierter Zugriff auf dekorierte Methoden/Funktionen
- Wiedereintrittsfähig bei Verwendung von RLock
- Exception-sicher durch automatische Lock-Freigabe
- Keine Race-Conditions bei korrekter Verwendung

Architektur-Prinzipien
----------------------
- Generisch und wiederverwendbar (keine Simulationslogik)
- Typ-erhaltend (Type Hints bleiben erhalten)
- Exception-sicher (Locks werden immer freigegeben)
- Minimal und fokussiert (nur Synchronisations-Logik)
- Vollständig dokumentiert und getestet
"""

from .instance_lock import synchronized
from .module_lock import synchronized_module
from .conditional_lock import conditional
from .lock_wrapper import acquire_lock, create_lock_wrapper

__all__ = [
    "synchronized",
    "synchronized_module",
    "conditional",
    "acquire_lock",
    "create_lock_wrapper",
]
