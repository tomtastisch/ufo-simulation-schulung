# tools/setup/steps/typing_check/checker.py
from __future__ import annotations

"""
AST-basierter Type Annotation Checker.

Analysiert Python-Dateien und prüft auf fehlende Typannotationen.
"""

import ast

from .model import TypeAnnotation


class AnnotationChecker(ast.NodeVisitor):
    """
    AST-Visitor zur Prüfung von Typannotationen.

    Prüft:
    - Funktionsparameter (wenn check_params=True)
    - Return-Typannotationen (wenn check_returns=True)
    - Variablen (nur im strict mode oder wenn check_variables=True)
    """

    def __init__(
        self,
        mode: str,
        check_variables: bool,
        check_params: bool = True,
        check_returns: bool = True,
    ) -> None:
        """
        Initialisiert den Checker.

        Args:
            mode: "strict" oder "relaxed"
            check_variables: Ob Variablen geprüft werden sollen
            check_params: Ob Funktionsparameter geprüft werden sollen
            check_returns: Ob Return-Annotationen geprüft werden sollen
        """
        self.mode: str = mode
        self.check_variables: bool = check_variables
        self.check_params: bool = check_params
        self.check_returns: bool = check_returns
        self.findings: list[TypeAnnotation] = []
        self._current_file: str = ""

    def set_file(self, filepath: str) -> None:
        """Setzt den aktuellen Dateipfad für Findings."""
        self._current_file = filepath

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Prüft eine Funktionsdefinition.

        Checks:
        - Parameter-Annotationen (wenn check_params=True, alle außer self/cls)
        - Return-Annotation (wenn check_returns=True, außer bei __init__)
        """
        # Parameter prüfen (nur wenn aktiviert)
        if self.check_params:
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
                        )
                    )

        # Return-Annotation prüfen (nur wenn aktiviert, außer __init__)
        if self.check_returns and node.returns is None and node.name != "__init__":
            self.findings.append(
                TypeAnnotation(
                    file=self._current_file,
                    line=node.lineno,
                    name=node.name,
                    type="return",
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
                        )
                    )
        self.generic_visit(node)
