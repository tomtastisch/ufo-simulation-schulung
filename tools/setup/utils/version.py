import sys
from pathlib import Path
from venv import create as venv_create

from tools.setup.steps.base import StepContext


def check_python_version(ctx: StepContext) -> tuple[bool, str, str]:
    required = ctx.profile.requires_min_python
    assert required is not None  # Profil muss eine Version liefern

    req_major, req_minor = required
    cur_major, cur_minor = sys.version_info[:2]

    if (cur_major, cur_minor) < (req_major, req_minor):
        return (
            False,
            "python_version_mismatch",
            f"current={cur_major}.{cur_minor}, required>={req_major}.{req_minor}",
        )

    return True, "", ""


def ensure_venv(ctx: StepContext, safety_check: bool = True) -> tuple[bool, str, str]:
    venv_dir: Path = ctx.config.venv_dir
    repo_root: Path = ctx.config.repo_root

    # Sicherheitsgurt: venv darf nur im aktuellen Projekt liegen
    try:
        venv_dir.relative_to(repo_root)
    except ValueError:
        return (
            False,
            "venv_outside_repo",
            f"venv_dir={venv_dir} liegt nicht unter repo_root={repo_root}",
        )

    # Optional: Name prüfen, um versehentliche Fremdpfade zu vermeiden
    if all((safety_check, venv_dir.name != ".venv")):
        return (
            False,
            "venv_unexpected_name",
            f"erwartet .venv, gefunden {venv_dir.name}",
        )

    try:
        # Bewusster Reset: vorhandene venv wird überschrieben
        venv_create(venv_dir, with_pip=True, clear=True)
    except OSError as exc:
        return (
            False,
            "venv_create_failed",
            str(exc),
        )

    return True, "", ""
