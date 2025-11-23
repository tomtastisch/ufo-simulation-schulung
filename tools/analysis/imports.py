from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Tuple


def run_import_linter(python_executable: str, project_root: Path) -> Tuple[bool, str]:
    """Führt Import-Linter im Kontext des angegebenen Python-Interpreters aus.

    Args:
        python_executable: Pfad zum Python-Interpreter (z. B. venv-Python).
        project_root: Wurzelverzeichnis des Projekts (Working-Directory).

    Returns:
        (ok, output):
            ok = True  -> Exit-Code 0, keine Contract-Verstöße.
            ok = False -> Contract-Verstoß oder technischer Fehler.
        output enthält stdout + stderr von Import-Linter.
    """
    try:
        # Wichtig: CLI-Modul verwenden, NICHT 'importlinter' direkt
        result = subprocess.run(
            [python_executable, "-m", "importlinter.cli"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        # Python selbst nicht gefunden (Konfigurationsfehler)
        return False, f"Python-Interpreter für Import-Linter nicht gefunden: {exc}"

    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output
