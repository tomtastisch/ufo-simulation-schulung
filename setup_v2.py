#!/usr/bin/env python3
"""Setuptools-Hilfsskript für Editier-Installationen."""

import sys

from tools import setup


def _run_bootstrap() -> int:
    """Führt das neue Setup-Bootstrap-System aus."""
    from tools.bootstrap import execute
    return execute()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(_run_bootstrap())
    setup()