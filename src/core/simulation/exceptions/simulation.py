#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simulationsspezifische Exception-Klassen."""


class SimulationError(Exception):
    """Basis-Exception für alle simulationsspezifischen Fehler."""

    pass


class ConfigError(SimulationError):
    """Exception für ungültige Konfigurationswerte oder Initialisierungsfehler."""

    pass

