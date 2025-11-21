#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zustandsrepräsentation für UFO-Simulation.

Kapselt die vollständige Zustandsrepräsentation als immutable dataclass
und thread-sichere Zustandsverwaltung.

Komponenten:
    - UfoState: Frozen dataclass für physikalischen Zustand (Position, Geschwindigkeit, etc.)
    - StateManager: Thread-sichere Zustandsverwaltung mit RLock
"""

from .manager import StateManager
from .state import UfoState

__all__ = ["UfoState", "StateManager"]


