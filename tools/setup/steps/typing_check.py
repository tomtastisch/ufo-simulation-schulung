# tools/setup/steps/typing_check.py
from __future__ import annotations

"""
Type annotation checker for src/task/* files.

Validates that student code has proper type annotations
to reinforce type annotation awareness (didactic focus).
"""

import ast
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


@dataclass(slots=True)
class TypeAnnotation:
    """
    Einzelner Befund zu einer fehlenden Typannotation.

    Attributes:
        file: Relative Dateipfad
        line: Zeilennummer
        name: Name des Elements (Parameter, Funktion, Variable)
        type: Art des Elements ("parameter", "return", "variable")
        has_annotation: Ob eine Annotation vorhanden ist
    """

    file: str
    line: int
    name: str
    type: str  # "parameter", "return", "variable"
    has_annotation: bool


class AnnotationChecker(ast.NodeVisitor):
    """
    AST-Visitor zur Prüfung von Typannotationen.

    Prüft:
    - Funktionsparameter
    - Return-Typannotationen
    - Variablen (nur im strict mode)
    """

    def __init__(self, mode: str, check_variables: bool) -> None:
        """
        Initialisiert den Checker.

        Args:
            mode: "strict" oder "relaxed"
            check_variables: Ob Variablen geprüft werden sollen
        """
        self.mode: str = mode
        self.check_variables: bool = check_variables
        self.findings: list[TypeAnnotation] = []
        self._current_file: str = ""

    def set_file(self, filepath: str) -> None:
        """Setzt den aktuellen Dateipfad für Findings."""
        self._current_file = filepath

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Prüft eine Funktionsdefinition.

        Checks:
        - Parameter-Annotationen (alle außer self/cls)
        - Return-Annotation (außer bei __init__)
        """
        # Parameter prüfen
        for arg in node.args.args:
            # self und cls überspringen
            if arg.arg in ("self", "cls"):
                continue

            if arg.annotation is None:
                self.findings.append(
                    TypeAnnotation(
                        file=self._current_file,
                        line=arg.lineno,
                        name=arg.arg,
                        type="parameter",
                        has_annotation=False,
                    )
                )

        # Return-Annotation prüfen (außer __init__)
        if node.returns is None and node.name != "__init__":
            self.findings.append(
                TypeAnnotation(
                    file=self._current_file,
                    line=node.lineno,
                    name=node.name,
                    type="return",
                    has_annotation=False,
                )
            )

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Variable mit Annotation - gut, nichts zu tun."""
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        Variable ohne Annotation.

        Nur im strict mode oder wenn check_variables=True wird dies gemeldet.
        """
        if self.check_variables or self.mode == "strict":
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.findings.append(
                        TypeAnnotation(
                            file=self._current_file,
                            line=node.lineno,
                            name=target.id,
                            type="variable",
                            has_annotation=False,
                        )
                    )
        self.generic_visit(node)


@dataclass(slots=True)
class TypingCheckStep(BaseStep[tuple[Path, ...]]):
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
    ) -> list[TypeAnnotation]:
        """
        Prüft eine einzelne Python-Datei mit AST.

        Args:
            path: Pfad zur Python-Datei
            mode: "strict" oder "relaxed"
            check_variables: Ob Variablen geprüft werden sollen

        Returns:
            Liste von Findings (fehlende Annotationen)
        """
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))

            checker = AnnotationChecker(mode=mode, check_variables=check_variables)
            checker.set_file(str(path.relative_to(Path.cwd())))
            checker.visit(tree)

            return checker.findings

        except SyntaxError as e:
            # Syntaxfehler überspringen - nicht Aufgabe des Typisierungs-Checks
            # (Syntaxfehler werden vom Python-Interpreter und pylint/flake8 gemeldet)
            # Logging für Debugging-Zwecke
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(
                f"Syntaxfehler in {path} ignoriert (Zeile {e.lineno}): {e.msg}"
            )
            return []

    @override
    @handle_prepare
    def prepare(self, ctx: BaseStepContext) -> PrepareResult[tuple[Path, ...]]:
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
        prepared: tuple[Path, ...] | None,
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

        # Alle Dateien prüfen
        all_findings: list[TypeAnnotation] = []
        for file_path in files:
            findings = self._check_file(
                path=file_path,
                mode=mode,
                check_variables=check_variables,
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
