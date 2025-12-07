# tools/setup/steps/linter_check.py
from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar, override

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
from tools.setup.utils.ui_text import initial_running_text, running_text

logger = logging.getLogger(__name__)

@dataclass(slots=True)
class EvaluateImportsStep(BaseStep[tuple[str, ...]]):
    """
    Setup-Schritt zum Ausführen von import-linter (Import-Regelprüfung).
    """

    stid: ClassVar[str] = "import_linter"
    prio: ClassVar[int] = 40

    @override
    @property
    def auto_install(self) -> bool:
        """import-linter darf bei Bedarf automatisch nachinstalliert werden."""
        return True

    def _prepare_error(
            self,
            default_msg: str,
            *,
            exc_info: str | None,
            output: str,
    ) -> PrepareResult[tuple[str, ...]]:
        """
        Gemeinsame Fehlererzeugung für die Prepare-Phase:
        - klassifiziert Fehler (install / probe)
        - erzeugt ein einheitliches PrepareResult
        """
        cause, details = module.classify(
            exc_info=exc_info,
            output=output,
            module="importlinter",
        )
        text = details or output or default_msg
        return PrepareResult(
            ok=False,
            cause=cause,
            details=text,
            error_hint=text,
            payload=None,
        )

    @staticmethod
    def _select_contracts(
            raw: Any,
            mode: str,
    ) -> tuple[str, ...]:
        """
        Filterschicht für Contracts:
        - liest aus der rohen Config-Liste
        - filtert nach type (forbidden / layers / all)
        - gibt eine nicht-leere Tuple-Liste zurück
        """
        if not isinstance(raw, list):
            return ("Konfigurationsprüfung",)

        def type_matches(item: Mapping[str, object]) -> bool:
            # Typ des Contracts; leer = „egal“ (nur bei mode == "all" relevant)
            ctype = str(item.get("type", "")).strip().lower()
            if mode == "forbidden":
                return ctype == "forbidden"
            if mode == "layers":
                return ctype == "layers"
            return True  # "all"

        names = [
            name
            for item in raw
            if isinstance(item, Mapping)
            if type_matches(item)
            if (name := str(item.get("name", "")).strip())
        ]

        # Fallback: mindestens eine „logische“ Einheit anzeigen
        return tuple(names) or ("Konfigurationsprüfung",)


    @override
    @handle_prepare
    def prepare(self, ctx: BaseStepContext) -> PrepareResult[tuple[str, ...]] | PrepareResult:
        """
        Prepare-Ablauf:
        1. importlinter.cli probeweise aufrufen
        2. ggf. Auto-Installation versuchen
        3. aus Profil die relevante Contract-Liste ermitteln
        """
        python = str(ctx.config.venv_python)
        cwd = ctx.config.repo_root

        def probe() -> tuple[bool, str, str | None]:
            """Einmaliger Probelauf von importlinter.cli (--help) im venv."""
            return module.evaluate(
                python=python,
                module="importlinter.cli",
                cwd=cwd,
                extra_args=("--help",),
            )

        # 1. erster Probeaufruf
        ok, output, exc_info = probe()

        # 2. Auto-Installation, falls erlaubt und erforderlich
        if self.auto_install and not ok:
            rc, raw_install, _ = module.install(
                python=python,
                spec="import-linter",
                cwd=cwd,
            )
            if rc != 0:
                # Installation fehlgeschlagen → als Prepare-Fehler melden
                return self._prepare_error(
                    "import-linter Installation fehlgeschlagen",
                    exc_info=None,
                    output=raw_install,
                )

            # nach erfolgreicher Installation erneut probieren
            ok, output, exc_info = probe()

        # 3. Probe nach evtl. Installation immer noch nicht ok → harter Fehler
        if not ok:
            return self._prepare_error(
                "import-linter Probe fehlgeschlagen",
                exc_info=exc_info,
                output=output,
            )

        # 4. Contract-Liste aus Profil ableiten
        contracts_raw: Any = ctx.profile.get_path(
            "tool",
            "importlinter",
            "contracts",
            default=[],
        )
        contracts = self._select_contracts(
            raw=contracts_raw,
            mode=ctx.profile.linter_contracts,
        )

        return PrepareResult(ok=True, payload=contracts)

    @override
    def _step_impl(
            self,
            ctx: BaseStepContext,
            prepared: tuple[str, ...] | None,
            progress: ProgressStep | None,
    ) -> StepResult:
        tests = prepared or (None,)

        tests_done_label = CATALOG.format(
            "RunTestsStep",
            field="tests_done",
            default="Alle Prüfungen erfolgreich.",
        )
        tests_failed_label = CATALOG.format(
            "RunTestsStep",
            field="tests_failed",
            default="Tests fehlgeschlagen – Details siehe Log.",
        )

        def make_result(ok: bool, cause: str, details: str) -> StepResult:
            text = details or "keine Ausgabe"
            return StepResult(
                ok=ok,
                cause="" if ok else (cause or "tests_failed"),
                details=text,
                label=tests_done_label if ok else tests_failed_label,
                error_hint="" if ok else text,
            )

        def update_progress(index: int, total: int, nodeid: str | None) -> None:
            if progress is None:
                return
            test_details = CATALOG.format(
                "RunTestsStep",
                field="test_details",
                default="Test {index}/{total}: {test}",
                index=index,
                total=total,
                test=nodeid or "<alle>",
            )
            progress.set_status(running_text(test_details))

        total = len(tests)
        if progress is not None:
            progress.set_status(initial_running_text())
        last_details = ""

        for index, nodeid in enumerate(tests, start=1):
            update_progress(index, total, nodeid)

            ok, cause, details = run_single(
                python=str(ctx.config.venv_python),
                cwd=ctx.config.repo_root,
                logger=logger,
            )
            last_details = details

            if progress is not None:
                progress.advance(1)

            if not ok:
                return make_result(False, cause, last_details)

        return make_result(True, "", last_details)
