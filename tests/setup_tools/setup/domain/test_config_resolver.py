# tests/tools/setup/domain/test_config_resolver.py
from __future__ import annotations

"""
Tests für ConfigResolver - drei-stufige Konfigurationsauflösung.

Testet:
- Laden von Standardkonfiguration
- Overlayen von pyproject.toml
- Overlayen von CLI-Commands
- Difflib-Vorschläge für ungültige Keys
- Szenarien 2.1, 2.2, 2.3 aus der Spezifikation
"""

import tempfile
from pathlib import Path


from tools.setup.domain.resolver import ConfigResolver, ConfigResolution


def test_load_from_nonexistent_defaults(tmp_path):
    """Test: Wenn setup_config.toml nicht existiert, wird Fallback-Config verwendet."""
    nonexistent_path = tmp_path / "does_not_exist_12345.toml"
    resolver = ConfigResolver.from_defaults(nonexistent_path)

    assert resolver._default_config is not None
    assert "config" in resolver._default_config
    # Fallback-Defaults sollten vorhanden sein
    defaults = resolver._default_config["config"]["defaults"]
    assert defaults["auto_install"] is True
    assert defaults["verbosity"] == 1


def test_load_from_valid_defaults():
    """Test: Laden einer gültigen setup_config.toml."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[config.defaults]
auto_install = false
verbosity = 2

[[steps]]
id = "test_step"
name = "Test Step"
prio = 100
enabled = true
""")
        config_path = Path(f.name)

    try:
        resolver = ConfigResolver.from_defaults(config_path)

        # Defaults prüfen
        defaults = resolver._default_config["config"]["defaults"]
        assert defaults["auto_install"] is False
        assert defaults["verbosity"] == 2

        # Steps prüfen
        steps = resolver._default_config["steps"]
        assert len(steps) == 1
        assert steps[0]["id"] == "test_step"
        assert steps[0]["prio"] == 100

    finally:
        config_path.unlink()


def test_add_pyproject_from_nonexistent_path(tmp_path):
    """Test: Wenn pyproject.toml nicht existiert, wird nichts hinzugefügt."""
    resolver = ConfigResolver.from_defaults(tmp_path / "nonexistent.toml")
    resolver.add_pyproject(tmp_path / "also_nonexistent" / "pyproject.toml")

    # Kein Fehler, pyproject_config bleibt leer
    assert resolver._pyproject_config == {}


def test_add_pyproject_from_valid_file():
    """Test: Laden von [tool.setup] aus pyproject.toml."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[project]
name = "test"

[tool.setup]
steps = ["create_env", "tests"]
exclude = ["linter"]
verbosity = 3
""")
        pyproject_path = Path(f.name)

    try:
        resolver = ConfigResolver.from_defaults(Path("/tmp/nonexistent.toml"))
        resolver.add_pyproject(pyproject_path)

        # pyproject_config sollte [tool.setup] enthalten
        assert "steps" in resolver._pyproject_config
        assert resolver._pyproject_config["steps"] == ["create_env", "tests"]
        assert resolver._pyproject_config["exclude"] == ["linter"]
        assert resolver._pyproject_config["verbosity"] == 3

    finally:
        pyproject_path.unlink()


def test_add_commands(tmp_path):
    """Test: CLI-Commands hinzufügen."""
    resolver = ConfigResolver.from_defaults(tmp_path / "nonexistent.toml")
    commands = {"verbosity": 5, "steps": ["only_this"]}
    resolver.add_commands(commands)

    assert resolver._command_config["verbosity"] == 5
    assert resolver._command_config["steps"] == ["only_this"]


def test_resolve_scenario_2_1_no_commands_no_pyproject(tmp_path):
    """
    Test Szenario 2.1: Keine commands, keine pyproject.toml.
    Ergebnis: defaultconfig.
    """
    resolver = ConfigResolver.from_defaults(tmp_path / "nonexistent.toml")
    # Keine pyproject, keine commands
    resolution = resolver.resolve()

    # Sollte nur Defaults enthalten
    assert resolution.config["auto_install"] is True
    assert resolution.config["verbosity"] == 1
    assert len(resolution.warnings) == 0


def test_resolve_scenario_2_2_no_commands_empty_pyproject(tmp_path):
    """
    Test Szenario 2.2: Keine commands, pyproject.toml ohne relevante Konfigurationen.
    Ergebnis: defaultconfig.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[project]
name = "test"

# Kein [tool.setup]
""")
        pyproject_path = Path(f.name)

    try:
        resolver = ConfigResolver.from_defaults(tmp_path / "nonexistent.toml")
        resolver.add_pyproject(pyproject_path)
        resolution = resolver.resolve()

        # Sollte nur Defaults enthalten (pyproject hat nichts zu [tool.setup])
        assert resolution.config["auto_install"] is True
        assert resolution.config["verbosity"] == 1
        assert len(resolution.warnings) == 0

    finally:
        pyproject_path.unlink()


def test_resolve_scenario_2_3_invalid_keys_with_suggestions(tmp_path):
    """
    Test Szenario 2.3: pyproject.toml mit falschen/unzuordenbaren Konfigurationen.
    Ergebnis: defaultconfig für diese Teile, plus Hinweise.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[project]
name = "test"

[tool.setup]
stpes = ["create_env"]  # Typo: sollte "steps" sein
verbosity = 2  # gültig
unknown_key = "value"  # unbekannt
""")
        pyproject_path = Path(f.name)

    try:
        resolver = ConfigResolver.from_defaults(tmp_path / "nonexistent.toml")
        resolver.add_pyproject(pyproject_path)
        resolution = resolver.resolve()

        # Gültiger Key wurde übernommen
        assert resolution.config["verbosity"] == 2

        # Ungültige Keys wurden ignoriert, Warnings vorhanden
        assert len(resolution.warnings) > 0

        # "stpes" sollte Vorschlag "steps" bekommen
        warnings_text = " ".join(resolution.warnings)
        assert "stpes" in warnings_text
        assert "steps" in warnings_text or "Meinten Sie" in warnings_text

    finally:
        pyproject_path.unlink()


def test_resolve_priority_order():
    """
    Test: Prioritätsreihenfolge commands > pyproject > defaults.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[config.defaults]
auto_install = true
verbosity = 1
""")
        config_path = Path(f.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[tool.setup]
verbosity = 3
""")
        pyproject_path = Path(f.name)

    try:
        resolver = ConfigResolver.from_defaults(config_path)
        resolver.add_pyproject(pyproject_path)
        resolver.add_commands({"verbosity": 5})

        resolution = resolver.resolve()

        # Commands haben höchste Priorität
        assert resolution.config["verbosity"] == 5
        # auto_install kommt aus defaults (nicht überschrieben)
        assert resolution.config["auto_install"] is True

    finally:
        config_path.unlink()
        pyproject_path.unlink()


def test_get_steps_metadata():
    """Test: Step-Metadaten aus Standardkonfiguration extrahieren."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[config.defaults]
auto_install = true

[[steps]]
id = "step1"
name = "Step One"
prio = 100

[[steps]]
id = "step2"
name = "Step Two"
prio = 50
""")
        config_path = Path(f.name)

    try:
        resolver = ConfigResolver.from_defaults(config_path)
        steps = resolver.get_steps_metadata()

        assert len(steps) == 2
        assert steps[0]["id"] == "step1"
        assert steps[0]["prio"] == 100
        assert steps[1]["id"] == "step2"
        assert steps[1]["prio"] == 50

    finally:
        config_path.unlink()


def test_suggest_keys_exact_match(tmp_path):
    """Test: difflib-Vorschläge bei ähnlichen Keys."""
    resolver = ConfigResolver.from_defaults(tmp_path / "nonexistent.toml")

    suggestions = resolver._suggest_keys(
        "stpes",
        frozenset({"steps", "exclude", "verbosity"}),
    )

    assert "steps" in suggestions


def test_suggest_keys_no_match(tmp_path):
    """Test: Keine Vorschläge wenn Key zu unterschiedlich."""
    resolver = ConfigResolver.from_defaults(tmp_path / "nonexistent.toml")

    suggestions = resolver._suggest_keys(
        "xyz123",
        frozenset({"steps", "exclude", "verbosity"}),
    )

    assert len(suggestions) == 0
