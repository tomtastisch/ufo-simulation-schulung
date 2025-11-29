# tools/setup/steps/install_deps.py
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import chain
from typing import override

from tools.setup.steps.base.config import step_config

from tools.setup.steps.base import BaseStep, BaseStepContext, StepResult, handles_step_result
from tools.setup.ui import CATALOG
from tools.setup.ui.progress import ProgressStep
from tools.setup.utils import run_command, short_output

Command = tuple[tuple[str, ...], str]  # (argv, label)


@step_config(stid="dependencies", priority=9999)
@dataclass(slots=True)
class InstallDepsStep(BaseStep[Sequence[Command]]):
    """
    Setup-Schritt zur Installation der Projekt-Abhängigkeiten aus pyproject.toml.

    Strategie:
    - Projekt im Editable-Modus installieren: python -m pip install -e .
    - Laufzeit-Dependencies aus [project].dependencies einzeln installieren
    - Dev-Dependencies aus [project.optional-dependencies].dev einzeln installieren
    """

    @override
    def prepare(self, ctx: BaseStepContext) -> tuple[Command, ...] | None:
        """
        Erzeugt die Liste von Installations-Kommandos aus dem bereits geladenen
        PyProjectProfile (runtime_requirements + dev_requirements).
        """
        python = str(ctx.config.venv_python)
        base = (python, "-m", "pip", "install")

        commands: list[Command] = [((*base, "-e", "."), "Projekt (editable)")]

        for name, spec in chain(
                ctx.profile.runtime_requirements.items(),
                ctx.profile.dev_requirements.items(),
        ):
            label = f"{name}{spec}"
            commands.append(((*base, label), label))

        return tuple(commands)

    @override
    @handles_step_result
    def step(
            self,
            ctx: BaseStepContext,
            prepared: Sequence[Command] | None,
            progress: ProgressStep | None,
    ) -> StepResult:
        assert prepared is not None, "InstallDepsStep.prepare() muss Commands liefern."

        cwd = str(ctx.config.repo_root)
        total = len(prepared) or 1
        empty_output = "keine Ausgabe"

        def fmt(field: str, default: str, **kwargs: object) -> str:
            return CATALOG.format(
                "step_default",
                field=field,
                default=default,
                **kwargs,
            )

        def status(field: str, default: str, **kwargs: object) -> None:
            if progress is not None:
                progress.set_status(fmt(field, default, **kwargs))

        if total:
            status(
                "progress_running",
                "Running  /   Installiere Abhängigkeiten ({total} Pakete)",
                total=total,
            )

        ok = True
        cause: str | None = None
        last_label = ""
        last_details = ""
        error_hint: str | None = None

        for index, (argv, label) in enumerate(prepared, start=1):
            last_label = label

            status(
                "progress_running",
                "Running  /   {details}",
                details=fmt(
                    "install_details",
                    "Installiere: {package} ({index}/{total})",
                    package=label,
                    index=index,
                    total=total,
                ),
            )

            result = run_command(argv, cwd=cwd)
            raw = (result.stdout or "") + (result.stderr or "")
            last_details = raw or empty_output

            if result.returncode == 0:
                if progress is not None:
                    progress.advance(1)
                continue

            # Fehlerfall
            ok = False
            cause = "pip_install_failed"
            short = short_output(raw) or last_details

            status(
                "progress_failed",
                "Failed   /   {details}",
                details=fmt(
                    "install_failed",
                    "{package}: {details}",
                    package=label,
                    details=short,
                ),
            )

            error_hint = f"{label}: {short}"
            break

        label = last_label if ok else fmt(
                "install_done",
                "Alle Abhängigkeiten installiert.",
        )

        return StepResult(
            ok=ok,
            cause=cause,
            details=last_details,
            label=label,
            error_hint=error_hint,
        )
