#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-Test für core.simulation.infrastructure.logging_setup Modul.

Testet grundlegende Import- und Funktionalität der Logging-Setup-Funktionen.
"""

import logging
import sys
from pathlib import Path

# Sicherstellen, dass src/ im Python-Pfad ist
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_logging_setup_import():
    """Test: Logging-Setup-Funktionen können importiert werden."""
    from core.simulation.infrastructure import configure_logging, get_logger
    assert configure_logging is not None
    assert get_logger is not None


def test_get_logger_returns_logger():
    """Test: get_logger gibt ein Logger-Objekt zurück."""
    from core.simulation.infrastructure import get_logger

    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_get_logger_with_module_name():
    """Test: get_logger funktioniert mit __name__."""
    from core.simulation.infrastructure import get_logger

    logger = get_logger(__name__)
    assert isinstance(logger, logging.Logger)
    # Der Name sollte den Modulnamen enthalten
    assert logger.name == __name__


def test_configure_logging_is_idempotent():
    """Test: configure_logging kann mehrfach aufgerufen werden ohne Fehler."""
    from core.simulation.infrastructure import configure_logging

    # Sollte keine Exceptions werfen
    configure_logging()
    configure_logging()
    configure_logging()


def test_configure_logging_with_custom_level():
    """Test: configure_logging akzeptiert benutzerdefiniertes Log-Level."""
    from core.simulation.infrastructure import configure_logging

    # Sollte keine Exceptions werfen
    configure_logging(level=logging.DEBUG)
    configure_logging(level=logging.WARNING)


def test_configure_logging_with_custom_format():
    """Test: configure_logging akzeptiert benutzerdefinierten Format-String."""
    from core.simulation.infrastructure import configure_logging

    # Sollte keine Exceptions werfen
    configure_logging(format_string='%(name)s - %(message)s')


def test_configure_logging_with_custom_datefmt():
    """Test: configure_logging akzeptiert benutzerdefiniertes Datumsformat."""
    from core.simulation.infrastructure import configure_logging

    # Sollte keine Exceptions werfen
    configure_logging(datefmt='%H:%M:%S')


def test_logger_can_log_messages():
    """Test: Logger kann Nachrichten ausgeben ohne Fehler."""
    from core.simulation.infrastructure import get_logger

    logger = get_logger("test_logging")
    
    # Diese sollten keine Exceptions werfen
    logger.debug("Debug-Nachricht")
    logger.info("Info-Nachricht")
    logger.warning("Warning-Nachricht")
    logger.error("Error-Nachricht")


def test_multiple_loggers_independent():
    """Test: Mehrere Logger sind unabhängig voneinander."""
    from core.simulation.infrastructure import get_logger

    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    assert logger1 is not logger2
    assert logger1.name == "module1"
    assert logger2.name == "module2"


def test_same_logger_name_returns_same_instance():
    """Test: Gleicher Logger-Name gibt gleiche Instanz zurück."""
    from core.simulation.infrastructure import get_logger

    logger1 = get_logger("same_module")
    logger2 = get_logger("same_module")
    
    # logging.getLogger gibt für gleichen Namen gleiche Instanz zurück
    assert logger1 is logger2


if __name__ == "__main__":
    from conftest import run_manual_tests

    tests = [
        test_logging_setup_import,
        test_get_logger_returns_logger,
        test_get_logger_with_module_name,
        test_configure_logging_is_idempotent,
        test_configure_logging_with_custom_level,
        test_configure_logging_with_custom_format,
        test_configure_logging_with_custom_datefmt,
        test_logger_can_log_messages,
        test_multiple_loggers_independent,
        test_same_logger_name_returns_same_instance,
    ]

    run_manual_tests("core.simulation.logging_setup", tests)
