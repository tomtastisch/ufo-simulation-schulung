from __future__ import annotations

"""Einfacher Entry-Point für Import-Linting mit import-linter."""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from tools.ui import SetupConsole, StepProgress
from tools.ui.resources import TextCatalog

_TEXTS: Final[TextCatalog] = TextCatalog()
LINTER_CMD: Final[list[str]] = ["lint-imports"]


@dataclass(slots=True)
class AnalyzerResult:
    """Ergebnis eines Import-Linting-Laufs."""

    exit_code: int
    output: str


class ImportAnalyzer:
    """Führt Import-Linting basierend auf der Projektkonfiguration aus."""

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialisiert den Analyzer mit einem Projekt-Root."""
        self.project_root: Path = project_root or Path(__file__).resolve().parent.parent

    @staticmethod
    def _build_env_with_src(project_root: Path) -> dict[str, str]:
        """Erweitert PYTHONPATH um src/ und das Projekt-Root."""
        env = os.environ.copy()
        paths = [str(project_root)]
        src_dir = project_root / "src"
        if src_dir.exists():
            paths.append(str(src_dir))
        existing = env.get("PYTHONPATH", "")
        all_paths = paths + ([existing] if existing else [])
        env["PYTHONPATH"] = os.pathsep.join(all_paths)
        return env

    def _run_import_linter(self) -> AnalyzerResult:
        """Startet import-linter und gibt Exit-Code und Ausgabe zurück."""
        env = self._build_env_with_src(self.project_root)
        try:
            result = subprocess.run(
                LINTER_CMD,
                cwd=self.project_root,
                env=env,
                text=True,
                capture_output=True,
            )
        except FileNotFoundError as exc:
            output = f"import-linter konnte nicht gestartet werden: {exc}"
            return AnalyzerResult(exit_code=1, output=output)

        output = (result.stdout or "") + (result.stderr or "")
        return AnalyzerResult(exit_code=result.returncode, output=output)

    def analyze_all(self) -> AnalyzerResult:
        """Führt die Import-Analyse aus und gibt das Ergebnis zurück."""
        SetupConsole.header("UMFASSENDE IMPORT-ANALYSE")
        with StepProgress("import-linter ausführen", total=1) as sp:
            result = self._run_import_linter()
            sp.advance(1)
            if result.exit_code == 0:
                sp.mark_success()
            else:
                sp.mark_error()

        if result.exit_code == 0:
            SetupConsole.success("Alle Import-Contracts wurden eingehalten.")
        else:
            SetupConsole.error("Mindestens ein Import-Contract wurde verletzt.")
        return result


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    analyzer = ImportAnalyzer(root)
    result = analyzer.analyze_all()
    sys.exit(result.exit_code)
