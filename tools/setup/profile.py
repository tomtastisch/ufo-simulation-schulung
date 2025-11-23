from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True, frozen=True)
class PyProjectProfile:
    """Abgeleitetes Profil aus pyproject.toml."""

    runtime_requirements: dict[str, str]
    dev_requirements: dict[str, str]
    uses_import_linter: bool
    uses_pytest: bool
    requires_min_python: tuple[int, int] | None


def _parse_requirements(entries: list[str] | None) -> dict[str, str]:
    """Zerlegt 'name[op]version' in {name: op+version}."""
    if not entries:
        return {}
    result: dict[str, str] = {}
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        for op in ("==", ">=", "<=", ">", "<", "~="):
            if op in entry:
                name, spec = entry.split(op, 1)
                result[name.strip()] = f"{op}{spec.strip()}"
                break
        else:
            result[entry] = ""
    return result


def load_pyproject_profile(pyproject_path: Path | None = None) -> PyProjectProfile:
    """Liest pyproject.toml und erzeugt das Setup-Profil."""
    path = pyproject_path or Path("pyproject.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))

    project: dict[str, Any] = data.get("project", {})
    dependencies = _parse_requirements(project.get("dependencies"))
    optional = project.get("optional-dependencies", {})
    dev_deps = _parse_requirements(optional.get("dev"))

    all_names = {name.lower() for name in (*dependencies.keys(), *dev_deps.keys())}

    uses_import_linter = "import-linter" in all_names
    uses_pytest = "pytest" in all_names

    requires_python = project.get("requires-python")
    min_version: tuple[int, int] | None = None
    if isinstance(requires_python, str):
        match = re.search(r"(\d+)\.(\d+)", requires_python)
        if match:
            min_version = (int(match.group(1)), int(match.group(2)))

    return PyProjectProfile(
        runtime_requirements=dependencies,
        dev_requirements=dev_deps,
        uses_import_linter=uses_import_linter,
        uses_pytest=uses_pytest,
        requires_min_python=min_version,
    )
