#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thread-Synchronisation-Utilities für die UFO-Simulation."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def synchronized(method: F) -> F:
    """
    Decorator für Instanzmethoden mit automatischem Locking über self._lock.

    Erwartet self._lock-Attribut auf der Klasseninstanz (threading.Lock/RLock).
    Serialisiert Zugriffe, wiedereintrittsfähig bei RLock, exception-sicher.

    Args:
        method: Die zu dekorierende Instanzmethode

    Returns:
        Dekorierte Methode mit automatischem Lock-Management

    Raises:
        AttributeError: Wenn die Instanz kein _lock-Attribut besitzt

    Example:
        >>> import threading
        >>> class Counter:
        ...     def __init__(self):
        ...         self._lock = threading.RLock()
        ...         self._value = 0
        ...     @synchronized
        ...     def increment(self):
        ...         self._value += 1
        ...     @synchronized
        ...     def get_value(self):
        ...         return self._value
    """

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            return method(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]
