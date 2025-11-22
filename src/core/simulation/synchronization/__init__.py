#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread-Synchronisation für die UFO-Simulation.

Stellt generische Decorators für Thread-Sicherheit bereit.
Projektübergreifend einsetzbar ohne Simulationsabhängigkeiten.

Öffentliche API:
    - synchronized: Decorator für Instanzmethoden (self._lock)
    - synchronized_module: Decorator-Factory für Modul-Level-Funktionen
    - conditional: Decorator für Condition-Variable-Methoden
    - acquire_lock: Context Manager für explizite Lock-Acquisition
    - create_lock_wrapper: Factory für eigene Lock-Decorators

Interne Struktur:
    - decorators/: High-Level Decorators für Endnutzer
    - primitives/: Low-Level Building Blocks (nicht direkt nutzen)
"""
# Import von internen Untermodulen
from .decorators.conditional import conditional
from .decorators.instance import synchronized
from .decorators.module import synchronized_module
from .primitives.wrapper import acquire_lock, create_lock_wrapper

__all__ = [
    "synchronized",
    "synchronized_module",
    "conditional",
    "acquire_lock",
    "create_lock_wrapper",
]
