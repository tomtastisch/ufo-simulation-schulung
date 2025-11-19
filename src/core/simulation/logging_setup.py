#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zentrale Logging-Konfiguration für die UFO-Simulation.

Dieses Modul stellt eine zentrale Logging-Konfiguration bereit, die von allen
Modulen des Projekts verwendet werden kann. Dies gewährleistet konsistentes
Logging-Verhalten ohne Nebenwirkungen auf andere Projekte im gleichen Prozess.
"""

import logging
from typing import Optional


# Flag um sicherzustellen, dass Konfiguration nur einmal gesetzt wird
_logging_configured = False


def configure_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    datefmt: Optional[str] = None,
) -> None:
    """
    Konfiguriert das Logging-System für die Simulation.

    Diese Funktion sollte einmalig beim Start der Anwendung aufgerufen werden.
    Sie verwendet logging.basicConfig mit moderaten Einstellungen, die keine
    störenden Nebenwirkungen auf andere Projekte im gleichen Prozess haben.

    Parameter
    ---------
    level : int, optional
        Das Log-Level (Standard: logging.INFO)
    format_string : str, optional
        Das Format für Log-Nachrichten. Falls None, wird ein Standard-Format verwendet.
    datefmt : str, optional
        Das Datumsformat für Log-Nachrichten. Falls None, wird ein Standard-Format verwendet.

    Hinweise
    --------
    - Die Funktion ist idempotent: mehrfache Aufrufe haben keine zusätzlichen Effekte
    - Verwendet moderate Einstellungen, um Interferenzen mit anderen Projekten zu vermeiden
    - Konfiguriert nur den Root-Logger
    """
    global _logging_configured

    if _logging_configured:
        return

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if datefmt is None:
        datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(level=level, format=format_string, datefmt=datefmt)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Gibt einen Logger mit dem angegebenen Namen zurück.

    Diese Hilfsfunktion vereinfacht das Abrufen von Loggern und stellt sicher,
    dass das Logging-System konfiguriert ist, bevor der Logger zurückgegeben wird.

    Parameter
    ---------
    name : str
        Der Name des Loggers (typischerweise __name__ des aufrufenden Moduls)

    Rückgabe
    --------
    logging.Logger
        Ein Logger-Objekt mit dem angegebenen Namen

    Beispiel
    --------
    >>> logger = get_logger(__name__)
    >>> logger.info("Simulation gestartet")
    """
    # Stelle sicher, dass Logging konfiguriert ist
    if not _logging_configured:
        configure_logging()

    return logging.getLogger(name)
