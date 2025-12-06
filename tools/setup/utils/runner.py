from __future__ import annotations

from logging import Logger
from pathlib import Path

from tools.setup.utils import module


def run_single(
        python: str,
        cwd: Path,
        nodeid: str | None = None,
        logger: Logger | None = None,
) -> tuple[bool, str, str]:
    """
    Führt einen einzelnen pytest-Lauf aus.

    Rückgabe:
        (ok, cause, details)
    """
    extra_args: tuple[str, ...] = (nodeid,) if nodeid is not None else tuple()

    argv = (python, "-m", "pytest", *extra_args)

    # Debug-Ausgabe über Standard-Logging (optional)
    if logger is not None:
        logger.debug("pytest argv: %r", argv)

    ok, output, exc_info = module.evaluate(
        python=python,
        module="pytest",
        cwd=cwd,  # Path, passt zu 'Path | None'
        extra_args=extra_args,
    )
    raw = output or ""
    if ok:
        return True, "", raw

    return (
        (False, "tests_running_error", exc_info)
        if isinstance(exc_info, str)
        else (False, "tests_failed", raw or "keine Ausgabe")
    )
