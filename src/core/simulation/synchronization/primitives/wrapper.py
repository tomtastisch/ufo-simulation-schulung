#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lock-Wrapper-Utilities für thread-sichere Decorators.

Implementiert die Kern-Funktionalität für Lock-Acquisition und Decorator-Factory.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@contextmanager
def acquire_lock(lock: threading.Lock | threading.RLock | threading.Condition) -> Generator[None, None, None]:
    """
    Context-Manager für thread-sichere Lock-Acquisition.

    Args:
        lock: Lock-Objekt (Lock, RLock oder Condition)

    Yields:
        None - Lock ist während yield aktiv

    Note:
        Lock wird garantiert freigegeben, auch bei Exceptions.
    """
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


def create_lock_wrapper(lock_getter: Callable[..., Any]) -> Callable[[F], F]:
    """
    Factory-Funktion für Lock-basierte Decorators.

    Args:
        lock_getter: Callable das das Lock zurückgibt.
                    Erhält die gleichen Argumente wie die dekorierte Funktion.

    Returns:
        Decorator-Funktion die das Locking implementiert

    Note:
        Diese Funktion ist das Fundament aller @synchronized-Varianten.
        Sie kapselt das acquire/release-Pattern in einem wiederverwendbaren Decorator.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            lock = lock_getter(*args, **kwargs)
            with acquire_lock(lock):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
