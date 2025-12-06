from __future__ import annotations

"""
Fassade für die Setup-Schritte der UFO-Simulation.

Dieses Paket bündelt die von außen genutzten Funktionen der einzelnen
Setup-Step-Module und stellt einen stabilen Importpunkt für den Bootstrap
bereit.
"""

from .base import BaseStep
from .create_env import CreateEnvStep
from .install_deps import InstallDepsStep
from .linter_check import EvaluateImportsStep
from .test_runner import RunTestsStep
from .typing_check import TypingCheckStep

STEPS: tuple[type[BaseStep[object]], ...] = (
    CreateEnvStep,
    InstallDepsStep,
    TypingCheckStep,
    EvaluateImportsStep,
    RunTestsStep,
)

__all__ = [cls.__name__ for cls in STEPS]
