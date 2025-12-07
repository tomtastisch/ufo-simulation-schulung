#!/usr/bin/env python3
"""Setuptools-Hilfsskript für Editier-Installationen."""

import sys


def _run_bootstrap() -> int:
    """Führt das neue Setup-Bootstrap-System aus."""
    from tools.bootstrap import execute
    return execute(sys.argv[1:])


if __name__ == "__main__":
    # Immer das neue Bootstrap-System verwenden
    raise SystemExit(_run_bootstrap())