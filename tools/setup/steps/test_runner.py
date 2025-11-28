# tools/setup/steps/test_runner.py
from __future__ import annotations

from dataclasses import dataclass
from typing import override

from tools.setup.steps.base import BaseStep, StepContext
from tools.setup.ui.progress import ProgressStep
from tools.setup.ui import CATALOG
from tools.setup.utils import module


@dataclass(slots=True)
class RunTestsStep(BaseStep[tuple[str, ...]]):
    """
    Setup-Schritt zum Ausführen der Test-Suite via pytest.

    Design:
    - prepare() sammelt alle Test-NodeIDs via "pytest --collect-only -q".
    - estimate_total() leitet die Balkenlänge aus der Anzahl Tests ab.
    - step() führt jeden Test einzeln aus und aktualisiert Progress/Status.
    """

    stid = "tests"
    priority = 0

    @override
    def prepare(self, ctx: StepContext) -> tuple[str, ...]:
        """Sammelt alle Test-NodeIDs, die später als Arbeitseinheiten dienen."""
        ok, output, exc_info = module.evaluate(
            python=str(ctx.config.venv_python),
            module="pytest",
            cwd=ctx.config.repo_root,
            extra_args=("--collect-only", "-q"),
        )

        if not ok:
            kind, details = module.classify(
                exc_info=exc_info,
                output=output,
                module="pytest",
            )
            msg = self.output(
                ctx,
                field="failure",
                cause=kind,
                details=details or output or "pytest --collect-only fehlgeschlagen",
            )
            ctx.log.write_error(
                section=self.name,
                message=msg,
                details=details or output or "",
            )
            # Harte Exception → BaseStep.run() behandelt das wie einen Step-Fehler
            raise RuntimeError(f"pytest Collect-Phase fehlgeschlagen: {kind}: {details}")

        tests: list[str] = []
        for line in (output or "").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            # Grober Filter: pytest gibt bei -q pro Test üblicherweise eine NodeID aus.
            if stripped.startswith(("collected ", "<", "=")):
                continue
            tests.append(stripped)

        return tuple(tests)

    @override
    def step(
            self,
            ctx: StepContext,
            prepared: tuple[str, ...] | None,
            progress: ProgressStep | None,
    ) -> bool:
        tests = prepared or tuple()
        python = str(ctx.config.venv_python)
        cwd = ctx.config.repo_root

        # Fall: keine Tests gefunden → einmaliger pytest-Run als Fallback.
        if not tests:
            ok, output, exc_info = module.evaluate(
                python=python,
                module="pytest",
                cwd=cwd,
                extra_args=(),
            )

            cause = ""
            details = ""

            match exc_info, ok:
                case str() as err, _:
                    cause = "tests_running_error"
                    details = err
                case None, False:
                    cause = "tests_failed"
                    details = output or "keine Ausgabe"

            msg = self.output(
                ctx,
                field="success" if ok else "failure",
                cause=cause,
                details=details,
            )

            if progress is not None:
                # Status über CATALOG (Running/Finished/Failed) aktualisieren
                field = "progress_finished" if ok else "progress_failed"
                default = (
                    "Finished /   Alle Tests erfolgreich."
                    if ok
                    else "Failed   /   Tests fehlgeschlagen – Details siehe Log."
                )
                progress.set_status(
                    CATALOG.format(
                        "step_default",
                        field=field,
                        default=default,
                        details=details or output or "",
                    )
                )

            if not ok:
                ctx.log.write_error(
                    section=self.name,
                    message=msg,
                    details=details or output or "",
                )

            return ok

        total = len(tests)
        ok_overall = True
        cause = ""
        details = ""
        last_output = ""

        for index, nodeid in enumerate(tests, start=1):
            # Fortschritts-Text: konkreter Testname
            if progress is not None:
                test_details = CATALOG.format(
                    "RunTestsStep",
                    field="test_details",
                    default="Test {index}/{total}: {test}",
                    index=index,
                    total=total,
                    test=nodeid,
                )
                running = CATALOG.format(
                    "step_default",
                    field="progress_running",
                    default="Running  /   {details}",
                    details=test_details,
                )
                progress.set_status(running)

            ok, output, exc_info = module.evaluate(
                python=python,
                module="pytest",
                cwd=cwd,
                extra_args=(nodeid,),
            )
            last_output = output or ""

            test_cause = ""
            test_details = ""

            match exc_info, ok:
                case str() as err, _:
                    test_cause = "tests_running_error"
                    test_details = err
                case None, False:
                    test_cause = "tests_failed"
                    test_details = output or "keine Ausgabe"

            if progress is not None:
                progress.advance(1)

            if not ok:
                ok_overall = False
                cause = test_cause
                details = test_details
                break

        msg = self.output(
            ctx,
            field="success" if ok_overall else "failure",
            cause=cause,
            details=details or last_output or "",
        )

        # Finaler Status unter dem Balken
        if progress is not None:
            field = "tests_done" if ok_overall else "tests_failed"
            default_details = (
                "Alle Tests erfolgreich."
                if ok_overall
                else "Tests fehlgeschlagen – Details siehe Log."
            )
            details_text = CATALOG.format(
                "RunTestsStep",
                field=field,
                default=default_details,
            )

            status_field = "progress_finished" if ok_overall else "progress_failed"
            status_default = (
                "Finished /   {details}"
                if ok_overall
                else "Failed   /   {details}"
            )

            progress.set_status(
                CATALOG.format(
                    "step_default",
                    field=status_field,
                    default=status_default,
                    details=details_text,
                )
            )

        if not ok_overall:
            ctx.log.write_error(
                section=self.name,
                message=msg,
                details=details or last_output or "",
            )

        return ok_overall
