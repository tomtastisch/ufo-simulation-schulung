#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread-Synchronisation für die UFO-Simulation.

Stellt generische Decorators für Thread-Sicherheit bereit.
Projektübergreifend einsetzbar ohne Simulationsabhängigkeiten.

Komponenten:
    - synchronized: Decorator für Instanzmethoden (self._lock)
    - synchronized_module: Decorator-Factory für Modul-Level-Funktionen
    - conditional: Decorator für Condition-Variable-Methoden
    - acquire_lock: Context Manager für explizite Lock-Acquisition
    - create_lock_wrapper: Factory für eigene Lock-Decorators
"""

from .instance_lock import synchronized
from .module_lock import synchronized_module
from .conditional_lock import conditional
from .lock_wrapper import acquire_lock, create_lock_wrapper

__all__ = [
    "synchronized",
    "synchronized_module",
    "conditional",
    "acquire_lock",
    "create_lock_wrapper",
]


