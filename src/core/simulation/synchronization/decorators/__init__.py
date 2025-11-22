#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
High-Level Decorators für Thread-Synchronisation.

Dieses Package stellt die öffentlichen Decorators für thread-sichere Methoden
und Funktionen bereit. Die Decorators vereinfachen das Locking-Management
durch automatische Lock-Acquisition und -Release.

Komponenten:
    - synchronized: Decorator für Instanzmethoden (nutzt self._lock)
    - synchronized_module: Decorator-Factory für Modul-Level-Funktionen
    - conditional: Decorator für Methoden mit Condition-Variables

Verwendung:
    Alle Decorators in diesem Package nutzen intern die primitives/ Building-Blocks,
    kapseln jedoch die Komplexität und bieten eine einfache, typsichere API.

    Instanzmethoden:
        Nutze @synchronized für Methoden, die self._lock erwarten.
        Das Lock wird automatisch vor der Methode erworben und nach
        der Ausführung (auch bei Exceptions) freigegeben.

    Modul-Funktionen:
        Nutze @synchronized_module(lock) für globale Funktionen.
        Erfordert ein explizites Lock-Objekt als Parameter.

    Condition-Variables:
        Nutze @conditional für Methoden, die self._condition nutzen.
        Verhindert nested locks bei notify_all()-Aufrufen.

Thread-Safety:
    Alle Decorators sind thread-sicher und exception-sicher. Locks werden
    immer korrekt freigegeben, auch wenn die dekorierte Funktion eine
    Exception wirft.

Beispiel:
    >>> import threading
    >>>
    >>> class ThreadSafeCounter:
    ...     def __init__(self):
    ...         self._lock = threading.RLock()
    ...         self.value = 0
    ...
    ...     @synchronized
    ...     def increment(self):
    ...         self.value += 1
    ...
    ...     @synchronized
    ...     def get_value(self):
    ...         return self.value
"""

from .conditional import conditional
from .instance import synchronized
from .module import synchronized_module

__all__ = [
    "synchronized",
    "synchronized_module",
    "conditional",
]
