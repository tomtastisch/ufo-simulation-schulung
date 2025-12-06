# tools/setup/steps/create_env.py
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import ClassVar, override

from tools.setup.steps.base import BaseStep, BaseStepContext, StepResult
from tools.setup.ui.progress import ProgressStep
from tools.setup.utils import run_command


@dataclass(slots=True)
class CreateEnvStep(BaseStep[None]):
    """
    Setup-Schritt zum Erzeugen der Projekt-Virtualenv.
    """

    # Registrierung über BaseStepCore
    stid: ClassVar[str] = "create_env"
    prio: ClassVar[int] = sys.maxsize - 1000


    @override
    def _step_impl(
            self,
            ctx: BaseStepContext,
            prepared: None,
            progress: ProgressStep | None,
    ) -> StepResult:
        # Host-Python verwenden, um die venv zu erstellen
        argv = (sys.executable, "-m", "venv", str(ctx.config.venv_dir))
        result = run_command(argv, cwd=str(ctx.config.repo_root))

        if result.returncode == 0:
            return StepResult(
                ok=True,
                label="Virtuelle Umgebung erstellt/gefunden.",
                details=result.stdout or "",
            )

        details = (result.stdout or "") + (result.stderr or "")
        return StepResult(
            ok=False,
            cause="create_env_failed",
            details=details or "keine Ausgabe",
            label="create_env",
            error_hint="Erzeugen der virtuellen Umgebung ist fehlgeschlagen.",
        )