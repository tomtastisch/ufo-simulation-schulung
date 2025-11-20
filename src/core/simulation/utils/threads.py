#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threading-Utilities für die UFO-Simulation.

Dieses Modul stellt generische, wiederverwendbare Decorators und Hilfsfunktionen
für Thread-Sicherheit bereit, ohne Annahmen über konkrete Simulationsklassen zu treffen.

Voraussetzung:
- Dekorierte Methoden müssen Teil einer Klasse sein, die ein `self._lock`-Attribut besitzt
  (typischerweise `threading.RLock()` oder `threading.Lock()`).

Verwendungsbeispiel:
    >>> import threading
    >>> from core.simulation.utils.threads import synchronized
    >>>
    >>> class SafeCounter:
    ...     def __init__(self):
    ...         self._lock = threading.RLock()
    ...         self._value = 0
    ...
    ...     @synchronized
    ...     def increment(self):
    ...         self._value += 1
    ...
    ...     @synchronized
    ...     def get_value(self):
    ...         return self._value
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

# Type variable für den synchronized Decorator
# Gebunden an Callable, damit Typchecker die Signatur der dekorierten Methode beibehalten
F = TypeVar("F", bound=Callable[..., Any])


def synchronized(method: F) -> F:
    """
    Decorator für threadsichere Methodenaufrufe.

    Dieser Decorator schützt eine Methode durch automatisches Locking
    über das `self._lock`-Attribut der Instanz. Das Lock wird beim
    Methodeneintritt erworben und beim Verlassen (auch bei Exceptions)
    automatisch freigegeben.

    Voraussetzungen:
        - Die Methode muss Teil einer Klasse sein (erwartet `self` als ersten Parameter)
        - Die Klasse muss ein `self._lock`-Attribut besitzen (z.B. `threading.RLock()`)

    Args:
        method: Die zu schützende Methode

    Returns:
        Die dekorierte Methode mit identischer Signatur

    Raises:
        AttributeError: Wenn die Instanz kein `_lock`-Attribut besitzt

    Thread-Safety-Garantien:
        - Serialisierter Zugriff: Nur ein Thread kann die Methode gleichzeitig ausführen
        - Wiedereintrittsfähig: Bei Verwendung von RLock kann derselbe Thread
          die Methode mehrfach betreten (Reentrant Lock)
        - Exception-sicher: Lock wird auch bei Exceptions korrekt freigegeben

    Beispiel:
        >>> import threading
        >>> class Counter:
        ...     def __init__(self):
        ...         self._lock = threading.RLock()
        ...         self._count = 0
        ...
        ...     @synchronized
        ...     def increment(self):
        ...         self._count += 1
        ...
        ...     @synchronized
        ...     def get_count(self):
        ...         return self._count
        >>>
        >>> counter = Counter()
        >>> counter.increment()
        >>> assert counter.get_count() == 1
    """

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        # Context-Manager sorgt für automatische Lock-Freigabe bei Exceptions
        with self._lock:
            return method(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]
