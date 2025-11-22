#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread-sichere Logging-Konfiguration und Logger-Factory.

Stellt zentrale Funktionen für Logging-Setup und Logger-Erzeugung bereit.
Alle Funktionen sind thread-sicher durch @synchronized_module.

Komponenten:
    - configure_logging: Initialisiert das Logging-System (idempotent)
    - get_logger: Factory für konfigurierte Logger

Hinweis zu zukünftigen Erweiterungen:
    Falls eine LoggingConfig-Klasse benötigt wird (z.B. für konfigurierbare
    Log-Levels, Handler, Formatter), sollte diese in simulation.py definiert werden,
    nicht hier. Dies gewährleistet Konsistenz mit anderen Konfigurationen.
"""

import logging
import threading
from typing import Optional

from core.simulation.synchronization import synchronized_module

# Flag und Lock für thread-sichere Konfiguration
_logging_configured = False
_config_lock = threading.RLock()


@synchronized_module(_config_lock)
def configure_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    datefmt: Optional[str] = None,
) -> None:
    """
    Initialisiert das Logging-System (idempotent, thread-sicher).

    Sollte einmalig beim Start aufgerufen werden. Mehrfache Aufrufe haben
    keine zusätzlichen Effekte.
    """
    global _logging_configured

    # Thread-sichere Prüfung und Konfiguration (Lock wird durch Decorator verwaltet)
    if _logging_configured:
        return

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if datefmt is None:
        datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(level=level, format=format_string, datefmt=datefmt)

    _logging_configured = True


@synchronized_module(_config_lock)
def get_logger(name: str) -> logging.Logger:
    """
    Gibt einen konfigurierten Logger zurück (thread-sicher).

    Stellt sicher, dass das Logging-System initialisiert ist, bevor
    der Logger zurückgegeben wird.
    """
    # Stellt sicher, dass Logging konfiguriert ist (thread-sicher durch Decorator)
    if not _logging_configured:
        configure_logging()

    return logging.getLogger(name)
