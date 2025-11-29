# tools/setup/steps/base/decorator.py
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar, TYPE_CHECKING

from tools.setup.steps.base.result import StepResult, PrepareResult
from tools.setup.ui.output.error import error as format_error

if TYPE_CHECKING:
    from tools.setup.steps.base.meta import BaseStepContext  # nur für Typchecker

P = ParamSpec("P")
T = TypeVar("T")


def _log_failure(
        self: Any,
        ctx: "BaseStepContext",
        *,
        cause: str,
        details: str,
        label: str,
        error_hint: str,
        with_block: bool,
) -> None:
    """
    Gemeinsame Fehlerbehandlung für Step- und Prepare-Ergebnisse.

    - formatiert Message via self.output(...)
    - schreibt in ctx.log
    - optional: YAML-Errorblock in self._error_block für BaseStep.run(...)
    """
    msg = self.output(
        ctx,
        field="failure",
        cause=cause,
        details=details,
    )

    ctx.log.write_error(
        section=self.name,
        message=msg,
        details=details,
    )

    if with_block:
        # YAML-Block für BaseStep.run(...), z. B. unter dem Progress-Balken
        self._error_block = format_error(
            step=self.name,
            stid=self.stid,
            exc_type=cause or "step_failed",
            message=error_hint or label or "Schritt fehlgeschlagen",
            traceback_text=details,
        )


def handle_step(
        func: Callable[P, StepResult],
) -> Callable[P, bool]:
    """
    Dekorator für step(...)-Implementierungen, die StepResult() liefern.
    """

    @wraps(func)
    def wrapper(self, ctx, prepared, progress, *args: P.args, **kwargs: P.kwargs) -> bool:
        result: StepResult = func(self, ctx, prepared, progress, *args, **kwargs)
        exists = progress is not None

        # Progress-Status (UI hängt nur an label/error_hint, nicht am Raw-Output)
        match result.ok, exists:
            case (True, True):
                text = result.label or "OK"
                progress.set_status(f"Finished /   {text}")

            case (False, True):
                text = result.label or result.error_hint or "Fehler"
                progress.set_status(f"Failed   /   {text}")

            case (False, False):
                _log_failure(
                    self,
                    ctx,
                    cause=result.cause or "step_failed",
                    details=result.details or "",
                    label=result.label or "",
                    error_hint=result.error_hint or "",
                    with_block=True,
                )

        return result.ok

    return wrapper


def handle_prepare(
        func: Callable[[Any, "BaseStepContext"], PrepareResult[T]],
) -> Callable[[Any, "BaseStepContext"], T | None]:
    """
    Dekorator für prepare(...)-Implementierungen, die PrepareResult[T] liefern.
    """

    @wraps(func)
    def wrapper(self: Any, ctx: "BaseStepContext") -> T | None:
        result: PrepareResult[T] = func(self, ctx)

        if not result.ok:
            _log_failure(
                self,
                ctx,
                cause=result.cause or "prepare_failed",
                details=result.details or "",
                label="",  # Prepare hat keinen "Testnamen"
                error_hint=result.error_hint or "",
                with_block=False,  # kein Errorblock im Progress-Kontext – den gibt es hier noch nicht
            )

            msg = result.error_hint or result.details or "Prepare-Phase fehlgeschlagen."
            raise RuntimeError(msg)

        return result.payload

    return wrapper
