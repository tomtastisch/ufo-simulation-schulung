from __future__ import annotations

"""
Gemeinsame Hilfsfunktionen für das Setup-System der UFO-Simulation.

Dieses Modul bündelt die häufig verwendeten Utility-Funktionen:

Es dient als schmale Fassade auf die eigentlichen Implementierungen
in ``context`` und ``pause``.
"""

from .context import run_command, short_output
from .module import evaluate, classify, install
from .version import ensure_venv, venv_create

__all__: list[str] = [
    "run_command",
    "short_output",
    "evaluate",
    "classify",
    "install",
    "ensure_venv",
    "venv_create",
]
