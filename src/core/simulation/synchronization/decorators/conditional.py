#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decorator für thread-sichere Methoden mit Condition-Variable-Unterstützung.

Implementiert @conditional für Methoden, die self._condition nutzen.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from ..primitives.wrapper import create_lock_wrapper

F = TypeVar("F", bound=Callable[..., Any])


def conditional(method: F) -> F:
    """
    Decorator für Methoden die mit threading.Condition arbeiten.

    Erwartet self._condition (threading.Condition) auf der Klasseninstanz.
    Nutzt das interne Lock der Condition - verhindert nested locks bei notify_all().

    Unterschied zu @synchronized:
        - @synchronized: Nutzt self._lock direkt
        - @conditional: Nutzt self._condition (deren internes Lock)

    Args:
        method: Zu dekorierende Methode

    Returns:
        Thread-sichere Version der Methode

    Raises:
        AttributeError: Falls self._condition nicht existiert
    """
    return create_lock_wrapper(lambda self, *args, **kwargs: self._condition)(method)
