#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemeinsame Test-Utilities und Fixtures für alle Tests.

Dieses Modul enthält wiederverwendbare Hilfsfunktionen und pytest-Fixtures,
die von mehreren Test-Modulen genutzt werden.
"""

from typing import Callable, List


def run_manual_tests(test_module_name: str, tests: List[Callable]) -> None:
    """
    Führt eine Liste von Test-Funktionen manuell aus (ohne pytest).

    Diese Funktion wird für __main__-Blöcke in Test-Modulen verwendet,
    um Tests auch ohne pytest ausführen zu können.

    Args:
        test_module_name: Name des Test-Moduls (z.B. "core.simulation.exceptions")
        tests: Liste von Test-Funktionen, die ausgeführt werden sollen
    """
    print(f"Running smoke tests for {test_module_name}...")

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
        except Exception as e:
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")

    print("\nAll smoke tests completed.")
