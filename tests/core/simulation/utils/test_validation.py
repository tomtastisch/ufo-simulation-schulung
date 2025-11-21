"""
Unit-Tests für das utils.validation Modul.

Testet Validierungsfunktionen für Wertebereichs-Prüfungen.
"""

from __future__ import annotations

import pytest

from core.simulation.utils.validation import is_in_range, validate_range


class TestValidateRange:
    """Tests für validate_range Funktion."""

    def test_value_in_range(self):
        """Wert im Bereich sollte keinen Fehler werfen."""
        validate_range(5.0, 0.0, 10.0, "test_value")  # Sollte nicht werfen

    def test_value_at_min_boundary(self):
        """Wert an unterer Grenze sollte erlaubt sein."""
        validate_range(0.0, 0.0, 10.0, "test_value")

    def test_value_at_max_boundary(self):
        """Wert an oberer Grenze sollte erlaubt sein."""
        validate_range(10.0, 0.0, 10.0, "test_value")

    def test_value_below_min(self):
        """Wert unter Minimum sollte ValueError werfen."""
        with pytest.raises(ValueError, match="test_value muss zwischen 0.0 und 10.0 liegen"):
            validate_range(-1.0, 0.0, 10.0, "test_value")

    def test_value_above_max(self):
        """Wert über Maximum sollte ValueError werfen."""
        with pytest.raises(ValueError, match="test_value muss zwischen 0.0 und 10.0 liegen"):
            validate_range(11.0, 0.0, 10.0, "test_value")

    def test_negative_range(self):
        """Negativer Wertebereich sollte funktionieren."""
        validate_range(-5.0, -10.0, -1.0, "negative_value")

    def test_error_message_includes_name(self):
        """Fehlermeldung sollte Parameter-Namen enthalten."""
        with pytest.raises(ValueError, match="velocity"):
            validate_range(150.0, 0.0, 100.0, "velocity")


class TestIsInRange:
    """Tests für is_in_range Funktion."""

    def test_value_in_range(self):
        """Wert im Bereich sollte True zurückgeben."""
        assert is_in_range(5.0, 0.0, 10.0) is True

    def test_value_at_min_boundary(self):
        """Wert an unterer Grenze sollte True sein."""
        assert is_in_range(0.0, 0.0, 10.0) is True

    def test_value_at_max_boundary(self):
        """Wert an oberer Grenze sollte True sein."""
        assert is_in_range(10.0, 0.0, 10.0) is True

    def test_value_below_min(self):
        """Wert unter Minimum sollte False sein."""
        assert is_in_range(-1.0, 0.0, 10.0) is False

    def test_value_above_max(self):
        """Wert über Maximum sollte False sein."""
        assert is_in_range(11.0, 0.0, 10.0) is False

    def test_negative_range(self):
        """Negativer Wertebereich sollte funktionieren."""
        assert is_in_range(-5.0, -10.0, -1.0) is True
        assert is_in_range(-15.0, -10.0, -1.0) is False

    def test_zero_value(self):
        """Null sollte korrekt behandelt werden."""
        assert is_in_range(0.0, -10.0, 10.0) is True
        assert is_in_range(0.0, 1.0, 10.0) is False


class TestModuleIntegration:
    """Integrations-Tests für validation Modul."""

    def test_both_functions_consistent(self):
        """validate_range und is_in_range sollten konsistent sein."""
        # Wert im Bereich
        assert is_in_range(5.0, 0.0, 10.0) is True
        validate_range(5.0, 0.0, 10.0, "test")  # Kein Fehler

        # Wert außerhalb
        assert is_in_range(15.0, 0.0, 10.0) is False
        with pytest.raises(ValueError):
            validate_range(15.0, 0.0, 10.0, "test")
