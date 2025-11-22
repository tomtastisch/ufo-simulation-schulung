"""
Unit-Tests für das utils.maths Modul.

Testet alle numerischen Hilfsfunktionen mit normalen Werten, Randwerten
und Edge-Cases gemäß den Anforderungen aus Ticket T6.
"""

from __future__ import annotations

import math
import pytest

from core.simulation.utils.maths import (
    clamp,
    deg_to_rad,
    rad_to_deg,
    wrap_angle_deg,
    wrap_angle_rad,
)


class TestDegToRad:
    """Tests für deg_to_rad Funktion."""

    def test_zero_degrees(self):
        """Null Grad sollte null Radiant ergeben."""
        assert deg_to_rad(0.0) == 0.0

    def test_90_degrees(self):
        """90 Grad sollte π/2 ergeben."""
        assert abs(deg_to_rad(90.0) - math.pi / 2) < 1e-10

    def test_180_degrees(self):
        """180 Grad sollte π ergeben."""
        assert abs(deg_to_rad(180.0) - math.pi) < 1e-10

    def test_360_degrees(self):
        """360 Grad sollte 2π ergeben."""
        assert abs(deg_to_rad(360.0) - 2 * math.pi) < 1e-10

    def test_negative_degrees(self):
        """Negative Grad sollten korrekt konvertiert werden."""
        assert abs(deg_to_rad(-90.0) + math.pi / 2) < 1e-10
        assert abs(deg_to_rad(-180.0) + math.pi) < 1e-10

    def test_large_angle(self):
        """Große Winkel sollten korrekt konvertiert werden."""
        assert abs(deg_to_rad(720.0) - 4 * math.pi) < 1e-10


class TestRadToDeg:
    """Tests für rad_to_deg Funktion."""

    def test_zero_radians(self):
        """Null Radiant sollte null Grad ergeben."""
        assert rad_to_deg(0.0) == 0.0

    def test_pi_over_2_radians(self):
        """π/2 Radiant sollte 90 Grad ergeben."""
        assert abs(rad_to_deg(math.pi / 2) - 90.0) < 1e-10

    def test_pi_radians(self):
        """π Radiant sollte 180 Grad ergeben."""
        assert abs(rad_to_deg(math.pi) - 180.0) < 1e-10

    def test_two_pi_radians(self):
        """2π Radiant sollte 360 Grad ergeben."""
        assert abs(rad_to_deg(2 * math.pi) - 360.0) < 1e-10

    def test_negative_radians(self):
        """Negative Radiant sollten korrekt konvertiert werden."""
        assert abs(rad_to_deg(-math.pi / 2) + 90.0) < 1e-10
        assert abs(rad_to_deg(-math.pi) + 180.0) < 1e-10

    def test_roundtrip_conversion(self):
        """Hin- und Rückkonvertierung sollte Original-Wert ergeben."""
        original = 45.0
        converted = rad_to_deg(deg_to_rad(original))
        assert abs(converted - original) < 1e-10


class TestWrapAngleDeg:
    """Tests für wrap_angle_deg Funktion."""

    def test_zero_angle(self):
        """Null Grad sollte unverändert bleiben."""
        assert wrap_angle_deg(0.0) == 0.0

    def test_angle_in_range(self):
        """Winkel im Bereich sollten unverändert bleiben."""
        assert wrap_angle_deg(45.0) == 45.0
        assert wrap_angle_deg(-45.0) == -45.0
        assert wrap_angle_deg(179.0) == 179.0
        assert wrap_angle_deg(-179.0) == -179.0

    def test_180_degrees(self):
        """180 Grad wraps zu -180 Grad (mathematisch äquivalent)."""
        # 180° und -180° sind mathematisch äquivalent
        # Der Bereich ist [-180, 180), also exklusiv bei 180
        assert wrap_angle_deg(180.0) == -180.0

    def test_wrap_around_positive(self):
        """Positive Winkel über 180° sollten auf negative Seite wrappen."""
        assert abs(wrap_angle_deg(181.0) - (-179.0)) < 1e-10
        assert abs(wrap_angle_deg(270.0) - (-90.0)) < 1e-10
        assert abs(wrap_angle_deg(359.0) - (-1.0)) < 1e-10

    def test_wrap_around_negative(self):
        """Negative Winkel unter -180° sollten auf positive Seite wrappen."""
        assert abs(wrap_angle_deg(-181.0) - 179.0) < 1e-10
        assert abs(wrap_angle_deg(-270.0) - 90.0) < 1e-10
        assert abs(wrap_angle_deg(-359.0) - 1.0) < 1e-10

    def test_full_rotation(self):
        """360° sollte zu 0° wrappen."""
        assert abs(wrap_angle_deg(360.0)) < 1e-10
        assert abs(wrap_angle_deg(-360.0)) < 1e-10

    def test_multiple_rotations(self):
        """Mehrfache Rotationen sollten korrekt behandelt werden."""
        assert abs(wrap_angle_deg(370.0) - 10.0) < 1e-10
        assert abs(wrap_angle_deg(720.0)) < 1e-10
        assert abs(wrap_angle_deg(-720.0)) < 1e-10

    def test_large_positive_angle(self):
        """Sehr große positive Winkel sollten korrekt wrappen."""
        assert abs(wrap_angle_deg(1810.0) - 10.0) < 1e-10

    def test_large_negative_angle(self):
        """Sehr große negative Winkel sollten korrekt wrappen."""
        assert abs(wrap_angle_deg(-1810.0) - (-10.0)) < 1e-10

    def test_custom_range_0_to_360(self):
        """Custom Range [0, 360) sollte funktionieren."""
        assert wrap_angle_deg(0.0, 0.0, 360.0) == 0.0
        assert wrap_angle_deg(180.0, 0.0, 360.0) == 180.0
        assert abs(wrap_angle_deg(370.0, 0.0, 360.0) - 10.0) < 1e-10
        assert abs(wrap_angle_deg(-10.0, 0.0, 360.0) - 350.0) < 1e-10

    def test_invalid_range_raises_error(self):
        """lower >= upper sollte ValueError auslösen."""
        with pytest.raises(ValueError, match="lower .* must be strictly less than upper"):
            wrap_angle_deg(0.0, 180.0, 180.0)

        with pytest.raises(ValueError, match="lower .* must be strictly less than upper"):
            wrap_angle_deg(0.0, 180.0, 0.0)


class TestWrapAngleRad:
    """Tests für wrap_angle_rad Funktion."""

    def test_zero_radians(self):
        """Null Radiant sollte unverändert bleiben."""
        assert wrap_angle_rad(0.0) == 0.0

    def test_angle_in_range(self):
        """Winkel im Bereich [-π, π) sollten unverändert bleiben."""
        assert abs(wrap_angle_rad(math.pi / 4) - math.pi / 4) < 1e-10
        assert abs(wrap_angle_rad(-math.pi / 4) - (-math.pi / 4)) < 1e-10

    def test_pi_radians(self):
        """π Radiant wraps zu -π (mathematisch äquivalent)."""
        # π und -π sind mathematisch äquivalent
        # Der Bereich ist [-π, π), also exklusiv bei π
        assert abs(wrap_angle_rad(math.pi) - (-math.pi)) < 1e-10

    def test_wrap_around_positive(self):
        """Positive Winkel über π sollten wrappen."""
        result = wrap_angle_rad(3 * math.pi)
        expected = -math.pi  # 3π wraps to -π (äquivalent zu π)
        assert abs(result - expected) < 1e-10

    def test_wrap_around_negative(self):
        """Negative Winkel unter -π sollten wrappen."""
        result = wrap_angle_rad(-3 * math.pi)
        expected = -math.pi  # -3π wraps to -π (äquivalent zu π)
        assert abs(result - expected) < 1e-10

    def test_two_pi_radians(self):
        """2π sollte zu 0 wrappen."""
        assert abs(wrap_angle_rad(2 * math.pi)) < 1e-10

    def test_large_positive_angle(self):
        """Sehr große positive Winkel sollten korrekt wrappen."""
        result = wrap_angle_rad(10 * math.pi)
        assert abs(result) < 1e-10

    def test_large_negative_angle(self):
        """Sehr große negative Winkel sollten korrekt wrappen."""
        result = wrap_angle_rad(-10 * math.pi)
        assert abs(result) < 1e-10


class TestClamp:
    """Tests für clamp Funktion."""

    def test_value_in_range(self):
        """Werte im Bereich sollten unverändert bleiben."""
        assert clamp(5.0, 0.0, 10.0) == 5.0
        assert clamp(0.0, 0.0, 10.0) == 0.0
        assert clamp(10.0, 0.0, 10.0) == 10.0

    def test_value_below_min(self):
        """Werte unter Minimum sollten auf Minimum begrenzt werden."""
        assert clamp(-5.0, 0.0, 10.0) == 0.0
        assert clamp(-100.0, -50.0, 50.0) == -50.0

    def test_value_above_max(self):
        """Werte über Maximum sollten auf Maximum begrenzt werden."""
        assert clamp(15.0, 0.0, 10.0) == 10.0
        assert clamp(100.0, -50.0, 50.0) == 50.0

    def test_negative_range(self):
        """Negativer Wertebereich sollte funktionieren."""
        assert clamp(-5.0, -10.0, -1.0) == -5.0
        assert clamp(-15.0, -10.0, -1.0) == -10.0
        assert clamp(0.0, -10.0, -1.0) == -1.0

    def test_zero_value(self):
        """Null sollte korrekt behandelt werden."""
        assert clamp(0.0, -10.0, 10.0) == 0.0
        assert clamp(0.0, 0.0, 10.0) == 0.0
        assert clamp(0.0, -10.0, 0.0) == 0.0

    def test_equal_min_max(self):
        """Wenn min == max, sollte dieser Wert zurückgegeben werden."""
        assert clamp(5.0, 3.0, 3.0) == 3.0
        assert clamp(0.0, 3.0, 3.0) == 3.0
        assert clamp(10.0, 3.0, 3.0) == 3.0

    def test_float_precision(self):
        """Floating-Point-Werte sollten präzise behandelt werden."""
        assert clamp(1.5, 1.0, 2.0) == 1.5
        assert clamp(0.99999, 1.0, 2.0) == 1.0
        assert clamp(2.00001, 1.0, 2.0) == 2.0

    def test_invalid_range_raises_error(self):
        """min_value > max_value sollte ValueError auslösen."""
        with pytest.raises(ValueError, match="min_value .* must not be greater than max_value"):
            clamp(5.0, 10.0, 0.0)


class TestModuleIndependence:
    """Tests für Modul-Unabhängigkeit gemäß Architektur-Anforderungen."""

    def test_no_simulation_imports(self):
        """
        Prüft, dass utils.maths keine Simulation-spezifischen Typen importiert.

        Dieser Test stellt sicher, dass die Architektur-Anforderung eingehalten wird,
        dass utils.maths unabhängig von Simulationslogik ist.
        """
        import core.simulation.utils.maths as maths_module

        # Hole alle importierten Module
        module_code = maths_module.__dict__

        # Prüfe, dass keine verbotenen Importe vorhanden sind
        forbidden_imports = ["UfoState", "UfoSim", "SimulationConfig", "StateManager"]

        for forbidden in forbidden_imports:
            assert forbidden not in module_code, f"utils.maths darf {forbidden} nicht importieren"

class TestIntegrationScenarios:
    """Integrations-Tests für realistische Anwendungsszenarien."""

    def test_navigation_scenario(self):
        """
        Simuliert typische Navigation-Berechnungen.

        Testet die Kombination mehrerer Funktionen wie sie in der
        Physik-Engine verwendet werden könnten.
        """
        # Heading von 370° normalisieren
        heading_deg = wrap_angle_deg(370.0, 0.0, 360.0)
        assert abs(heading_deg - 10.0) < 1e-10

        # Konvertierung zu Radiant
        heading_rad = deg_to_rad(heading_deg)
        assert abs(heading_rad - deg_to_rad(10.0)) < 1e-10

        # Neigungswinkel clampen
        inclination = clamp(95.0, -90.0, 90.0)
        assert inclination == 90.0

    def test_angle_difference_calculation(self):
        """
        Testet Berechnung von Winkeldifferenzen über die 360°-Grenze.

        Dies ist ein häufiger Use-Case in der Navigation.
        """
        # Von 350° nach 10° ist +20° (nicht +380° oder -340°)
        angle1 = 350.0
        angle2 = 10.0

        # Normalisiere beide Winkel
        norm1 = wrap_angle_deg(angle1, -180.0, 180.0)  # -> -10°
        norm2 = wrap_angle_deg(angle2, -180.0, 180.0)  # -> 10°

        diff = norm2 - norm1  # 10° - (-10°) = 20°
        assert abs(diff - 20.0) < 1e-10

    def test_velocity_clamping_scenario(self):
        """
        Testet Geschwindigkeits-Clamping wie in der Physik-Engine.
        """
        vmax = 100.0

        # Normale Geschwindigkeit
        v1 = clamp(50.0, 0.0, vmax)
        assert v1 == 50.0

        # Zu hohe Geschwindigkeit
        v2 = clamp(150.0, 0.0, vmax)
        assert v2 == 100.0

        # Negative Geschwindigkeit (nicht erlaubt)
        v3 = clamp(-10.0, 0.0, vmax)
        assert v3 == 0.0
