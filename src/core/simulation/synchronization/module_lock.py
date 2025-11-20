#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module-Lock Decorator für die UFO-Simulation.

Dieses Modul stellt einen Decorator für Thread-Sicherheit bei Modul-Level-Funktionen bereit.
Der Decorator erwartet ein explizit übergebenes Lock-Objekt als Parameter.

Im Gegensatz zu `instance_lock` (für Instanzmethoden mit `self._lock`) arbeitet
dieses Modul mit expliziten, oft modul-globalen Locks.

Verwendungsbeispiel:
    >>> import threading
    >>> from core.simulation.synchronization.module_lock import synchronized_module
    >>>
    >>> # Modul-globaler Lock
    >>> _my_lock = threading.RLock()
    >>>
    >>> @synchronized_module(_my_lock)
    >>> def critical_function():
    ...     # Thread-sichere Funktion
    ...     pass
"""

from __future__ import annotations

import threading
from functools import wraps
from typing import Any, Callable, TypeVar

# Type variable für den synchronized_module Decorator
F = TypeVar("F", bound=Callable[..., Any])


def synchronized_module(lock: threading.Lock | threading.RLock) -> Callable[[F], F]:
    """
    Decorator für threadsichere Modul-Level-Funktionen mit explizitem Lock.

    Dieser Decorator schützt eine Modul-Level-Funktion durch automatisches Locking
    über das übergebene Lock-Objekt. Das Lock wird beim Funktionseintritt
    erworben und beim Verlassen (auch bei Exceptions) automatisch freigegeben.

    Im Gegensatz zu `@synchronized` (für Instanzmethoden mit `self._lock`) erwartet
    dieser Decorator ein explizit übergebenes Lock-Objekt als Parameter.

    Args:
        lock: Das zu verwendende Lock-Objekt (threading.Lock oder threading.RLock)

    Returns:
        Decorator-Funktion, die die ursprüngliche Funktion mit Lock-Schutz umschließt

    Raises:
        TypeError: Wenn `lock` kein gültiges Lock-Objekt ist

    Thread-Safety-Garantien:
        - Serialisierter Zugriff: Nur ein Thread kann die Funktion gleichzeitig ausführen
        - Wiedereintrittsfähig: Bei Verwendung von RLock kann derselbe Thread
          die Funktion mehrfach betreten (Reentrant Lock)
        - Exception-sicher: Lock wird auch bei Exceptions korrekt freigegeben

    Beispiel:
        >>> import threading
        >>>
        >>> # Modul-Level Lock
        >>> _config_lock = threading.RLock()
        >>> _configured = False
        >>>
        >>> @synchronized_module(_config_lock)
        >>> def configure():
        ...     global _configured
        ...     if not _configured:
        ...         # Kritischer Abschnitt
        ...         _configured = True
        >>>
        >>> configure()  # Thread-sicher durch Decorator

    Siehe auch:
        - `synchronized`: Für Instanzmethoden mit `self._lock`
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Context-Manager sorgt für automatische Lock-Freigabe bei Exceptions
            with lock:
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
