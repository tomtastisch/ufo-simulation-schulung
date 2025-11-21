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
    Context-Manager für Lock-Acquisition.

    Exception-sicher via try/finally.
    """
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


def create_lock_wrapper(lock_getter: Callable[..., Any]) -> Callable[[F], F]:
    """
    Factory-Funktion für Lock-basierte Decorators.

    lock_getter bestimmt das Lock dynamisch:
    - Instanzmethoden: lambda self, *a, **kw: self._lock
    - Modul-Funktionen: lambda *a, **kw: module_lock
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            lock = lock_getter(*args, **kwargs)
            with _acquire_lock(lock):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator

