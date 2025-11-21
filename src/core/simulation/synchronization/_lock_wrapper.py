#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zentrale Lock-Wrapper-Utilities für thread-sichere Decorators."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@contextmanager
def _acquire_lock(lock: threading.Lock | threading.RLock | threading.Condition) -> Generator[None, None, None]:
    """
    Zentrale Context-Manager-Funktion für Lock-Acquisition.

    Unterstützt alle Lock-Typen (Lock, RLock, Condition) und garantiert
    exception-sichere Freigabe via try/finally.

    Args:
        lock: Lock-Objekt (Lock, RLock oder Condition)

    Yields:
        None (Context Manager)

    Example:
        >>> lock = threading.RLock()
        >>> with _acquire_lock(lock):
        ...     # Kritischer Abschnitt
        ...     pass
    """
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


def create_lock_wrapper(lock_getter: Callable[..., Any]) -> Callable[[F], F]:
    """
    Factory-Funktion für Lock-basierte Decorators.

    Erstellt einen Decorator der eine Funktion/Methode unter einem Lock ausführt.
    Das Lock wird dynamisch über die `lock_getter`-Funktion bestimmt.

    Args:
        lock_getter: Funktion die das Lock-Objekt zurückgibt.
                    Signatur: (*args, **kwargs) -> Lock
                    Für Instanzmethoden: lambda self, *args, **kwargs: self._lock
                    Für Modul-Funktionen: lambda *args, **kwargs: module_lock

    Returns:
        Decorator-Funktion die Methoden/Funktionen wrapped

    Design:
        - Generisch: Funktioniert mit Lock, RLock und Condition
        - Exception-sicher: Lock wird immer freigegeben
        - Typ-erhaltend: @wraps preserviert Original-Signatur
        - DRY: Zentrale Implementierung für alle Lock-Decorators

    Example:
        >>> # Für Instanzmethoden
        >>> def synchronized(method):
        ...     return create_lock_wrapper(lambda self, *args, **kwargs: self._lock)(method)
        >>>
        >>> # Für Modul-Funktionen
        >>> _module_lock = threading.RLock()
        >>> def synchronized_module(func):
        ...     return create_lock_wrapper(lambda *args, **kwargs: _module_lock)(func)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Lock dynamisch bestimmen
            lock = lock_getter(*args, **kwargs)

            # Unter Lock ausführen
            with _acquire_lock(lock):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator

