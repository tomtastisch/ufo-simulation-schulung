#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decorator für thread-sichere Methoden mit Condition-Variable-Unterstützung."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from ._lock_wrapper import create_lock_wrapper

F = TypeVar("F", bound=Callable[..., Any])


def conditional(method: F) -> F:
    """
    Decorator für Methoden die mit threading.Condition arbeiten.

    Erwartet self._condition (threading.Condition) auf der Klasseninstanz.
    Nutzt das Lock der Condition Variable - verhindert nested locks bei notify_all().

    Unterschied zu @synchronized:
        - @synchronized: Nutzt self._lock direkt
        - @conditional: Nutzt self._condition (und deren internes Lock)

    Nutzt zentrale create_lock_wrapper() Implementation.

    Example:
        >>> import threading
        >>> class MyManager:
        ...     def __init__(self):
        ...         self._lock = threading.RLock()
        ...         self._condition = threading.Condition(self._lock)
        ...         self._state = 0
        ...
        ...     @conditional
        ...     def update(self, value: int) -> None:
        ...         self._state = value
        ...         self._condition.notify_all()  # Kein nested lock!
    """
    return create_lock_wrapper(lambda self, *args, **kwargs: self._condition)(method)

