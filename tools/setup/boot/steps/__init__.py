"""Submodul mit allen öffentlich nutzbaren Setup-Schritten."""

from __future__ import annotations

from .environment import (
    get_platform_info,
    check_python_version,
    create_virtualenv,
    update_pip,
    configure_pip_index,
    check_pyqt5_macos,
)
from .dependencies import (
    install_runtime_requirements,
    install_dev_requirements,
    install_project_editable,
    verify_installation,
)
from .check import run_tests
from .linting import run_import_analysis

__all__ = [
    # environment
    "get_platform_info",
    "check_python_version",
    "create_virtualenv",
    "update_pip",
    "configure_pip_index",
    "check_pyqt5_macos",
    # dependencies
    "install_runtime_requirements",
    "install_dev_requirements",
    "install_project_editable",
    "verify_installation",
    # testing
    "run_tests",
    # linting
    "run_import_analysis",
]
