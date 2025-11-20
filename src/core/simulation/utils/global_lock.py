#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Lock Utilities für die UFO-Simulation.

Dieses Modul stellt Decorators für Thread-Sicherheit bei Modul-Level-Funktionen
bereit, die mit globalen Locks arbeiten.

Im Gegensatz zu `threads.py` (für Instanzmethoden mit `self._lock`) arbeitet
dieses Modul mit globalen/modulweiten Locks.

Verwendungsbeispiel:
    >>> import threading
    >>> from core.simulation.utils.global_lock import synchronized_global
    >>>
    >>> # Globaler Lock auf Modul-Ebene
    >>> _my_lock = threading.RLock()
    >>>
    >>> @synchronized_global(_my_lock)
    >>> def critical_function():
    ...     # Thread-sichere Funktion
    ...     pass
"""

from __future__ import annotations

import threading
from functools import wraps
from typing import Any, Callable, TypeVar

# Type variable für den synchronized_global Decorator
F = TypeVar("F", bound=Callable[..., Any])


def synchronized_global(lock: threading.Lock | threading.RLock) -> Callable[[F], F]:
    """
    Decorator für threadsichere Funktionsaufrufe mit globalem Lock.

    Dieser Decorator schützt eine Funktion durch automatisches Locking
    über das übergebene Lock-Objekt. Das Lock wird beim Funktionseintritt
    erworben und beim Verlassen (auch bei Exceptions) automatisch freigegeben.

    Im Gegensatz zu `@synchronized` (für Instanzmethoden) erwartet dieser
    Decorator ein explizit übergebenes Lock-Objekt.

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
        >>> @synchronized_global(_config_lock)
        >>> def configure():
        ...     global _configured
        ...     if not _configured:
        ...         # Kritischer Abschnitt
        ...         _configured = True
        >>>
        >>> configure()  # Thread-sicher durch Decorator

    Hinweis:
        Für Instanzmethoden mit `self._lock` verwenden Sie stattdessen
        den `@synchronized` Decorator aus `threads.py`.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Context-Manager sorgt für automatische Lock-Freigabe bei Exceptions
            with lock:
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
