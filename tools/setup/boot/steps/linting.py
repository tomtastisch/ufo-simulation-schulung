from __future__ import annotations

"""Integration von import-linter in die Setup-Pipeline."""

from pathlib import Path

from tools.analysis.imports import ImportAnalyzer
from tools.common import ErrorLog
from tools.ui import SetupConsole


def run_import_analysis(log: ErrorLog) -> bool:
    """Führt die Import-Linter-Prüfung aus und protokolliert Verstöße."""
    SetupConsole.subheader("Import-Linter Prüfung")
    project_root = Path(__file__).resolve().parent.parent.parent
    analyzer = ImportAnalyzer(project_root)
    result = analyzer.analyze_all()

    if result.exit_code == 0:
        SetupConsole.success("Import-Linter meldet keine Contract-Verletzungen.")
        return True

    SetupConsole.error("Import-Linter hat Verstöße festgestellt.")
    SetupConsole.info("Bitte Ausgabe im Terminal oder in setup.log prüfen.")
    log.write_error(
        "Import-Linter",
        "Mindestens ein Contract wurde verletzt",
        result.output,
    )
    return False
