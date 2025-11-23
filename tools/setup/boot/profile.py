from __future__ import annotations

"""Erzeugt ein Setup-Profil direkt aus pyproject.toml."""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(slots=True, frozen=True)
class SetupProfile:
    """Abgeleitete Informationen aus pyproject.toml für die Setup-Pipeline."""

    requires_pyqt: bool
    uses_import_linter: bool
    uses_pytest: bool
    has_dev_requirements: bool
    requires_min_python: tuple[int, int] | None
    runtime_requirements: Mapping[str, str]
    dev_requirements: Mapping[str, str]
    pyproject_path: Path


def _normalize_requirement(spec: str) -> tuple[str, str]:
    """Zerlegt einen PEP 508-String in (Name, Versions-Spec)."""
    spec = spec.strip()
    if not spec:
        return "", ""
    stop_chars = "<>!=~[ "
    idx = len(spec)
    for i, ch in enumerate(spec):
        if ch in stop_chars:
            idx = i
            break
    name = spec[:idx].strip()
    version = spec[idx:].strip()
    return name, version


def build_profile_from_pyproject(pyproject_path: Path | None = None) -> SetupProfile:
    """Liest pyproject.toml und baut daraus ein SetupProfile."""
    path = pyproject_path or Path("pyproject.toml")
    if not path.exists():
        raise FileNotFoundError(f"pyproject.toml nicht gefunden: {path}")

    with path.open("rb") as fh:
        data = tomllib.load(fh)

    project = data.get("project", {})
    requires_python = str(project.get("requires-python", "")).strip() or None
    runtime_list = list(project.get("dependencies", []))
    optional = project.get("optional-dependencies", {})
    dev_list = list(optional.get("dev", []))

    runtime_req: dict[str, str] = {}
    for entry in runtime_list:
        name, version = _normalize_requirement(str(entry))
        if name:
            runtime_req[name] = version

    dev_req: dict[str, str] = {}
    for entry in dev_list:
        name, version = _normalize_requirement(str(entry))
        if name:
            dev_req[name] = version

    all_names = {n.lower() for n in runtime_req} | {n.lower() for n in dev_req}

    requires_pyqt = any(n.startswith("pyqt") for n in all_names)
    uses_import_linter = "import-linter" in all_names
    uses_pytest = "pytest" in all_names
    has_dev_requirements = bool(dev_req)

    min_version: tuple[int, int] | None = None
    if requires_python:
        match = re.search(r"(\d+)\.(\d+)", requires_python)
        if match:
            min_version = (int(match.group(1)), int(match.group(2)))

    return SetupProfile(
        requires_pyqt=requires_pyqt,
        uses_import_linter=uses_import_linter,
        uses_pytest=uses_pytest,
        has_dev_requirements=has_dev_requirements,
        requires_min_python=min_version,
        runtime_requirements=runtime_req,
        dev_requirements=dev_req,
        pyproject_path=path,
    )
