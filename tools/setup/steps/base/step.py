# tools/setup/steps/base/step.py
from __future__ import annotations

import time
import traceback
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sized
from dataclasses import dataclass, field
from typing import Any, Generic, Mapping, TypeVar, ClassVar

from tools.setup.steps.base.meta import BaseStepMeta, BaseStepContext, BaseStepCore
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


    def estimate_total(self, prepared: T | None) -> int | None:
        """
        Dient als Progress-Hook zur Festlegung der Arbeitseinheiten
        für den Progress-Balken.
        """
        if prepared is None:
            return None

        return len(prepared) if isinstance(prepared, Sized) else 1


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
    def step(
            self,
            ctx: BaseStepContext,
            prepared: T | None,
            progress: ProgressStep | None,
    ) -> bool:
        """
        Fachlicher Kern des Arbeitsschritts.

        Rückgabe:
            True  → Step erfolgreich
            False → Step fehlgeschlagen
        """
        raise NotImplementedError

    def run(self, ctx: BaseStepContext) -> bool:
        """
        Orchestriert den Arbeitsschritt mithilfe der festgelegten Anzahl
        an Arbeitseinheiten, welche anhand von estimate_total festgelegt werden.

        Returns:
            True, wenn alle Durchläufe erfolgreich waren
            False, wenn mindestens ein Durchlauf fehlgeschlagen ist
        """

        self._error_block = None
        self._prepared = self.prepare(ctx)

        header_text = self.output(ctx, field="header") or f"Setup-{self.stid} {self.name}"

        with self.mode.make_context(header_text, ctx.console) as progress:
            if progress is not None:
                total_hint = self.estimate_total(self._prepared)

                if total_hint is not None:
                    progress.set_total(total_hint)

            try:
                ok = self.step(ctx, self._prepared, progress)

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
                    progress.mark_failed()

                block = error(
                    step=self.name,
                    stid=self.stid,
                    exc_type=exc_type_name,
                    message=exc_message,
                    traceback_text=tb_text,
                )
                ctx.console.error(block)

                ctx.log.write_error(
                    section=self.name,
                    message=msg,
                    details=tb_text,
                )
                return False

            if progress is not None:
                total = getattr(progress, "total", None)
                completed = getattr(progress, "completed", 0)

                if isinstance(total, int) and (delta := total - completed) > 0:
                    progress.advance(delta)

                (progress.mark_finished if ok else progress.mark_failed)()

            if not ok and self._error_block:
                ctx.console.error(self._error_block)

            # kurzes warten, damit der Status im UI aktualisiert wird
            time.sleep(0.5)

            return ok