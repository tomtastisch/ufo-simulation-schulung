from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import ClassVar, override

from tools.setup.steps.base import (
    BaseStep,
    BaseStepContext,
    StepResult,
    PrepareResult,
    handle_prepare,
)
from tools.setup.steps.executer import (
    BatchExecutor,
    ChainedMap,
    TaskState,
    build_task_list,
    count_completed,
    get_last_completed_record,
    has_failures,
)
from tools.setup.ui.progress import ProgressStep
from tools.setup.utils import module
from tools.setup.utils.runner import run_single
from tools.setup.utils.task_naming import build_task_id, build_display_name
from tools.setup.utils.ui_text import initial_running_text, running_text

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
# Hinweis zur Unterscheidung "Dir" vs. "Package":
# - "Dir": Ein normales Verzeichnis ohne __init__.py.
# - "Package": Ein Verzeichnis mit __init__.py, wird von pytest ab Version >= 7.0 als "Package" angezeigt.
# Für die Test-Sammlung werden beide Typen ("Dir" und "Package") identisch behandelt,
# da sie jeweils einen Verzeichnis-Knoten in der Test-Hierarchie darstellen.
# Die Regex erfasst daher beide Fälle unter dem gemeinsamen Gruppennamen "kind".
_COLLECT_LINE_RE = re.compile(
    r"^(?P<indent>\s*)<(?P<kind>Dir|Package|Module|Class|Function) (?P<name>[^>]+)>"
)


# ============================================================
# Domänen-Objekte für Test-Ausführung
# ============================================================


@dataclass(frozen=True)
class TestFile:
    """
    Repräsentiert eine Test-Datei mit allen darin enthaltenen Tests.

    Attribute:
        file_relpath: Relativer Pfad zur Test-Datei (z.B. "tests/core/test_foo.py")
        qualified_names: Liste von Test-Namen in dieser Datei
            (z.B. ["TestClass::test_method", "test_function"])
    """

    file_relpath: str
    qualified_names: list[str]


@dataclass(frozen=True)
class TestFileResult:
    """Ergebnis eines Test-Datei-Laufs."""

    file_relpath: str
    ok: bool
    cause: str | None
    details: str


# ============================================================
# RunTestsStep mit generischem BatchExecutor
# ============================================================


@dataclass(slots=True)
class RunTestsStep(BaseStep[tuple[tuple[str, str], ...]]):
    """
    Setup-Schritt zum Ausführen der Test-Suite via pytest.

    Nutzt den generischen BatchExecutor für parallele Test-Ausführung
    mit Snapshot-basierter Progress-Anzeige.

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
        """
        Liefert die Anzahl der auszuführenden Test-DATEIEN (nicht Tests!).

        Dies ist kritisch für korrekte Fortschrittsberechnung:
        - Jede Datei = 1 Task
        - Fortschritt erhöht sich pro abgeschlossener Datei
        """
        if not prepared:
            return 1  # Fallback: Gesamtlauf

        # Gruppiere nach Dateien → Anzahl eindeutiger Dateien
        files = {file_relpath for file_relpath, _ in prepared}
        return len(files)

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

                # Verzeichnisse vor dem Module-Eintrag (inkl. Packages)
                dir_parts = [
                    n
                    for k, n, _ in stack[:module_index]
                    if k in ("Dir", "Package")
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

            # Für Dir / Package / Module / Class: Node in den Stack pushen
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
        """
        Führt Tests mit generischem BatchExecutor + Snapshot-Polling aus.

        Ablauf:
        1. Gruppiere Tests nach Dateien
        2. Erstelle TestFile-Objekte
        3. Baue Task-Liste via build_task_list()
        4. Seede ChainedMap
        5. Starte BatchExecutor in Thread
        6. Snapshot-Polling-Schleife mit UI-Updates
        7. Fehlerbehandlung via Snapshots
        """
        python = str(ctx.config.venv_python)
        cwd = ctx.config.repo_root
        max_workers = getattr(ctx.config, "tests_max_workers", 4) or 4

        tests: tuple[tuple[str, str], ...] = prepared or tuple()

        # Labels aus Catalog über BaseStep.output
        tests_done_label = self.output(ctx, field="tests_done") or "Alle Tests erfolgreich."
        tests_failed_label = self.output(ctx, field="tests_failed") or "Tests fehlgeschlagen – Details siehe Log."

        def make_result(ok: bool, cause: str | None, details: str, label: str | None = None) -> StepResult:
            """Erstellt StepResult mit korrektem Label aus CATALOG."""
            result_label = label if label else (tests_done_label if ok else tests_failed_label)

            if ok:
                return StepResult.success(label=result_label, details=details)
            return StepResult.failure(
                cause=cause or "tests_failed",
                details=details,
                label=result_label,
            )

        # Fall 1: Keine Tests → Gesamtlauf
        if not tests:
            if progress:
                progress.set_status("Running / –")

            ok, cause, details = run_single(
                python=python,
                cwd=cwd,
                nodeid=None,
                logger=logger,
            )
            return make_result(ok, cause, details or "")

        # ========================================
        # Fall 2: Parallele Ausführung via BatchExecutor
        # ========================================

        # 1. Gruppiere Tests nach Dateien
        file_to_tests: dict[str, list[str]] = {}
        for file_relpath, qualified_name in tests:
            if file_relpath not in file_to_tests:
                file_to_tests[file_relpath] = []
            file_to_tests[file_relpath].append(qualified_name)

        # 2. Erstelle TestFile-Objekte
        test_files: list[TestFile] = [
            TestFile(file_relpath=fpath, qualified_names=qnames)
            for fpath, qnames in file_to_tests.items()
        ]

        # 3. Erstelle Wrapper-Callable mit gebundenen Parametern
        from functools import partial

        def _run_test_file(
                test_file: TestFile,
                *,
                python: str,
                cwd_str: str,
        ) -> TestFileResult:
            ok, cause, details = run_single(
                python=python,
                cwd=cwd,
                nodeid=test_file.file_relpath,
                logger=None,
            )
            return TestFileResult(
                file_relpath=test_file.file_relpath,
                ok=bool(ok),
                cause=str(cause or ""),
                details=str(details or ""),
            )

        run_test_file_bound = partial(
            _run_test_file,
            python=python,
            cwd_str=str(cwd),
        )

        # 4. Baue Task-Liste
        tasks = build_task_list(
            objects=test_files,
            call=run_test_file_bound,
            id_builder=build_task_id,
            name_builder=build_display_name,
        )

        if logger:
            logger.debug(
                f"RunTestsStep: {len(tasks)} Test-Dateien, "
                f"{len(tests)} Tests, {max_workers} Worker"
            )

        # 5. ChainedMap seeden
        chained_map: ChainedMap[TestFileResult] = ChainedMap()
        chained_map.seed([(t.task_id, t.display_name) for t in tasks])

        # 6. Initialzustand der Progress-Bar: strikt gemäß Vorgabe
        if progress:
            progress.set_status(initial_running_text())

        # 7. Starte BatchExecutor in separatem Thread
        import threading

        def run_executor():
            executor = BatchExecutor(
                tasks=tasks,
                chained_map=chained_map,
                max_workers=max_workers,
                logger=logger,
            )
            executor.execute()

        executor_thread = threading.Thread(target=run_executor, daemon=True)
        executor_thread.start()

        # ========================================
        # 8. Snapshot-Polling-Schleife
        # ========================================

        snapshot_id = 0
        timeout = time.time() + 300.0  # Max. 5 Minuten
        completed_prev = 0

        while time.time() < timeout:
            # Hole nächsten Snapshot
            next_snap = chained_map.get_next(snapshot_id)

            if next_snap is None:
                # Kein neuer Snapshot → prüfe ob fertig
                latest = chained_map.get_latest()
                if count_completed(latest) == len(tasks):
                    # Alle Tasks abgeschlossen → fertig
                    break
                # Noch nicht fertig → kurz warten
                time.sleep(0.05)
                continue

            # Neuer Snapshot verfügbar
            snapshot_id = next_snap.snapshot_id

            # Nur Abschlussereignisse beeinflussen die UI (Fortschritt + Text)
            last_rec = get_last_completed_record(next_snap)
            if last_rec:
                completed_now = count_completed(next_snap)
                if progress:
                    delta = max(0, completed_now - completed_prev)
                    if delta:
                        progress.advance(delta)
                    progress.set_status(running_text(last_rec.display_name))
                completed_prev = completed_now

            # Fehler-Check: Sobald ein Task FAILED ist, abbrechen
            if has_failures(next_snap):
                # Finde ersten FAILED-Task
                failed_rec = next(
                    (r for r in next_snap.records.values() if r.task_state == TaskState.FAILED),
                    None,
                )

                # Optionaler Status-Text in gefordertem Stil
                if progress and failed_rec:
                    progress.set_status(running_text(failed_rec.display_name))

                # Erzeuge Fehlermeldung aus error-Text
                cause_text = (failed_rec.error or "test_failed") if failed_rec else "test_failed"
                details_msg = cause_text if isinstance(cause_text, str) else str(cause_text)
                return make_result(
                    False,
                    "test_failed",
                    details_msg,
                )

        # 9. Executor-Thread beenden
        executor_thread.join(timeout=5.0)

        # 10. Zusammenfassung
        final_snapshot = chained_map.get_latest()
        all_ok = not has_failures(final_snapshot)

        if all_ok:
            details_msg = (
                f"{len(tasks)} Dateien erfolgreich getestet ({len(tests)} Tests)"
            )
        else:
            # Sollte hier nicht ankommen (Fehler wird oben abgefangen)
            details_msg = "Unerwarteter Fehler"

        # Label kommt direkt aus CATALOG via make_result()
        return make_result(all_ok, None, details_msg)
