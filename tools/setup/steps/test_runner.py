from __future__ import annotations

import logging
import re
from dataclasses import dataclass
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
from tools.setup.utils import module, run_single

logger = logging.getLogger(__name__)

# Beispielzeilen aus pytest --collect-only:
# <Dir ufo-simulation-schulung>
#   <Dir tests>
#     <Dir core>
#       <Dir simulation>
#         <Dir observer>
#           <Module test_heading_delta.py>
#             <Class TestNormalizeHeadingDelta>
#               <Function test_no_wrap_around_positive_small>
_COLLECT_LINE_RE = re.compile(
    r"^(?P<indent>\s*)<(?P<kind>Dir|Module|Class|Function) (?P<name>[^>]+)>"
)


@dataclass(slots=True)
class RunTestsStep(BaseStep[tuple[tuple[str, str], ...]]):
    """
    Setup-Schritt zum Ausführen der Test-Suite via pytest.

    prepared-Payload:
        tuple[(testfile_relpath, qualified_name), ...]

    Beispiel eines Eintrags:
        ("tests/core/simulation/observer/test_heading_delta.py",
         "TestNormalizeHeadingDelta::test_no_wrap_around_positive_small")
    """

    stid: ClassVar[str] = "tests"
    prio: ClassVar[int] = 0

    @override
    def estimate_total(
            self,
            prepared: tuple[tuple[str, str], ...] | None,
    ) -> int | None:
        if prepared:
            return len(prepared)
        # Fallback: Gesamtlauf
        return 1

    @override
    @handle_prepare
    def prepare(self, ctx: BaseStepContext) -> PrepareResult[tuple[tuple[str, str], ...]]:
        """
        Führt `pytest --collect-only` aus und baut daraus ein 2D-Array:

            [(testfile_relpath, qualified_name), ...]

        qualified_name ist z. B. "Class::SubClass::test_func"
        oder bei freien Funktionen einfach "test_func".
        """
        ok, output, exc_info = module.evaluate(
            python=str(ctx.config.venv_python),
            module="pytest",
            cwd=ctx.config.repo_root,
            extra_args=("--collect-only",),
        )

        if not ok:
            kind, details = module.classify(
                exc_info=exc_info,
                output=output,
                module="pytest",
            )
            text = details or output or "pytest --collect-only fehlgeschlagen"
            return PrepareResult(
                ok=False,
                cause=kind,
                details=text,
                error_hint=text,
                payload=None,
            )

        text = output or ""

        # Stack über die Baumstruktur; jedes Element:
        # (kind, name, level)
        stack: list[tuple[str, str, int]] = []
        pairs: list[tuple[str, str]] = []

        for line in text.splitlines():
            m = _COLLECT_LINE_RE.match(line)
            if not m:
                continue

            indent = m.group("indent") or ""
            level = len(indent) // 2
            kind = m.group("kind")
            name = m.group("name")

            # Stack auf aktuelle Ebene kürzen
            while stack and stack[-1][2] >= level:
                stack.pop()

            if kind == "Function":
                # Wir haben eine Funktion; Module + Klassen aus dem Stack auslesen
                if not any(k == "Module" for k, _, _ in stack):
                    continue

                # Index des letzten Modules im Stack
                module_index = max(
                    i for i, (k, _, _) in enumerate(stack) if k == "Module"
                )

                # Verzeichnisse vor dem Module-Eintrag
                dir_parts = [
                    n
                    for k, n, _ in stack[:module_index]
                    if k == "Dir"
                ]
                module_name = stack[module_index][1]

                # Relativer Pfad ab "tests" aufbauen
                if "tests" in dir_parts:
                    idx = dir_parts.index("tests")
                    dir_parts = dir_parts[idx:]
                module_path = "/".join(dir_parts + [module_name])

                # Klassen zwischen Module und Function einsammeln
                class_names = [
                    n
                    for k, n, _ in stack[module_index + 1:]
                    if k == "Class"
                ]
                if class_names:
                    qualified = "::".join((*class_names, name))
                else:
                    qualified = name

                pairs.append((module_path, qualified))
                continue

            # Für Dir / Module / Class: Node in den Stack pushen
            stack.append((kind, name, level))

        return PrepareResult(
            ok=True,
            payload=tuple(pairs),
        )

    @override
    def _step_impl(
            self,
            ctx: BaseStepContext,
            prepared: tuple[tuple[str, str], ...] | None,
            progress: ProgressStep | None,
    ) -> StepResult:
        python = str(ctx.config.venv_python)
        cwd = ctx.config.repo_root

        tests: tuple[tuple[str, str], ...] = prepared or tuple()
        total = len(tests)

        tests_done_label = CATALOG.format(
            "RunTestsStep",
            field="tests_done",
            default="Alle Tests erfolgreich.",
        )
        tests_failed_label = CATALOG.format(
            "RunTestsStep",
            field="tests_failed",
            default="Tests fehlgeschlagen – Details siehe Log.",
        )

        def run_with_progress(
                *,
                nodeid: str | None,
                status: str | None,
        ) -> tuple[bool, str | None, str]:
            # ====================================================
            # Deinition interner Methoden
            # ====================================================
            if progress is not None and status:
                progress.set_status(status)

            ok, cause, details = run_single(
                python=python,
                cwd=cwd,
                nodeid=nodeid,
                logger=logger,
            )

            if progress is not None:
                progress.advance(1)

            return ok, cause, details or ""

        def make_result(ok: bool, cause: str | None, details: str) -> StepResult:
            if ok:
                return StepResult.success(
                    label=tests_done_label,
                    details=details,
                )
            return StepResult.failure(
                cause=cause or "tests_failed",
                details=details,
                label=tests_failed_label,
            )

        # ====================================================
        # Methodenstart
        # ====================================================

        # Fall 1: Kein einzelnes Test-Listing → Gesamtlauf
        if not tests:
            ok, cause, details = run_with_progress(
                nodeid=None,
                status="Running  /   pytest-Gesamtlauf",
            )
            return make_result(ok, cause, details)

        # Fall 2: Einzelläufe mit Fortschritt
        last_ok = True
        last_cause: str | None = None
        last_details = ""

        for index, (file_relpath, qualified_name) in enumerate(tests, start=1):
            nodeid = f"{file_relpath}::{qualified_name}"
            func_name = qualified_name.split("::")[-1]
            status = f"Running  /   Test {index}/{total}: {func_name}"

            ok, cause, details = run_with_progress(
                nodeid=nodeid,
                status=status,
            )

            last_ok = ok
            last_cause = cause
            last_details = details

            if not ok:
                break

        return make_result(last_ok, last_cause, last_details)
