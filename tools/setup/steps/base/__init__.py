# tools/setup/steps/base/__init__.py
from __future__ import annotations

"""
Basis-API für Setup-Schritte.

Bündelt die zentrale Step-Basis und den StepContext.
"""

from .step import BaseStep
from .meta import StepContext

__all__: list[str] = [
    "BaseStep",
    "StepContext",
]
