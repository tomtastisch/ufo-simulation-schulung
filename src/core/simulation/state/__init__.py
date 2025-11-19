#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State-Paket für UFO-Simulation.

Dieses Paket kapselt die Zustandsrepräsentation der Simulation.

Öffentliche API:
    UfoState: Zentrale Datenstruktur für den physikalischen Zustand des UFOs

Architektur-Konformität:
    - Keine Abhängigkeiten zu höherwertigen Modulen (Controller, View, Command, Observer)
    - Nur config und generische Utilities dürfen importiert werden
"""

from .state import UfoState

__all__ = ["UfoState"]
