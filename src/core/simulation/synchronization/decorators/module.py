#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decorator-Factory für thread-sichere Modul-Level-Funktionen.

Implementiert @synchronized_module(lock) für globale Funktionen.
"""

from __future__ import annotations

import threading
from typing import Any, Callable, TypeVar

from ..primitives.wrapper import create_lock_wrapper

F = TypeVar("F", bound=Callable[..., Any])


def synchronized_module(lock: threading.Lock | threading.RLock) -> Callable[[F], F]:
    """
    Decorator-Factory für Modul-Level-Funktionen mit explizitem Lock.

    Args:
        lock: Lock-Objekt für die Synchronisation (Lock oder RLock)

    Returns:
        Decorator-Funktion für thread-sichere Funktionen

    Raises:
        TypeError: Falls lock kein Lock-Objekt ist
    """
    return create_lock_wrapper(lambda *args, **kwargs: lock)
