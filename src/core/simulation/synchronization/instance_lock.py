#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decorator für thread-sichere Instanzmethoden."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from ._lock_wrapper import create_lock_wrapper

F = TypeVar("F", bound=Callable[..., Any])


def synchronized(method: F) -> F:
    """
    Decorator für Instanzmethoden mit automatischem Locking über self._lock.

    Erwartet self._lock-Attribut auf der Klasseninstanz (threading.Lock/RLock).
    Nutzt zentrale create_lock_wrapper() Implementation.

    Example:
        >>> import threading
        >>> class Counter:
        ...     def __init__(self):
        ...         self._lock = threading.RLock()
        ...         self.value = 0
        ...
        ...     @synchronized
        ...     def increment(self):
        ...         self.value += 1
    """
    return create_lock_wrapper(lambda self, *args, **kwargs: self._lock)(method)
