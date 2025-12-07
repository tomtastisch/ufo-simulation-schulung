# tools/setup/utils/interpreter_worker.py
from __future__ import annotations

import sys
from pathlib import Path

from tools.setup.domain import BootstrapConfig


class InterpreterWorker:
    """Ermittelt den passenden Python‑Interpreter und baut Pip‑Befehle."""

    def __init__(self, config: BootstrapConfig) -> None:
        self.config = config

    def has_venv(self) -> bool:
        """Prüft, ob .venv überhaupt existiert."""
        return Path(self.config.venv_dir).exists()

    def python_executable(self) -> str:
        """Gibt die zu verwendende Python‑Binary zurück."""
        if self.has_venv():
            return str(self.config.venv_python)

        return sys.executable  # laufender Interpreter, vgl. Codango‑Hinweis [oai_citation:0‡codango.com](https://codango.com/what-does-sys-executable-m-mean-in-python-code/#:~:text=Understanding%20%60)

    def pip_install_cmd(self, spec: str, *, editable: bool = False) -> tuple[str, ...]:
        """Erzeugt das richtige pip‑Installationskommando für das angegebene Paket."""
        # Basisbefehle: python -m pip install …
        cmd: list[str] = [self.python_executable(), "-m", "pip", "install"]

        if not self.has_venv():
            # In der globalen Umgebung besser --user nutzen [oai_citation:1‡codango.com](https://codango.com/what-does-sys-executable-m-mean-in-python-code/#:~:text=The%20%60,users%20or%20requiring%20administrative%20privileges)
            cmd.append("--user")

        if editable:
            cmd += ["-e", spec]

        else:
            cmd.append(spec)

        return tuple(cmd)
