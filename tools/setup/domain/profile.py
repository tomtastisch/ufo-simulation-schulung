# tools/setup/domain/profile.py
from __future__ import annotations

"""
Projektprofil auf Basis von pyproject.toml.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Mapping, Literal
import tomllib

PYPROJECT_FILENAME: Final[str] = "pyproject.toml"


class RequirementOperator(StrEnum):
    """Unterstützte Vergleichsoperatoren für Dependency-Spezifikationen."""

    NOT_EQUAL = "!="
    EQUAL = "=="
    GTE = ">="
    LTE = "<="
    GT = ">"
    LT = "<"
    COMPAT = "~="
    EXACT = "==="

    @classmethod
    def detect(cls, text: str) -> tuple[str, str] | None:
        """Zerlegt eine Requirement-Spezifikation in (name, version_spec).

        Beispiele:
        - "importlinter>=2.0" -> ("importlinter", ">=2.0")
        - ">=3.10"            -> ("", ">=3.10")  (z. B. für requires-python)

        Liefert None, wenn kein Vergleichsoperator aus RequirementOperator gefunden wird.
        """
        spec = text.strip()
        if not spec:
            return None

        # Längere Operatoren zuerst prüfen (z. B. ">=" vor ">")
        operators = sorted(
            cls.__members__.values(),  # type: dict[str, RequirementOperator].values
            key=lambda o: len(o.value),  # hier ist o klar ein RequirementOperator
            reverse=True,
        )

        candidates: list[tuple[int, str]] = [
            (pos, op_str)
            for op in operators
            if (op_str := op.value)  # op_str: str
            if (pos := spec.find(op_str)) != -1
        ]

        if not candidates:
            return None

        best_pos, best_op = min(candidates, key=lambda t: t[0])

        name = spec[:best_pos].strip()
        version_spec = spec[best_pos:].strip()
        return name, version_spec


@dataclass(slots=True)
class PyProjectProfile:
    """Setup-relevante Inhalte aus pyproject.toml."""

    requires_min_python: tuple[int, int] | None
    runtime_requirements: Mapping[str, str] = field(default_factory=dict)
    dev_requirements: Mapping[str, str] = field(default_factory=dict)

    # Step-Steuerung aus [tool.setup]
    step_include: tuple[str, ...] = field(default_factory=tuple)
    step_exclude: tuple[str, ...] = field(default_factory=tuple)
    step_options: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    verbosity: int = 1
    auto_install: bool = True

    # Linter-spezifische Steuerung aus [tool.setup.linter]
    # "all" (Default) | "forbidden" | "layers"
    linter_contracts: Literal["all", "forbidden", "layers"] = "all"

    # Vollständige pyproject-Struktur für generische Zugriffe
    pyproject_data: Mapping[str, Any] = field(default_factory=dict)

    def get_path(self, *path: str, default: Any = None) -> Any:
        """Generischer Zugriff auf verschachtelte pyproject.toml-Werte."""
        data: Any = self.pyproject_data
        for key in path:
            if not isinstance(data, Mapping):
                return default
            data = data.get(key)
            if data is None:
                return default
        return data


def _min_version_from_segment(segment: str) -> tuple[int, int] | None:
    """
    Extrahiert eine Mindestversion (major, minor) aus einem Segment.

    Erwartet Einträge wie ">=3.10" und ignoriert fachlich unpassende Werte.
    """
    result: tuple[int, int] | None = None
    detection: tuple[str, str] | None = RequirementOperator.detect(segment)

    if detection is not None:
        name, version_spec = detection

        # für requires-python sind Paketnamen unerwartet
        if not name:
            gte: str = RequirementOperator.GTE
            if version_spec.startswith(gte):
                version: str = version_spec.removeprefix(gte).strip()
                parts: list[str] = version.split(".")

                if len(parts) >= 2:
                    major_str: str = parts[0]
                    minor_str: str = parts[1]

                    if major_str.isdecimal() and minor_str.isdecimal():
                        major: int = int(major_str)
                        minor: int = int(minor_str)
                        result = (major, minor)
    return result


def _parse_requires_python(spec: str | None) -> tuple[int, int] | None:
    """
    Interpretiert `project.requires-python` als Mindestversion (major, minor).

    Ausgewertet wird nur die erste untere Schranke vom Typ ">=X.Y".
    """
    result: tuple[int, int] | None = None

    if spec:
        segments = (segment.strip() for segment in spec.split(","))
        for segment in segments:
            if not segment:
                continue

            version: tuple[int, int] | None = _min_version_from_segment(segment)
            if version is not None:
                result = version
                break

    return result


def _normalize_requirements(entries: list[str]) -> Mapping[str, str]:
    """
    Normalisiert eine Liste von Abhängigkeiten in ein Mapping name -> spec.
    """
    result: dict[str, str] = {}

    for raw in entries:
        entry: str = raw.strip()
        if not entry:
            continue

        detection: tuple[str, str] | None = RequirementOperator.detect(entry)
        if detection is None:
            result[entry] = ""
        else:
            name, version_spec = detection
            result[name] = version_spec

    return result


def _load_pyproject_data(path: Path) -> Mapping[str, Any]:
    """
    Lädt pyproject.toml.

    Falls keine Datei existiert, wird ein leeres Mapping geliefert,
    so dass das Setup mit Standardprofil weiterlaufen kann.
    """
    # Wenn ein Verzeichnis übergeben wurde, pyproject.toml darin suchen,
    # ansonsten path direkt als Dateipfad interpretieren.
    pyproject_path = path / PYPROJECT_FILENAME if path.is_dir() else path

    if not pyproject_path.exists():
        return {}

    with pyproject_path.open("rb") as handle:
        data: Mapping[str, Any] = tomllib.load(handle)

    return data


def _normalize_str_list(value: Any) -> tuple[str, ...]:
    """
    Normalisiert Werte aus der pyproject-Konfiguration auf eine
    geordnete Tupel-Liste von Strings.
    """
    if value is None:
        return ()

    if isinstance(value, str):
        value = [value]

    return tuple(
        str(item).strip()
        for item in value
        if str(item).strip()
    )


def build_profile(repo_root: Path) -> PyProjectProfile:
    """
    Lädt die pyproject.toml genau einmal und baut ein Setup-Profil.

    - [project]                  → Dependencies, requires-python
    - [tool.setup]               → steps, exclude, options, linter
    - [tool.setup.linter]        → contracts-Modus ("all" | "forbidden" | "layers")
    - weitere tool-Abschnitte    → über pyproject_data / get_path(...)
    """
    data = _load_pyproject_data(repo_root)

    project_table: Mapping[str, Any] = data.get("project", {})
    requires_python_str: str | None = project_table.get("requires-python")
    requires_min_python: tuple[int, int] | None = _parse_requires_python(
        requires_python_str,
    )

    # Laufzeit-Abhängigkeiten kommen aus [project].dependencies
    deps_list: list[str] = project_table.get("dependencies", [])
    runtime_requirements: Mapping[str, str] = _normalize_requirements(deps_list)

    # Dev-Abhängigkeiten kommen aus [project.optional-dependencies].dev
    optional_deps: Mapping[str, list[str]] = project_table.get(
        "optional-dependencies",
        {},
    )
    dev_requirements: Mapping[str, str] = _normalize_requirements(
        optional_deps.get("dev", []),
    )

    tool_table: Mapping[str, Any] = data.get("tool", {})
    setup_table: Mapping[str, Any] = tool_table.get("setup", {})

    # [tool.setup].steps / exclude
    step_include: tuple[str, ...] = _normalize_str_list(setup_table.get("steps"))
    step_exclude: tuple[str, ...] = _normalize_str_list(setup_table.get("exclude"))

    # [tool.setup].options.<step-id>
    raw_options: Any = setup_table.get("options", {})
    if isinstance(raw_options, Mapping):
        tmp: dict[str, Mapping[str, Any]] = {}
        for key, value in raw_options.items():
            if isinstance(value, Mapping):
                tmp[str(key)] = dict(value)
        step_options: Mapping[str, Mapping[str, Any]] = tmp
    else:
        step_options = {}

    # [tool.setup].auto_install (optional, Default=True)
    auto_install_raw: Any = setup_table.get("auto_install", True)
    auto_install: bool = bool(auto_install_raw)

    # [tool.setup.linter].contracts
    linter_table: Mapping[str, Any] = setup_table.get("linter", {})
    contracts_raw: Any = linter_table.get("contracts", "all")
    contracts_mode = str(contracts_raw).strip().lower()

    if contracts_mode not in {"all", "forbidden", "layers"}:
        # Fallback auf "all" bei ungültigen Werten oder leerem String
        linter_contracts: Literal["all", "forbidden", "layers"] = "all"
    else:
        linter_contracts = contracts_mode  # type: ignore[assignment]

    profile = PyProjectProfile(
        requires_min_python=requires_min_python,
        runtime_requirements=runtime_requirements,
        dev_requirements=dev_requirements,
        step_include=step_include,
        step_exclude=step_exclude,
        step_options=step_options,
        auto_install=auto_install,
        linter_contracts=linter_contracts,
        pyproject_data=data,
    )
    return profile
