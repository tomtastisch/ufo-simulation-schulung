from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final, override

from tools.setup.steps.base import BaseStep, StepContext
from tools.setup.ui import CATALOG
from tools.setup.ui.progress import ProgressStep
from tools.setup.utils import run_command, short_output

Command = tuple[tuple[str, ...], str]  # (argv, label)


@dataclass(slots=True)
class InstallDepsStep(BaseStep[Sequence[Command]]):
    """
    Setup-Schritt zur Installation der Projekt-Abhängigkeiten aus pyproject.toml.

    Strategie:
    - Projekt im Editable-Modus installieren: python -m pip install -e .
    - Laufzeit-Dependencies aus [project].dependencies einzeln installieren
    - Dev-Dependencies aus [project.optional-dependencies].dev einzeln installieren
    """

    stid = "dependencies"
    priority = 9999

    @override
    def prepare(self, ctx: StepContext) -> Sequence[Command]:
        python = str(ctx.config.venv_python)

        runtime = ctx.profile.runtime_requirements
        dev = ctx.profile.dev_requirements

        def build_spec(name: str, spec: str) -> str:
            return f"{name}{spec}" if spec else name

        commands: list[Command] = [((python, "-m", "pip", "install", "-e", "."), "Projekt (editable)",)]

        for name, spec in runtime.items():
            pkg_spec = build_spec(name, spec)
            commands.append(((python, "-m", "pip", "install", pkg_spec), pkg_spec))

        for name, spec in dev.items():
            pkg_spec = build_spec(name, spec)
            commands.append(((python, "-m", "pip", "install", pkg_spec), pkg_spec))

        return tuple(commands)

    @override
    def step(
            self,
            ctx: StepContext,
            prepared: Sequence[Command] | None,
            progress: ProgressStep | None,
    ) -> bool:
        assert prepared is not None, "InstallDepsStep.prepare() muss Commands liefern."

        cwd = str(ctx.config.repo_root)
        total = len(prepared) or 1

        def fmt(field: str, default: str, **kwargs: object) -> str:
            return CATALOG.format(
                "step_default",
                field=field,
                default=default,
                **kwargs,
            )

        def set_status(field: str, default: str, **kwargs: object) -> None:
            if progress:
                progress.set_status(fmt(field=field, default=default, **kwargs))

        for index, (argv, label) in enumerate(prepared, start=1):
            set_status(
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

            if result.returncode != 0:
                details_text = short_output(raw) or raw or "keine Ausgabe"

                set_status(
                    "progress_failed",
                    "Failed   /   {details}",
                    details=fmt(
                        "install_failed",
                        "{package}: {details}",
                        package=label,
                        details=details_text,
                    ),
                )
                if progress:
                    progress.mark_failed()

                msg = self.output(
                    ctx,
                    field="failure",
                    cause="pip_install_failed",
                    details=details_text,
                )
                ctx.log.write_error(
                    section=self.name,
                    message=msg,
                    details=raw or "keine Ausgabe",
                )
                return False

            if progress:
                progress.advance(1)

        set_status(
            "progress_finished",
            "Finished /   {details}",
            details=fmt(
                "install_done",
                "Alle Abhängigkeiten installiert.",
            ),
        )

        if progress:
            progress.mark_finished()

        return True
