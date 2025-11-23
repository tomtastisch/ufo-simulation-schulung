#!/usr/bin/env python3
"""Setuptools-Hilfsskript für Editier-Installationen."""

import sys

from setuptools import setup


def _run_bootstrap() -> int:
    """Führt Bootstrap-Setup aus."""
    from tools.setup.bootstrap import main as bootstrap_main
    return bootstrap_main()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(_run_bootstrap())
    setup()
