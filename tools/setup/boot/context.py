from __future__ import annotations

"""Kontext und Pipeline-Definition für den Bootstrap-Prozess."""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Protocol

from tools.common import ErrorLog
from tools.setup.config import BootstrapConfig, PlatformInfo
from tools.setup.boot.profile import SetupProfile, build_profile_from_pyproject
from tools.setup.boot.steps import linting, environment, dependencies


class StepId(StrEnum):
    PYTHON_VERSION = auto()
    VENV = auto()
    PIP_UPDATE = auto()
    PIP_INDEX = auto()
    PYQT_CHECK = auto()
    RUNTIME_DEPS = auto()
    DEV_DEPS = auto()
    EDITABLE_INSTALL = auto()
    VERIFY = auto()
    IMPORT_LINTER = auto()


@dataclass(slots=True)
class BootstrapContext:
    """Gesamtkontext für die Setup-Pipeline."""

    config: BootstrapConfig
    platform: PlatformInfo
    log: ErrorLog
    profile: SetupProfile


class StepFunc(Protocol):
    """Signatur eines Setup-Schritts."""

    def __call__(self, ctx: BootstrapContext) -> bool:  # pragma: no cover - Interface
        ...


@dataclass(slots=True, frozen=True)
class StepDefinition:
    """Definition eines einzelnen Setup-Schritts."""

    id: StepId
    label: str
    func: StepFunc
    fatal: bool = True
    enabled: bool = True
    show_progress: bool = True


def build_context(config: BootstrapConfig) -> BootstrapContext:
    """Erzeugt den Bootstrap-Kontext aus Konfiguration und pyproject.toml."""
    profile = build_profile_from_pyproject()
    platform = steps_env.get_platform_info(config)
    log = ErrorLog(config.log_path)
    return BootstrapContext(config=config, platform=platform, log=log, profile=profile)


def build_pipeline(ctx: BootstrapContext) -> list[StepDefinition]:
    """Definiert die Setup-Pipeline als Liste von Schritten."""
    p = ctx.profile

    return [
        StepDefinition(
            StepId.PYTHON_VERSION,
            "Python-Version prüfen",
            lambda c: steps_env.check_python_version(p.requires_min_python),
        ),
        StepDefinition(
            StepId.VENV,
            "Virtuelle Umgebung erstellen",
            lambda c: steps_env.create_virtualenv(c.config),
        ),
        StepDefinition(
            StepId.PIP_UPDATE,
            "pip aktualisieren",
            lambda c: steps_env.update_pip(c.platform),
        ),
        StepDefinition(
            StepId.PIP_INDEX,
            "pip Index konfigurieren",
            lambda c: steps_env.configure_pip_index(c.platform),
            fatal=False,
        ),
        StepDefinition(
            StepId.PYQT_CHECK,
            "PyQt5 macOS-Check",
            lambda c: steps_env.check_pyqt5_macos(c.platform),
            enabled=p.requires_pyqt,
            fatal=False,
        ),
        StepDefinition(
            StepId.RUNTIME_DEPS,
            "Runtime-Dependencies installieren",
            lambda c: steps_deps.install_runtime_requirements(
                c.platform,
                dict(p.runtime_requirements),
                c.log,
            ),
        ),
        StepDefinition(
            StepId.DEV_DEPS,
            "Dev-Dependencies installieren",
            lambda c: steps_deps.install_dev_requirements(
                c.platform,
                dict(p.dev_requirements),
                c.log,
            ),
            enabled=p.has_dev_requirements,
        ),
        StepDefinition(
            StepId.EDITABLE_INSTALL,
            "Projekt (Editable) installieren",
            lambda c: steps_deps.install_project_editable(c.platform, c.log),
        ),
        StepDefinition(
            StepId.VERIFY,
            "Installation verifizieren",
            lambda c: steps_deps.verify_installation(
                dict(p.runtime_requirements),
                dict(p.dev_requirements),
                c.log,
            ),
        ),
        StepDefinition(
            StepId.IMPORT_LINTER,
            "Import-Linter ausführen",
            lambda c: steps_linting.run_import_analysis(c.log),
            enabled=p.uses_import_linter,
            fatal=False,
        ),
    ]
