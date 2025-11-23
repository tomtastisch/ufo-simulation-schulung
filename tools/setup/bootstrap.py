from __future__ import annotations

"""Orchestrator für die Setup-Pipeline."""

import sys
from contextlib import nullcontext

from tools.setup.boot.context import (
    BootstrapContext,
    StepDefinition,
    build_context,
    build_pipeline,
)
from tools.setup.boot.steps.check import run_tests
from tools.setup.config import BootstrapConfig
from tools.ui import SetupConsole, StepProgress
from tools.ui.resources import TextCatalog
from enum import StrEnum

_TEXTS = TextCatalog()


class TestStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


def _print_test_hint(status: TestStatus) -> None:
    """Gibt den passenden Test-Hinweis anhand des Status aus."""
    field_map = {
        TestStatus.SUCCESS: "success_hint",
        TestStatus.FAILED: "failed_hint",
        TestStatus.SKIPPED: "skipped_hint",
    }
    field = field_map[status]
    SetupConsole.info(
        _TEXTS.format(
            "tests",
            field=field,
            success=_TEXTS.icon("success", "✅"),
            warning=_TEXTS.icon("warning", "⚠️"),
        ),
    )


def _run_step(step: StepDefinition, ctx: BootstrapContext) -> bool:
    """Führt einen einzelnen Setup-Schritt mit Fortschrittsanzeige aus."""
    if not step.enabled:
        SetupConsole.info(f"Überspringe Schritt: {step.label}")
        return True

    cm = StepProgress(step.label, total=1) if step.show_progress else nullcontext()
    with cm:
        try:
            ok = step.func(ctx)
        except Exception as exc:  # noqa: BLE001
            ctx.log.write_error(
                f"Setup-Schritt: {step.label}",
                "Unerwartete Ausnahme im Setup-Schritt",
                str(exc),
            )
            SetupConsole.error(f"Schritt '{step.label}' ist mit einem Fehler abgebrochen.")
            return False

    if ok:
        SetupConsole.success(f"Schritt '{step.label}' erfolgreich.")
    else:
        SetupConsole.error(f"Schritt '{step.label}' fehlgeschlagen.")
    return ok


def main(argv: list[str] | None = None) -> int:
    """Haupteinstieg für das Setup (wird von setup.py aufgerufen)."""
    args = list(sys.argv[1:] if argv is None else argv)

    skip_tests = "--skip-tests" in args
    if skip_tests:
        args.remove("--skip-tests")

    config = BootstrapConfig(skip_tests=skip_tests)

    try:
        ctx = build_context(config)
    except Exception as exc:  # noqa: BLE001
        SetupConsole.error(f"Fehler beim Initialisieren des Setup-Kontexts: {exc}")
        return 1

    SetupConsole.header(_TEXTS.text("setup_header", field="title"))
    SetupConsole.info(_TEXTS.text("setup_header", field="intro"))
    SetupConsole.legend()
    SetupConsole.info(f"Betriebssystem: {ctx.platform.system}\n")

    for step in build_pipeline(ctx):
        if not _run_step(step, ctx):
            SetupConsole.from_resource("troubleshooting")
            return 1

    if ctx.profile.uses_pytest:
        if not config.skip_tests:
            status = TestStatus.SUCCESS if run_tests(ctx.platform, ctx.log) else TestStatus.FAILED
        else:
            status = TestStatus.SKIPPED
        _print_test_hint(status)

    SetupConsole.from_resource("next_steps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
