# tools/setup/domain/resolver.py
from __future__ import annotations

"""
Configuration resolution with three-tier fallback model.

Priority: commands > pyproject.toml > defaultconfig
Always-Default-First: load defaults completely, then layer user configs
"""

import difflib
import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Final

from .config_resolution import ConfigResolution


@dataclass(slots=True)
class ConfigResolver:
    """
    Dreistufiger Konfigurations-Resolver.

    Priorität: commands > pyproject.toml > defaultconfig
    Always-Default-First: Lade Standardwerte vollständig, dann überlagere User-Konfig.

    Design Note:
        This class combines loading, validation, and merging responsibilities.
        While this violates Single Responsibility Principle, it provides a cohesive
        API for config resolution. Future refactoring could split into:
        - ConfigLoader: Loads from files
        - ConfigValidator: Validates keys and suggests corrections
        - ConfigMerger: Merges multiple config layers
        
        Current unified design chosen for simplicity and fewer dependencies.

    Attributes:
        _default_config: Standardkonfiguration (immer vollständig)
        _pyproject_config: Konfiguration aus pyproject.toml
        _command_config: Konfiguration aus CLI-Argumenten
    """

    _default_config: Mapping[str, Any]
    _pyproject_config: Mapping[str, Any] = field(default_factory=dict)
    _command_config: Mapping[str, Any] = field(default_factory=dict)

    # Valide Top-Level-Keys für [tool.setup]
    # TODO: Consider making these configurable via TOML for easier extension.
    # Current design: hardcoded for stability and explicit validation.
    # Future: Could load from setup_config.toml [config.valid_keys] section.
    _VALID_KEYS: Final[frozenset[str]] = frozenset({
        "steps",
        "exclude",
        "auto_install",
        "verbosity",
        "options",
        "linter",
    })

    @classmethod
    def from_defaults(cls, default_toml_path: Path) -> "ConfigResolver":
        """
        Lädt den Resolver mit Standardkonfiguration aus TOML.

        Args:
            default_toml_path: Pfad zur setup_config.toml

        Returns:
            Initialisierter ConfigResolver mit geladener Standardkonfig.
        """
        if not default_toml_path.exists():
            # Fallback: leere Standardkonfiguration
            default_config: Mapping[str, Any] = {
                "config": {"defaults": {"auto_install": True, "verbosity": 1}},
                "steps": [],
            }
        else:
            try:
                with default_toml_path.open("rb") as f:
                    default_config = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise ValueError(
                    f"Ungültige TOML-Syntax in {default_toml_path}: {e}"
                ) from e

        return cls(_default_config=default_config)

    def add_pyproject(self, pyproject_path: Path) -> None:
        """
        Fügt pyproject.toml-Ebene hinzu.

        Liest [tool.setup] aus der pyproject.toml und speichert es
        als pyproject-Layer. Ungültige Schlüssel werden später beim
        Resolve gemeldet.

        Args:
            pyproject_path: Pfad zur pyproject.toml (Datei oder Verzeichnis)
        """
        if pyproject_path.is_dir():
            pyproject_path = pyproject_path / "pyproject.toml"

        if not pyproject_path.exists():
            # Keine pyproject.toml vorhanden → leerer Layer
            return

        try:
            with pyproject_path.open("rb") as f:
                data: Mapping[str, Any] = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            # Ungültige pyproject.toml → leerer Layer mit Warnung
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Ungültige TOML-Syntax in {pyproject_path}, ignoriert: {e}"
            )
            return

        tool_table: Mapping[str, Any] = data.get("tool", {})
        setup_table: Mapping[str, Any] = tool_table.get("setup", {})

        # Komplette [tool.setup]-Sektion speichern (Validierung später)
        self._pyproject_config = dict(setup_table)

    def add_commands(self, command_dict: Mapping[str, Any]) -> None:
        """
        Fügt CLI-Command-Ebene hinzu.

        Args:
            command_dict: Dictionary mit CLI-Argumenten
                z.B. {"steps": ["create_env"], "verbosity": 2}
        """
        self._command_config = dict(command_dict)

    def _suggest_keys(
        self,
        unknown_key: str,
        valid_keys: frozenset[str],
        cutoff: float = 0.6,
    ) -> tuple[str, ...]:
        """
        Generiert 'Meinten Sie…?'-Vorschläge via difflib.

        Args:
            unknown_key: Der unbekannte Schlüssel
            valid_keys: Menge gültiger Schlüssel
            cutoff: Minimale Ähnlichkeit (0.0 bis 1.0)

        Returns:
            Tuple von bis zu 3 Vorschlägen
        """
        matches: list[str] = difflib.get_close_matches(
            unknown_key,
            list(valid_keys),
            n=3,
            cutoff=cutoff,
        )
        return tuple(matches)

    def _validate_and_merge(
        self,
        base: dict[str, Any],
        overlay: Mapping[str, Any],
        source_name: str,
    ) -> tuple[dict[str, Any], list[str], dict[str, tuple[str, ...]]]:
        """
        Validiert und merged einen Config-Layer.

        Args:
            base: Basis-Konfiguration (wird modifiziert)
            overlay: Zu merge-nde Konfiguration
            source_name: Name der Quelle (für Warnungen)

        Returns:
            (merged_config, warnings, suggestions)
        """
        warnings: list[str] = []
        suggestions: dict[str, tuple[str, ...]] = {}

        for key, value in overlay.items():
            if key in self._VALID_KEYS:
                # Gültiger Schlüssel: überschreiben
                base[key] = value
            else:
                # Ungültiger Schlüssel: Warnung + Vorschlag
                matches = self._suggest_keys(key, self._VALID_KEYS)
                if matches:
                    msg = (
                        f"{source_name}: Unbekannte Option '{key}' ignoriert. "
                        f"Meinten Sie: {', '.join(matches)}?"
                    )
                    suggestions[key] = matches
                else:
                    msg = f"{source_name}: Unbekannte Option '{key}' ignoriert."

                warnings.append(msg)

        return base, warnings, suggestions

    def resolve(self) -> ConfigResolution:
        """
        Löst die finale Konfiguration auf.

        Reihenfolge:
        1. Standardkonfiguration vollständig laden
        2. pyproject.toml darüberlegen (gültige Keys)
        3. commands darüberlegen (gültige Keys)

        Returns:
            ConfigResolution mit aufgelöster Konfiguration,
            Warnungen und Vorschlägen für ungültige Keys.
        """
        # 1. Start mit Standardwerten aus [config.defaults]
        defaults_section: Mapping[str, Any] = self._default_config.get("config", {})
        defaults_data: Mapping[str, Any] = defaults_section.get("defaults", {})

        result: dict[str, Any] = dict(defaults_data)

        all_warnings: list[str] = []
        all_suggestions: dict[str, tuple[str, ...]] = {}

        # 2. Pyproject-Layer mergen
        if self._pyproject_config:
            result, warnings, suggestions = self._validate_and_merge(
                result,
                self._pyproject_config,
                "pyproject.toml",
            )
            all_warnings.extend(warnings)
            all_suggestions.update(suggestions)

        # 3. Command-Layer mergen (höchste Priorität)
        if self._command_config:
            result, warnings, suggestions = self._validate_and_merge(
                result,
                self._command_config,
                "CLI-Argumente",
            )
            all_warnings.extend(warnings)
            all_suggestions.update(suggestions)

        return ConfigResolution(
            config=result,
            warnings=tuple(all_warnings),
            suggestions=all_suggestions,
        )

    def get_steps_metadata(self) -> tuple[dict[str, Any], ...]:
        """
        Liefert die Step-Metadaten aus der Standardkonfiguration.

        Returns:
            Tuple von Step-Dictionaries mit id, name, description, prio, etc.
        """
        steps_list: list[dict[str, Any]] = self._default_config.get("steps", [])
        return tuple(steps_list)
