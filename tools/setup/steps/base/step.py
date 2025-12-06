# tools/setup/steps/base/step.py
from __future__ import annotations

import time
import traceback
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Generic, Mapping, TypeVar, ClassVar

from tools.setup.steps.base.decorator import handle_step
from tools.setup.steps.base.meta import BaseStepMeta, BaseStepContext, BaseStepCore
from tools.setup.steps.base.result import StepResult
from tools.setup.ui import CATALOG
from tools.setup.ui.output.error import error
from tools.setup.ui.progress import ProgressMode, ProgressStep

T = TypeVar("T")  # Typ des prepare()-Ergebnisses


@dataclass(slots=True)
class BaseStep(
    BaseStepCore,
    Generic[T],
    ABC,
    metaclass=BaseStepMeta,
):
    """
    Abstrakte Basis eines Setup-Schritts.

    Verantwortlichkeiten:
    - Konfiguration (options)
    - Textausgabe (output)
    - Vorbereitungsphase (prepare)
    - fachliche Ausführung (step)
    - zentrale Orchestrierung (run)
    """

    mode: ProgressMode = ProgressMode.AUTO
    stid: ClassVar[str] = "base"
    prio: ClassVar[int] = 0

    _error_block: str | None = field(default=None, init=False, repr=False)
    _prepared: T | None = field(default=None, init=False, repr=False)


    @property
    def name(self) -> str:
        return type(self).__name__


    @property
    def auto_install(self) -> bool:
        """
        Flag für automatische Installation in prepare().
        Default: False – Steps überschreiben bei Bedarf.
        Globale Voreinstellung kann über ctx.profile.auto_install interpretiert werden.
        """
        return False


    def options(self, ctx: BaseStepContext) -> dict[str, object]:
        """
        Liefert Step-spezifische Optionen aus [tool.setup.options.<stid>].
        """
        raw: Mapping[str, Any] | None = ctx.profile.step_options.get(self.stid)
        return dict(raw or {})

    @staticmethod
    def _iter_units(prepared: T | None) -> Iterable[Any]:
        """
        Standard-Implementierung:
        - kein prepared → keine Units
        - sonst genau EINE Unit = der gesamte Payload

        Steps, die mehrere Arbeitseinheiten haben (Contracts, Dependencies,
        Test-Suites, ...), überschreiben diese Methode und liefern eine
        Sequenz von „Units“.
        """
        return () if prepared is None else (prepared,)

    def estimate_total(self, prepared: T | None) -> int | None:
        """
        Standard: Anzahl Units als Progress-Gesamtlänge, falls zählbar.
        Spezielle Steps können das überschreiben (z. B. Gewichtung).
        """
        units = list(self._iter_units(prepared))
        return len(units) if units else 1


    def output(
            self,
            ctx: BaseStepContext,
            *,
            field: str = "default",
            **extra: object,
    ) -> str:
        """
        Liefert einen formatierten Text aus setup_ui.toml mit Fallback.
        """
        placeholders: dict[str, object] = {
            "step": self.name,
            "env": ctx.config.platform.name,
            "type": self.stid,
            "module": self.name,
            **extra,
        }

        status = str(extra.get("status", "")).strip()
        cause = str(extra.get("cause", "")).strip()
        parts = [p for p in (status, cause) if p]

        fallback: str = (
            f"Setup-{self.stid} {self.name}"
            if field == "header" else
            f"{self.name}: {' – '.join(parts)}" if parts else self.name
        )

        for block in (self.name, "step_default"):
            if text := CATALOG.format(block, field=field, default="", **placeholders):
                return text

        return fallback


    # noinspection PyMethodMayBeStatic
    def _ensure(
            self,
            ctx: BaseStepContext,
            *,
            spec: str | None = None,
            cmd: Iterable[str] | None = None,
    ) -> bool:
        """
        Führe eine Installation über tools.setup.utils.install aus.
        """
        from tools.setup.utils import install  # Lazy import
        assert (spec is not None) ^ (cmd is not None)

        kwargs: dict[str, object] = {"cmd": cmd} if cmd else {
            "python": str(ctx.config.venv_python),
            "spec": spec,
        }

        rc, *_ = install(
            cwd=ctx.config.repo_root,
            **kwargs,
        )

        return rc == 0


    def prepare(self, ctx: BaseStepContext) -> T | None:
        """Optionaler Vorbereitungsschritt, wenn Arbeitsschritt dies erfordert."""
        return None


    @abstractmethod
    def _step_impl(
            self,
            ctx: BaseStepContext,
            prepared: T | None,
            progress: ProgressStep | None,
    ) -> StepResult:
        """Fachlicher Kern des Arbeitsschritts."""
        raise NotImplementedError


    def step(
            self,
            ctx: BaseStepContext,
            prepared: T | None,
            progress: ProgressStep | None,
    ) -> bool:
        impl = type(self)._step_impl
        wrapped = handle_step(impl)  # type: ignore[misc]
        return wrapped(self, ctx, prepared, progress)


    def run(self, ctx: BaseStepContext) -> bool:
        """
        Orchestriert den Arbeitsschritt.

        Ablauf:
        1. prepare(...) liefert Payload
        2. iter_units(...) wandelt Payload in „Units“ um
        3. Progress-Gesamtlänge aus estimate_total(...) / Units
        4. Für jede Unit genau ein step(...)-Aufruf
        """
        self._error_block = None
        self._prepared = self.prepare(ctx)

        # Units aus prepared ableiten (1D/2D egal – die Step-Klasse definiert das)
        units = list(self._iter_units(self._prepared))
        has_units = bool(units)

        header_text = self.output(ctx, field="header") or f"Setup-{self.stid} {self.name}"

        with self.mode.make_context(header_text, ctx.console) as progress:
            if progress is not None:
                total_hint = self.estimate_total(self._prepared)
                if total_hint is None:
                    # Fallback: Anzahl Units, wenn vorhanden
                    total_hint = len(units) if has_units else None

                if isinstance(total_hint, int):
                    progress.set_total(total_hint)

            ok = True

            try:
                if not has_units:
                    ok = self.step(ctx, None, progress)
                else:
                    for unit in units:
                        if not self.step(ctx, unit, progress):
                            ok = False
                            break

            except BaseException as exc:
                exc_type_name = type(exc).__name__
                exc_message = str(exc) or repr(exc)
                tb_text = "".join(
                    traceback.format_exception(type(exc), exc, exc.__traceback__),
                )

                msg = self.output(
                    ctx,
                    field="failure",
                    cause=exc_type_name,
                    details=exc_message,
                )

                if progress is not None:
                    progress.set_status(msg)
                    # keine Entscheidung über „fertig“, nur Status setzen

                block = error(
                    step=self.name,
                    stid=self.stid,
                    exc_type=exc_type_name,
                    message=exc_message,
                    traceback_text=tb_text,
                )
                self._error_block = block
                ctx.console.error(block)

                ctx.log.write_error(
                    section=self.name,
                    message=msg,
                    details=tb_text,
                )

                ok = False  # wichtig: nur Flag setzen, kein return

            if progress is not None:
                total = getattr(progress, "total", None)
                completed = getattr(progress, "completed", 0)

                # Nur bei Erfolg auf 100 % ziehen:
                if ok and isinstance(total, int) and (delta := total - completed) > 0:
                    progress.advance(delta)

                if ok:
                    progress.mark_finished()
                else:
                    progress.mark_failed()

            if not ok and self._error_block:
                ctx.console.error(self._error_block)

            time.sleep(0.5)
            return ok