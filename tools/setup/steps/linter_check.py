# tools/setup/steps/linter_check.py
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, override

from tools.setup.steps.base import BaseStep, BaseStepContext
from tools.setup.ui import CATALOG
from tools.setup.ui.progress import ProgressStep
from tools.setup.utils import module


@dataclass(slots=True)
class EvaluateImportsStep(BaseStep[tuple[str, ...]]):
    """
    Setup-Schritt zum Ausführen von import-linter (Import-Regelprüfung).

    Design:
    - prepare()
        * prüft, ob importlinter.cli aufrufbar ist (Probe).
        * versucht bei Bedarf Auto-Installation.
        * liest Contracts aus dem bereits geladenen PyProjectProfile und gibt
          die Contract-Namen als Arbeitseinheiten zurück, gefiltert nach
          [tool.setup.linter].contracts.
    - estimate_total()
        * leitet die Progress-Balkenlänge aus der Anzahl Contracts ab.
    - step()
        * führt import-linter pro Contract logisch als eigene Einheit aus und
          aktualisiert den Fortschritt/Status entsprechend.
    """

    stid = "import_linter"
    priority = 40

    @override
    @property
    def auto_install(self) -> bool:
        """import-linter darf bei Bedarf automatisch nachinstalliert werden."""
        return True

    # -------------------------------------------------------------
    # Hilfsfunktionen
    # -------------------------------------------------------------
    def _collect_contracts(self, ctx: BaseStepContext) -> tuple[str, ...]:
        """
        Versucht, Contract-Namen aus dem bereits geladenen PyProjectProfile
        zu extrahieren und anhand von [tool.setup.linter].contracts zu filtern.

        Erwartete (vereinfachte) Struktur in pyproject.toml:

            [tool.importlinter]
            root_package = "..."

            [[tool.importlinter.contracts]]
            name = "Contract 1"
            type = "forbidden" | "layers" | ...

        Rückgabe:
            Tuple aller gefundenen Contract-Namen nach Filterung.
            Fallback: leeres Tuple, falls nichts gefunden werden kann.
        """
        contracts_raw: Any = ctx.profile.get_path(
            "tool",
            "importlinter",
            "contracts",
            default=[],
        )
        if not isinstance(contracts_raw, list):
            return ()

        mode = ctx.profile.linter_contracts  # "all" | "forbidden" | "layers"
        names: list[str] = []

        for item in contracts_raw:
            if not isinstance(item, Mapping):
                continue

            type_value = str(item.get("type", "")).strip().lower()

            if mode == "forbidden" and type_value != "forbidden":
                continue
            if mode == "layers" and type_value != "layers":
                continue
            # mode == "all" → kein Filter auf type

            name = item.get("name")
            if isinstance(name, str):
                stripped = name.strip()
                if stripped:
                    names.append(stripped)

        return tuple(names)

    @override
    def prepare(self, ctx: BaseStepContext) -> tuple[str, ...]:
        """
        Prüft importlinter.cli, versucht ggf. Auto-Installation und liefert
        die Contract-Namen als Arbeitseinheiten.
        """
        python = str(ctx.config.venv_python)
        cwd = ctx.config.repo_root

        def probe() -> tuple[bool, str, str | None]:
            return module.evaluate(
                python=python,
                module="importlinter.cli",
                cwd=cwd,
                extra_args=("--help",),
            )

        def fail(prefix: str, exc_info: str | None, output: str) -> None:
            cause, details = module.classify(
                exc_info=exc_info,
                output=output,
                module="importlinter",
            )
            text = details or output or ""
            msg = self.output(ctx, field="failure", cause=cause, details=text)
            ctx.log.write_error(section=self.name, message=msg, details=text)
            raise RuntimeError(f"{prefix}: {cause}: {details}")

        # 1. Probe
        ok, output, exc_info = probe()

        # 2. Optional: Auto-Installation + erneute Probe
        if self.auto_install and not ok:
            rc, raw_install, _short_install = module.install(
                python=python,
                spec="import-linter",
                cwd=cwd,
            )
            ok_install = rc == 0
            if not ok_install:
                fail(
                    "import-linter konnte nicht installiert werden",
                    exc_info=None,
                    output=raw_install,
                )

            ok, output, exc_info = probe()

        # 3. Finale Prüfung
        if not ok:
            fail(
                "import-linter Probe fehlgeschlagen",
                exc_info=exc_info,
                output=output,
            )

        # Contracts kommen jetzt ausschließlich aus dem bereits geladenen Profil
        return self._collect_contracts(ctx)

    @override
    def estimate_total(self, prepared: tuple[str, ...] | None) -> int | None:
        if prepared:
            return len(prepared)

        return 1

    @override
    def step(
            self,
            ctx: BaseStepContext,
            prepared: tuple[str, ...] | None,
            progress: ProgressStep | None,
    ) -> bool:

        python = str(ctx.config.venv_python)
        cwd = ctx.config.repo_root

        contracts = prepared or tuple()
        if not contracts:
            # Fallback: eine logische Einheit, z. B. "Gesamtkonfiguration"
            contracts = ("Konfigurationsprüfung",)

        total = len(contracts)

        ok_overall = True
        cause = ""
        details = ""
        last_output = ""

        for index, contract in enumerate(contracts, start=1):
            if progress is not None:
                contract_details = CATALOG.format(
                    "ImportLinterStep",
                    field="import_details",
                    default="Contract {index}/{total}: {contract}",
                    index=index,
                    total=total,
                    contract=contract,
                )
                running = CATALOG.format(
                    "step_default",
                    field="progress_running",
                    default="Running  /   {details}",
                    details=contract_details,
                )
                progress.set_status(running)

            # Technisch wird hier die gesamte Konfiguration geprüft – die
            # Contract-Namen dienen primär der Visualisierung.
            ok, output, exc_info = module.evaluate(
                python=python,
                module="importlinter.cli",
                cwd=cwd,
                extra_args=(),
            )
            last_output = output or ""

            if not ok:
                kind, det = module.classify(
                    exc_info=exc_info,
                    output=output,
                    module="importlinter",
                )
                ok_overall = False
                cause = kind
                details = det or output or "keine Ausgabe"

            if progress is not None:
                progress.advance(1)

            if not ok:
                break

        msg = self.output(
            ctx,
            field="success" if ok_overall else "failure",
            cause=cause,
            details=details or last_output or "",
        )

        if progress is not None:
            field = "import_done" if ok_overall else "import_failed"
            default_details = (
                "Alle Import-Regeln eingehalten."
                if ok_overall
                else "Import-Regeln verletzt – Details siehe Log."
            )
            details_text = CATALOG.format(
                "ImportLinterStep",
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
