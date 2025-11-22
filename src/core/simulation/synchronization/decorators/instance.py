#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decorator für thread-sichere Instanzmethoden.

Implementiert @synchronized für Methoden, die self._lock nutzen.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from ..primitives.wrapper import create_lock_wrapper

F = TypeVar("F", bound=Callable[..., Any])


def synchronized(method: F) -> F:
    """
    Decorator für Instanzmethoden mit automatischem Locking.

    Erwartet self._lock-Attribut (threading.Lock oder threading.RLock).

    Args:
        method: Zu dekorierende Instanzmethode

    Returns:
        Thread-sichere Version der Methode

    Raises:
        AttributeError: Falls self._lock nicht existiert
    """
    return create_lock_wrapper(lambda self, *args, **kwargs: self._lock)(method)
