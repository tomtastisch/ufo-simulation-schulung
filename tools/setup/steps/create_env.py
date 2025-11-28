# tools/setup/steps/create_env.py
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import override

from tools.setup.steps.base import BaseStep, StepContext
from tools.setup.ui.progress import ProgressStep
from tools.setup.utils.version import check_python_version, ensure_venv


@dataclass(slots=True)
class CreateEnvStep(BaseStep[None]):
    """
    Setup-Schritt zum Erzeugen der Projekt-Virtualenv.
    """

    stid = "create_env"
    priority = sys.maxsize - 1000

    @override
    def step(
            self,
            ctx: StepContext,
            _prepared: None,
            progress: ProgressStep | None,
    ) -> bool:
        # 1) Python-Version prüfen
        ok, cause, details = check_python_version(ctx)
        if not ok:
            msg = self.output(
                ctx,
                field="failure",
                cause=cause,
                details=details,
            )
            if progress is not None:
                progress.set_status(msg)
            ctx.log.write_error(
                section=self.name,
                message=msg,
                details=details,
            )
            return False

        # 2) venv erzeugen
        ok, cause, details = ensure_venv(ctx, True)
        field = "success" if ok else "failure"
        msg = self.output(
            ctx,
            field=field,
            cause=cause,
            details=details,
        )

        if progress is not None:
            progress.set_status(msg)

        if not ok:
            ctx.log.write_error(
                section=self.name,
                message=msg,
                details=details,
            )

        return ok
