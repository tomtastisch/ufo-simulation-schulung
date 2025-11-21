# ...existing code...
import subprocess
import sys


def test_state_module_is_independent() -> None:
    """
    Lädt `src/core/simulation/state/state.py` isoliert (ohne Paket-__init__ auszulösen)
    und prüft, dass dabei keine höheren Simulationsmodule importiert werden.

    Dieser Test läuft in einem separaten Python-Subprozess, damit bereits in diesem Prozess
    geladene Module (z. B. aus anderen Tests) das Ergebnis nicht beeinflussen.
    """
    script = r"""
from pathlib import Path
import importlib.util
import sys

p = Path('src/core/simulation/state/state.py').resolve()
# Load module from file location to avoid executing package __init__
spec = importlib.util.spec_from_file_location('ufo_state_isolation_test', str(p))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Now check sys.modules for forbidden higher-level modules
forbidden = [
    'core.simulation.ufosim',
    'core.simulation.view',
    'core.simulation.ufo_main',
    'core.simulation'
]
found = [m for m in forbidden if m in sys.modules]
if found:
    # Print the first found module name (signal to caller)
    print(found[0])
"""

    proc = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
    out = proc.stdout.strip()
    if proc.returncode != 0:
        # provide diagnostics on failure
        raise AssertionError(f"Subprocess failed: returncode={proc.returncode}, stderr={proc.stderr}\nstdout={proc.stdout}")

    assert out == "", f"state module imported higher-level module: {out}"

# ...existing code...

