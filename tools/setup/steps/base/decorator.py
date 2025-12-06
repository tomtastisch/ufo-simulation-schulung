from __future__ import annotations

from functools import wraps
from typing import (
    Any,
    Callable,
    TYPE_CHECKING,
    TypeVar,
    ParamSpec,
    Concatenate,
)

from tools.setup.steps.base.result import StepResult, PrepareResult
from tools.setup.ui.output.error import error as format_error
from tools.setup.ui.progress import ProgressStep

if TYPE_CHECKING:
    from tools.setup.steps.base.meta import BaseStepContext
    from tools.setup.steps.base.step import BaseStep  # optional, nur für Self-Typ

T = TypeVar("T")
S = TypeVar("S", bound="BaseStep[Any]")  # Self-Typ des Steps

P = ParamSpec("P")  # zusätzliche Parameter nach ctx

PrepT = TypeVar("PrepT")  # Typ von prepared
ProgT = TypeVar("ProgT")  # Typ von progress

_FAILURE_TEMPLATE = "{name}-Phase fehlgeschlagen."


def _log_failure(
        self: Any,
        ctx: "BaseStepContext",
        *,
        func: Callable[..., Any],
        cause: str | None = None,
        details: str | None = None,
        label: str | None = None,
        error_hint: str | None = None,
        with_block: bool = True,
) -> None:
    """Gemeinsame Fehlerbehandlung für Step- und Prepare-Ergebnisse.

    - formatiert Message via self.output(...)
    - schreibt in ctx.log
    - optional: YAML-Errorblock in self._error_block für BaseStep.run(...)
    """

    qualname = getattr(func, "__qualname__", getattr(func, "__name__", "step"))
    effective_label = label or qualname
    default_details = _FAILURE_TEMPLATE.format(name=effective_label)

    effective_cause = cause or f"{qualname}_failed"
    effective_details = details or default_details
    effective_error_hint = error_hint or ""

    msg = self.output(
        ctx,
        field="failure",
        cause=effective_cause,
        details=effective_details,
    )

    ctx.log.write_error(
        section=self.name,
        message=msg,
        details=effective_details,
    )

    if with_block:
        # YAML-Block für BaseStep.run(...), z. B. unter dem Progress-Balken
        self._error_block = format_error(
            step=self.name,
            stid=self.stid,
            exc_type=effective_cause,
            message=effective_error_hint or effective_label or "Schritt fehlgeschlagen",
            traceback_text=effective_details,
        )


def handle_prepare(
        func: Callable[
            Concatenate[S, BaseStepContext, P],
            PrepareResult[T],
        ],
) -> Callable[
    Concatenate[S, BaseStepContext, P],
    T | None,
]:
    """Dekorator für prepare(...)-Implementierungen, die PrepareResult[T] liefern."""

    @wraps(func)
    def wrapper(
            self: S,
            ctx: BaseStepContext,
            *args: P.args,
            **kwargs: P.kwargs,
    ) -> T | None:
        result: PrepareResult[T] = func(self, ctx, *args, **kwargs)
        label = getattr(func, "__qualname__", "prepare")

        if not result.ok:
            _log_failure(
                self,
                ctx,
                func=func,
                cause=result.cause,
                details=result.details,
                label=label,
                error_hint=result.error_hint,
                with_block=False,  # Errorblock wird erst später geschrieben
            )

            default_msg = _FAILURE_TEMPLATE.format(name=label)
            raise_msg = result.error_hint or result.details or default_msg
            # wichtig: Laufzeitverhalten unverändert
            raise RuntimeError(raise_msg)

        return result.payload

    return wrapper


def handle_step(
        func: Callable[
            [S, BaseStepContext, PrepT | None, ProgressStep | None],
            StepResult,
        ],
) -> Callable[
    [S, BaseStepContext, PrepT | None, ProgressStep | None],
    bool,
]:
    """Dekorator für step(...)-Implementierungen, die StepResult liefern."""

    @wraps(func)
    def wrapper(
            self: S,
            ctx: BaseStepContext,
            prepared: PrepT | None,
            progress: ProgressStep | None,
    ) -> bool:
        result: StepResult = func(self, ctx, prepared, progress)

        if progress is not None:
            if result.ok:
                text = result.label or "OK"
                progress.set_status(f"Finished /   {text}")
            else:
                text = result.label or result.error_hint or "Fehler"
                progress.set_status(f"Failed   /   {text}")

        if not result.ok:
            _log_failure(
                self,
                ctx,
                func=func,
                cause=result.cause,
                details=result.details,
                label=result.label,
                error_hint=result.error_hint,
                with_block=True,
            )

        return result.ok

    return wrapper