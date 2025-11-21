"""
Unit-Tests für das utils.geometry Modul.

Testet geometrische Transformationsfunktionen für 3D-Koordinaten.
"""

from __future__ import annotations

import math

from core.simulation.utils.geometry import cartesian_to_spherical, spherical_to_cartesian


class TestCartesianToSpherical:
    """Tests für cartesian_to_spherical Funktion."""

    def test_origin(self):
        """Ursprung sollte (0, 0, 0) ergeben."""
        r, theta, phi = cartesian_to_spherical(0.0, 0.0, 0.0)
        assert r == 0.0
        assert theta == 0.0
        assert phi == 0.0

    def test_positive_z_axis(self):
        """Punkt auf positiver z-Achse."""
        r, theta, phi = cartesian_to_spherical(0.0, 0.0, 1.0)
        assert abs(r - 1.0) < 1e-10
        assert abs(theta - 0.0) < 1e-10  # θ = 0 für +z

    def test_negative_z_axis(self):
        """Punkt auf negativer z-Achse."""
        r, theta, phi = cartesian_to_spherical(0.0, 0.0, -1.0)
        assert abs(r - 1.0) < 1e-10
        assert abs(theta - math.pi) < 1e-10  # θ = π für -z

    def test_positive_x_axis(self):
        """Punkt auf positiver x-Achse."""
        r, theta, phi = cartesian_to_spherical(1.0, 0.0, 0.0)
        assert abs(r - 1.0) < 1e-10
        assert abs(theta - math.pi / 2) < 1e-10  # θ = π/2 für xy-Ebene
        assert abs(phi - 0.0) < 1e-10  # φ = 0 für +x

    def test_positive_y_axis(self):
        """Punkt auf positiver y-Achse."""
        r, theta, phi = cartesian_to_spherical(0.0, 1.0, 0.0)
        assert abs(r - 1.0) < 1e-10
        assert abs(theta - math.pi / 2) < 1e-10
        assert abs(phi - math.pi / 2) < 1e-10  # φ = π/2 für +y

    def test_general_point(self):
        """Allgemeiner Punkt im Raum."""
        r, theta, phi = cartesian_to_spherical(1.0, 1.0, 1.0)
        expected_r = math.sqrt(3.0)
        assert abs(r - expected_r) < 1e-10

    def test_large_coordinates(self):
        """Große Koordinaten sollten korrekt konvertiert werden."""
        r, theta, phi = cartesian_to_spherical(100.0, 0.0, 0.0)
        assert abs(r - 100.0) < 1e-8


class TestSphericalToCartesian:
    """Tests für spherical_to_cartesian Funktion."""

    def test_origin(self):
        """r=0 sollte Ursprung ergeben."""
        x, y, z = spherical_to_cartesian(0.0, 0.0, 0.0)
        assert abs(x) < 1e-10
        assert abs(y) < 1e-10
        assert abs(z) < 1e-10

    def test_positive_z_axis(self):
        """θ=0 sollte positive z-Achse ergeben."""
        x, y, z = spherical_to_cartesian(1.0, 0.0, 0.0)
        assert abs(x - 0.0) < 1e-10
        assert abs(y - 0.0) < 1e-10
        assert abs(z - 1.0) < 1e-10

    def test_negative_z_axis(self):
        """θ=π sollte negative z-Achse ergeben."""
        x, y, z = spherical_to_cartesian(1.0, math.pi, 0.0)
        assert abs(x - 0.0) < 1e-10
        assert abs(y - 0.0) < 1e-10
        assert abs(z - (-1.0)) < 1e-10

    def test_positive_x_axis(self):
        """θ=π/2, φ=0 sollte positive x-Achse ergeben."""
        x, y, z = spherical_to_cartesian(1.0, math.pi / 2, 0.0)
        assert abs(x - 1.0) < 1e-10
        assert abs(y - 0.0) < 1e-10
        assert abs(z - 0.0) < 1e-10

    def test_positive_y_axis(self):
        """θ=π/2, φ=π/2 sollte positive y-Achse ergeben."""
        x, y, z = spherical_to_cartesian(1.0, math.pi / 2, math.pi / 2)
        assert abs(x - 0.0) < 1e-10
        assert abs(y - 1.0) < 1e-10
        assert abs(z - 0.0) < 1e-10

    def test_large_radius(self):
        """Großer Radius sollte korrekt skaliert werden."""
        x, y, z = spherical_to_cartesian(100.0, math.pi / 2, 0.0)
        assert abs(x - 100.0) < 1e-8


class TestRoundtripConversion:
    """Tests für Hin- und Rück-Konvertierung."""

    def test_roundtrip_cartesian_spherical_cartesian(self):
        """Kartesisch → Sphärisch → Kartesisch sollte Original ergeben."""
        original_x, original_y, original_z = 3.0, 4.0, 5.0

        # Hin
        r, theta, phi = cartesian_to_spherical(original_x, original_y, original_z)

        # Zurück
        x, y, z = spherical_to_cartesian(r, theta, phi)

        assert abs(x - original_x) < 1e-10
        assert abs(y - original_y) < 1e-10
        assert abs(z - original_z) < 1e-10

    def test_roundtrip_spherical_cartesian_spherical(self):
        """Sphärisch → Kartesisch → Sphärisch sollte Original ergeben."""
        original_r = 5.0
        original_theta = math.pi / 4
        original_phi = math.pi / 3

        # Hin
        x, y, z = spherical_to_cartesian(original_r, original_theta, original_phi)

        # Zurück
        r, theta, phi = cartesian_to_spherical(x, y, z)

        assert abs(r - original_r) < 1e-10
        assert abs(theta - original_theta) < 1e-10
        assert abs(phi - original_phi) < 1e-10

    def test_multiple_points_roundtrip(self):
        """Mehrere Punkte sollten Roundtrip korrekt durchlaufen."""
        test_points = [
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (1.0, 1.0, 1.0),
            (-1.0, -1.0, -1.0),
        ]

        for orig_x, orig_y, orig_z in test_points:
            r, theta, phi = cartesian_to_spherical(orig_x, orig_y, orig_z)
            x, y, z = spherical_to_cartesian(r, theta, phi)

            assert abs(x - orig_x) < 1e-10
            assert abs(y - orig_y) < 1e-10
            assert abs(z - orig_z) < 1e-10
