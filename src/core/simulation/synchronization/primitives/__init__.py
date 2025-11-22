#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Low-Level Lock-Primitives für Thread-Synchronisation.

Dieses Package enthält die grundlegenden Building-Blocks für Lock-basierte
Synchronisation. Diese Komponenten werden intern von den decorators/ verwendet
und sollten nicht direkt von außerhalb genutzt werden.

Komponenten:
    - acquire_lock: Context-Manager für sichere Lock-Acquisition
    - create_lock_wrapper: Factory-Funktion für Lock-basierte Decorators

Zweck:
    Die Primitives kapseln die low-level Lock-Verwaltung (acquire/release)
    und stellen sicher, dass Locks immer korrekt freigegeben werden, auch
    bei Exceptions. Sie dienen als Basis für die High-Level-Decorators.

Verwendung:
    Nutze NICHT direkt diese Primitives, sondern die Decorators aus dem
    decorators/ Package. Die Primitives sind als interne Implementierungs-
    details gedacht und ihre API kann sich ändern.

    Für eigene Lock-Decorators:
        Falls du eigene Decorator-Varianten benötigst, kannst du
        create_lock_wrapper() nutzen. Siehe wrapper.py für Details.

Thread-Safety:
    Alle Funktionen in diesem Package sind thread-sicher und exception-sicher.
    Der Context-Manager acquire_lock() garantiert, dass das Lock immer
    freigegeben wird, auch bei Exceptions.

Architektur:
    Die Trennung von primitives/ und decorators/ folgt dem Prinzip der
    Separation of Concerns:
    - primitives/ = WIE funktioniert Locking (Implementierung)
    - decorators/ = WAS wird gelockt (API für Endnutzer)
"""

from .wrapper import acquire_lock, create_lock_wrapper

__all__ = [
    "acquire_lock",
    "create_lock_wrapper",
]
