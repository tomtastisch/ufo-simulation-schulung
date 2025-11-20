#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projektspezifische Exception-Klassen für die UFO-Simulation.

Dieses Modul definiert eine Hierarchie von Exception-Klassen, die spezifisch
für die Simulation verwendet werden. Dies ermöglicht eine klare Typisierung
von Fehlern und erleichtert die Fehlerbehandlung.
"""


class SimulationError(Exception):
    """
    Basis-Exception für alle simulationsspezifischen Fehler.

    Diese Klasse dient als Oberklasse für alle projektspezifischen Exceptions
    und ermöglicht es, simulationsspezifische Fehler gezielt zu behandeln.
    """

    pass


class ConfigError(SimulationError):
    """
    Exception für Konfigurationsfehler.

    Wird ausgelöst, wenn ungültige Konfigurationswerte verwendet werden
    oder die Konfiguration nicht korrekt initialisiert werden kann.
    """

    pass
