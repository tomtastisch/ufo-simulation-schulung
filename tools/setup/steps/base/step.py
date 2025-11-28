# tools/setup/steps/base/step.py
from __future__ import annotations

import time
import traceback
from collections.abc import Sized
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Generic, Iterable, TypeVar, Mapping, Any

from tools.setup.steps.base.meta import BaseStepMeta, StepContext
from tools.setup.ui import CATALOG
from tools.setup.ui.progress import ProgressMode, ProgressStep
from tools.setup.ui.output.error import error

T = TypeVar("T")  # Typ des prepare()-Ergebnisses


@dataclass(slots=True)
class BaseStep(Generic[T], ABC, metaclass=BaseStepMeta):
    """
    Abstrakte Basis eines Setup-Schritts.

    Vereinheitlicht:
    - Vorbereitungsphase (prepare)
    - fachliche Ausführung (step)
    - zentralen Orchestrator (run)
    """

    # Instanzzustand
    mode: ProgressMode = ProgressMode.AUTO

    # Metadaten – Klassenattribute, NICHT Dataclass-Felder
    stid: ClassVar[str] = "generic"
    priority: ClassVar[int] = 0

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

    # ------------------------------------------------------------
    # Konfig-/Text-Helfer
    # ------------------------------------------------------------

    def options(self, ctx: StepContext) -> dict[str, object]:
        """
        Liefert Step-spezifische Optionen aus [tool.setup.options.<stid>].

        Beispiel-TOML:
            [tool.setup.options.tests]
            marker = "not slow"
            max-workers = 4
        """
        raw: Mapping[str, Any] | None = ctx.profile.step_options.get(self.stid)
        return dict(raw or {})

    def output(
            self,
            ctx: StepContext,
            *,
            field: str = "default",
            **extra: object,
    ) -> str:
        """
        Liefert einen formatierten Text aus setup_ui.toml mit Fallback.

        Für field="header":
            - texts.<StepName>.header
            - texts.step_default.header
            - Fallback: "Setup-{stid} {StepName}"

        Für andere Felder:
            - texts.<StepName>.<field>
            - texts.step_default.<field>
            - Fallback: "StepName: status – cause"
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

        if field == "header":
            fallback = f"Setup-{self.stid} {self.name}"
        else:
            fallback = f"{self.name}: {' – '.join(parts)}" if parts else self.name

        for block in (self.name, "step_default"):
            if text := CATALOG.format(block, field=field, default="", **placeholders):
                return text

        return fallback

    from collections.abc import Sized
    ...

    def estimate_total(self, prepared: T | None) -> int | None:
        """
        Liefert eine Schätzung der Anzahl Arbeitseinheiten für den Progress-Balken.
        Diese Methode dient der notwendigkeit bei Spezialfällen, wenn diese Semantik
        nicht passt (z.B. leere Collection soll trotzdem als 1 Einheit gelten).
        """
        if prepared is None:
            return None

        if isinstance(prepared, Sized):
            return len(prepared)

        # einzelnes, nicht-sized Objekt → eine logische Einheit
        return 1

    # noinspection PyMethodMayBeStatic
    def _ensure(
            self,
            ctx: StepContext,
            *,
            spec: str | None = None,
            cmd: Iterable[str] | None = None,
    ) -> bool:
        """
        Führe eine Installation über tools.setup.utils.install aus.

        Entweder:
            _ensure(ctx, spec="paket")
        oder:
            _ensure(ctx, cmd=("sh", "-c", "..."))
        """
        from tools.setup.utils import install  # Fassade

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

    # ------------------------------------------------------------
    # Template-Method
    # ------------------------------------------------------------

    def prepare(self, ctx: StepContext) -> T | None:
        """
        Optionaler Vorbereitungsschritt.

        Default: nichts vorbereiten – Subklassen überschreiben.
        """
        return None

    @abstractmethod
    def step(
            self,
            ctx: StepContext,
            prepared: T | None,
            progress: ProgressStep | None,
    ) -> bool:
        """
        Fachlicher Kern des Schritts.

        Rückgabe:
            True  → Step erfolgreich
            False → Step fehlgeschlagen
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------

    def run(self, ctx: StepContext) -> bool:
        prepared = self.prepare(ctx)

        header_text = self.output(ctx, field="header")
        if not header_text:
            header_text = f"Setup-{self.stid} {self.name}"

        with self.mode.make_context(header_text, ctx.console) as progress:
            # Total generisch aus prepared ableiten
            if progress is not None:
                total_hint = self.estimate_total(prepared)
                if total_hint is not None:
                    progress.set_total(total_hint)

            try:
                ok = self.step(ctx, prepared, progress)
            except BaseException as exc:
                exc_type_name = type(exc).__name__
                exc_message = str(exc) or repr(exc)
                tb_text = "".join(
                    traceback.format_exception(type(exc), exc, exc.__traceback__)
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

                # YAML-Fehlerblock bauen und auf Konsole schreiben
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

                if total and completed < total:
                    progress.advance(total - completed)  # type: ignore[arg-type]

                if ok:
                    progress.mark_finished()
                else:
                    progress.mark_failed()

            time.sleep(1.5)
            return ok
