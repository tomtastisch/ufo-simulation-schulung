# tools/setup/steps/typing_check/__init__.py
from __future__ import annotations

"""
Type annotation checker for src/task/* files.

Validates that student code has proper type annotations
to reinforce type annotation awareness (didactic focus).
"""

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
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

from .checker import AnnotationChecker
from .model import TypeAnnotation

# Type alias for improved readability
type TaskFilePaths = tuple[Path, ...]


@dataclass(slots=True)
class TypingCheckStep(BaseStep[TaskFilePaths]):
    """
    Prüft Typannotationen in src/task/*.

    Konfigurierbar über [tool.setup.options.typing_check]:
    - mode: "strict" | "relaxed"
    - check_params: bool
    - check_returns: bool
    - check_variables: bool
    """

    stid: ClassVar[str] = "typing_check"
    prio: ClassVar[int] = 100  # nach deps, vor import_linter

    def _check_file(
        self,
        path: Path,
        mode: str,
        check_variables: bool,
        check_params: bool = True,
        check_returns: bool = True,
    ) -> list[TypeAnnotation]:
        """
        Prüft eine einzelne Python-Datei mit AST.

        Args:
            path: Pfad zur Python-Datei
            mode: "strict" oder "relaxed"
            check_variables: Ob Variablen geprüft werden sollen
            check_params: Ob Funktionsparameter geprüft werden sollen
            check_returns: Ob Return-Annotationen geprüft werden sollen

        Returns:
            Liste von Findings (fehlende Annotationen)
        """
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))

            checker = AnnotationChecker(
                mode=mode,
                check_variables=check_variables,
                check_params=check_params,
                check_returns=check_returns,
            )
            checker.set_file(str(path.relative_to(Path.cwd())))
            checker.visit(tree)

            return checker.findings

        except SyntaxError as e:
            # Syntaxfehler überspringen - nicht Aufgabe des Typisierungs-Checks
            # (Syntaxfehler werden vom Python-Interpreter und pylint/flake8 gemeldet)
            # Logging für Debugging-Zwecke
            logger = logging.getLogger(__name__)
            logger.debug(
                f"Syntaxfehler in {path} ignoriert (Zeile {e.lineno}): {e.msg}"
            )
            return []

    @override
    @handle_prepare
    def prepare(self, ctx: BaseStepContext) -> PrepareResult[TaskFilePaths]:
        """
        Findet alle Python-Dateien in src/task/*.

        Returns:
            PrepareResult mit Tuple von Dateipfaden oder None wenn Verzeichnis fehlt.
        """
        task_dir = ctx.config.repo_root / "src" / "task"
        if not task_dir.exists():
            return PrepareResult(
                ok=True,
                payload=tuple(),  # leeres Tuple → wird als "keine Files" behandelt
            )

        # Alle .py-Dateien sammeln, aber __init__.py ignorieren
        files = [
            p
            for p in task_dir.rglob("*.py")
            if p.name != "__init__.py"
        ]

        return PrepareResult(ok=True, payload=tuple(files))

    @override
    def _step_impl(
        self,
        ctx: BaseStepContext,
        prepared: TaskFilePaths | None,
        progress: ProgressStep | None,
    ) -> StepResult:
        """
        Prüft jede Datei und meldet Findings.

        Returns:
            StepResult mit Erfolg/Fehler und Details zu fehlenden Annotationen.
        """
        files = prepared or tuple()

        # Falls keine Dateien vorhanden (src/task/ fehlt oder leer)
        if not files:
            no_files_msg = CATALOG.text(
                "typing_check",
                field="no_files",
                default="Verzeichnis src/task/ nicht gefunden (übersprungen)",
            )
            return StepResult.success(
                label=no_files_msg,
                details="Keine Python-Dateien in src/task/ gefunden",
            )

        # Optionen aus Konfiguration lesen
        options = self.options(ctx)
        mode: str = str(options.get("mode", "relaxed"))
        check_variables: bool = bool(options.get("check_variables", False))
        check_params: bool = bool(options.get("check_params", True))
        check_returns: bool = bool(options.get("check_returns", True))

        # Alle Dateien prüfen
        all_findings: list[TypeAnnotation] = []
        for file_path in files:
            findings = self._check_file(
                path=file_path,
                mode=mode,
                check_variables=check_variables,
                check_params=check_params,
                check_returns=check_returns,
            )
            all_findings.extend(findings)

            if progress is not None:
                progress.advance(1)

        # Ergebnis auswerten
        if not all_findings:
            success_msg = CATALOG.text(
                "typing_check",
                field="success",
                default="Alle Dateien in src/task/* haben vollständige Typannotationen",
            )
            return StepResult.success(
                label=success_msg,
                details=f"{len(files)} Dateien geprüft, keine fehlenden Annotationen",
            )

        # Fehlende Annotationen gefunden → Details aufbereiten
        details_lines: list[str] = []
        current_file = ""

        for finding in sorted(all_findings, key=lambda f: (f.file, f.line)):
            if finding.file != current_file:
                current_file = finding.file
                details_lines.append(f"\n{current_file}:")

            # Passende Nachricht aus Katalog holen
            field_name = f"missing_{finding.type}"
            msg = CATALOG.format(
                "typing_check",
                field=field_name,
                default=f"  Zeile {finding.line}: {finding.name} ({finding.type})",
                line=finding.line,
                name=finding.name,
            )
            details_lines.append(msg)

        details_text = "\n".join(details_lines)

        # Hint-Text anfügen
        hint = CATALOG.text("typing_check", field="hint", default="")
        if hint:
            details_text += f"\n\n{hint}"

        # Bei relaxed mode: Warnung statt Fehler
        if mode == "relaxed":
            warning_msg = CATALOG.format(
                "typing_check",
                field="warning",
                default="Fehlende Annotationen gefunden",
                file=f"{len(set(f.file for f in all_findings))} Dateien",
            )
            return StepResult.success(
                label=warning_msg,
                details=details_text,
            )

        # Strict mode: Fehler
        failure_msg = CATALOG.format(
            "typing_check",
            field="failure",
            default="Typannotationen-Check fehlgeschlagen",
            cause=f"{len(all_findings)} fehlende Annotationen",
        )
        return StepResult.failure(
            cause="missing_annotations",
            label=failure_msg,
            details=details_text,
        )


__all__ = ["TypingCheckStep", "TypeAnnotation", "AnnotationChecker"]
