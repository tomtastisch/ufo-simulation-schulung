#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Observer-Modul für Phasenbestimmung und Manöveranalyse.

Implementiert rein lesende Analyse-Logik für UFO-Zustände ohne Schreibzugriffe.
Erkennt Flugphasen und Manöver deterministisch aus Zustandswerten und Historie.
"""

from .heading_delta import normalize_heading_delta
from .observer import ManeuverAnalysis, StateObserver
from .phase import Phase, compute_phase

__all__ = [
    "Phase",
    "ManeuverAnalysis",
    "compute_phase",
    "normalize_heading_delta",
    "StateObserver",
]
