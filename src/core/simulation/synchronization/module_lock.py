#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decorator-Factory für thread-sichere Modul-Level-Funktionen."""

from __future__ import annotations

import threading
from typing import Any, Callable, TypeVar

from ._lock_wrapper import create_lock_wrapper

F = TypeVar("F", bound=Callable[..., Any])


def synchronized_module(lock: threading.Lock | threading.RLock) -> Callable[[F], F]:
    """
    Decorator-Factory für Modul-Level-Funktionen mit explizitem Lock.

    Erwartet threading.Lock oder threading.RLock als Parameter.
    Nutzt zentrale create_lock_wrapper() Implementation.

    Example:
        >>> import threading
        >>> _module_lock = threading.RLock()
        >>>
        >>> @synchronized_module(_module_lock)
        >>> def critical_function():
        ...     # Thread-sicherer Code
        ...     pass
    """
    return create_lock_wrapper(lambda *args, **kwargs: lock)
