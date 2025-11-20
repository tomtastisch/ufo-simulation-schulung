#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decorator für thread-sichere Instanzmethoden."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def synchronized(method: F) -> F:
    """
    Decorator für Instanzmethoden mit automatischem Locking über self._lock.

    Erwartet self._lock-Attribut auf der Klasseninstanz (threading.Lock/RLock).
    Serialisiert Zugriffe, wiedereintrittsfähig bei RLock, exception-sicher.
    """

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            return method(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]
