# tools/setup/steps/install_deps.py
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import chain
from typing import ClassVar, override

from tools.setup.steps.base import (
    BaseStep,
    BaseStepContext,
    StepResult,
    PrepareResult,
    handle_prepare,
)
from tools.setup.ui import CATALOG
from tools.setup.ui.progress import ProgressStep
from tools.setup.utils import run_command, short_output
from tools.setup.utils.ui_text import initial_running_text, running_text, failed_text

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

    stid: ClassVar[str] = "dependencies"
    prio: ClassVar[int] = 9999

    @override
    def estimate_total(self, prepared: Sequence[Command] | None) -> int | None:
        if prepared:
            return len(prepared)
        return 1


    @override
    @handle_prepare
    def prepare(self, ctx: BaseStepContext) -> PrepareResult[tuple[str, ...]]:
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

        return PrepareResult(
            ok=True,
            payload=tuple(commands),
        )


    @override
    def _step_impl(
            self,
            ctx: BaseStepContext,
            prepared: Sequence[Command] | None,
            progress: ProgressStep | None,
    ) -> StepResult:
        assert prepared is not None, "InstallDepsStep.prepare() muss Commands liefern."

        cwd = str(ctx.config.repo_root)
        total = len(prepared) or 1
        empty_output = "keine Ausgabe"

        if total and progress is not None:
            progress.set_status(initial_running_text())

        ok = True
        cause: str | None = None
        last_label = ""
        last_details = ""
        error_hint: str | None = None

        for index, (argv, label) in enumerate(prepared, start=1):
            last_label = label

            # Laufender Status: welches Paket wird gerade installiert?
            if progress is not None:
                progress.set_status(
                    running_text(f"Installiere: {label} ({index}/{total})")
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

            # Fehlerstatus
            if progress is not None:
                progress.set_status(failed_text(label))

            error_hint = f"{label}: {short}"
            break

        # Auf Summen-Label mappen:
        # - Erfolg  → „Alle Abhängigkeiten installiert.“
        # - Fehler  → Name des zuletzt fehlgeschlagenen Pakets
        label = (
            CATALOG.format(
                "step_default",
                field="install_done",
                default="Alle Abhängigkeiten installiert.",
            )
            if ok
            else last_label
        )

        return StepResult(
            ok=ok,
            cause=cause or "",
            details=last_details or empty_output,
            label=label,
            error_hint=error_hint or "",
        )