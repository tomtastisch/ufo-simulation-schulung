#!/usr/bin/env python3
"""Setuptools-Hilfsskript für Editier-Installationen.

Die eigentliche Umgebungseinrichtung befindet sich in tools/bootstrap_env.py.
"""

import runpy
import sys
from pathlib import Path
from typing import Callable, SupportsInt, cast

from setuptools import setup


def _ensure_exit_code(value: SupportsInt | int | None) -> int:
    """Konvertiert beliebige int-kompatible Rückgaben in einen Exitcode."""
    return 0 if value is None else int(value)


def _run_bootstrap() -> int:
    repo_root = Path(__file__).resolve().parent
    bootstrap_path = repo_root / "tools" / "bootstrap_env.py"
    module_globals = runpy.run_path(str(bootstrap_path))
    main_obj = module_globals.get("main")
    if not callable(main_obj):
        raise RuntimeError("tools/bootstrap_env.py muss eine main()-Funktion bereitstellen.")

    main_func = cast(Callable[..., SupportsInt | int | None], main_obj)
    return _ensure_exit_code(main_func())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(_run_bootstrap())
    setup()
