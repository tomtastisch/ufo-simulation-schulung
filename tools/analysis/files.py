from __future__ import annotations

"""AST-basierte Analyse einzelner Python-Dateien."""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, TypedDict


class FileAnalysisResult(TypedDict, total=False):
    """Strukturiertes Analyseergebnis einer Python-Datei."""

    filepath: Path
    imports: List[str]
    from_imports: Dict[str, List[str]]
    used_names: Set[str]


@dataclass(slots=True)
class FileAnalyzer:
    """Analysiert Python-Dateien mit dem AST-Modul."""

    def analyze(self, path: Path) -> FileAnalysisResult:
        """Analysiert eine Datei und extrahiert Import- und Namensinformationen."""
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        imports: list[str] = []
        from_imports: dict[str, list[str]] = {}
        used_names: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                bucket = from_imports.setdefault(node.module, [])
                bucket.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)

        return FileAnalysisResult(
            filepath=path,
            imports=imports,
            from_imports=from_imports,
            used_names=used_names,
        )
