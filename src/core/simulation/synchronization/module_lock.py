#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decorator-Factory für thread-sichere Modul-Level-Funktionen."""

from __future__ import annotations

import threading
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def synchronized_module(lock: threading.Lock | threading.RLock) -> Callable[[F], F]:
    """
    Decorator-Factory für Funktionen mit explizitem Lock-Parameter.

    Erwartet threading.Lock oder threading.RLock als Parameter.
    Serialisiert Zugriffe, wiedereintrittsfähig bei RLock, exception-sicher.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with lock:
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
