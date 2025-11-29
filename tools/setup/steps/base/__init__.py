# tools/setup/steps/base/__init__.py
from __future__ import annotations

"""
Basis-API für Setup-Schritte.

Bündelt die zentrale Step-Basis und den StepContext.
"""

from .step import BaseStep
from .meta import BaseStepContext, BaseStepCore
from .result import StepResult, PrepareResult
from .decorator import handle_step, handle_prepare

__all__: list[str] = [
    # step interface
    "BaseStep",
    "BaseStepCore",
    "BaseStepContext",
    # result types
    "StepResult",
    "PrepareResult",
    # decorators
    "handle_step",
    "handle_prepare",
]
