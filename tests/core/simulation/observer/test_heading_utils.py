#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-Tests für Heading-Hilfsfunktionen (Wrap-around-Logik).

Testet die normalize_heading_delta Funktion isoliert.
"""

from core.simulation.observer import normalize_heading_delta


class TestNormalizeHeadingDelta:
    """Tests für die Heading-Delta-Normalisierung (Wrap-around)."""

    def test_no_wrap_around_positive_small(self):
        """Kleine positive Differenz ohne Wrap-around."""
        delta = normalize_heading_delta(45.0)
        assert delta == 45.0

    def test_no_wrap_around_negative_small(self):
        """Kleine negative Differenz ohne Wrap-around."""
        delta = normalize_heading_delta(-45.0)
        assert delta == -45.0

    def test_no_wrap_around_at_boundary_positive(self):
        """Differenz genau bei +180° (Grenzfall)."""
        delta = normalize_heading_delta(180.0)
        assert delta == 180.0

    def test_no_wrap_around_at_boundary_negative(self):
        """Differenz genau bei -180° (Grenzfall)."""
        delta = normalize_heading_delta(-180.0)
        assert delta == -180.0

    def test_wrap_around_positive_to_negative(self):
        """Wrap-around von positiv zu negativ (350° → 10° = +20°)."""
        # Delta roh: 10 - 350 = -340
        # Normalisiert: -340 + 360 = +20
        delta = normalize_heading_delta(-340.0)
        assert delta == 20.0

    def test_wrap_around_negative_to_positive(self):
        """Wrap-around von negativ zu positiv (10° → 350° = -20°)."""
        # Delta roh: 350 - 10 = +340
        # Normalisiert: +340 - 360 = -20
        delta = normalize_heading_delta(340.0)
        assert delta == -20.0

    def test_wrap_around_just_over_180(self):
        """Knapp über +180° triggert Wrap-around."""
        # 181° → -179°
        delta = normalize_heading_delta(181.0)
        assert delta == -179.0

    def test_wrap_around_just_under_minus_180(self):
        """Knapp unter -180° triggert Wrap-around."""
        # -181° → +179°
        delta = normalize_heading_delta(-181.0)
        assert delta == 179.0

    def test_full_circle_positive(self):
        """Voller Kreis positiv (360°) wird zu 0°."""
        delta = normalize_heading_delta(360.0)
        assert delta == 0.0

    def test_full_circle_negative(self):
        """Voller Kreis negativ (-360°) wird zu 0°."""
        delta = normalize_heading_delta(-360.0)
        assert delta == 0.0

    def test_multiple_wraps_positive(self):
        """Mehrfache Umläufe positiv (540° = 360° + 180°)."""
        # 540° - 360° = 180°
        delta = normalize_heading_delta(540.0)
        assert delta == 180.0

    def test_multiple_wraps_negative(self):
        """Mehrfache Umläufe negativ (-540° = -360° - 180°)."""
        # -540° + 360° = -180°
        delta = normalize_heading_delta(-540.0)
        assert delta == -180.0

    def test_realistic_scenario_right_turn(self):
        """Realistisches Szenario: Rechtskurve von 5° auf 355°."""
        # Delta: 355 - 5 = 350° (roh)
        # Normalisiert: 350 - 360 = -10° (Rechtskurve)
        delta = normalize_heading_delta(350.0)
        assert delta == -10.0

    def test_realistic_scenario_left_turn(self):
        """Realistisches Szenario: Linkskurve von 355° auf 5°."""
        # Delta: 5 - 355 = -350° (roh)
        # Normalisiert: -350 + 360 = +10° (Linkskurve)
        delta = normalize_heading_delta(-350.0)
        assert delta == 10.0

    def test_zero_delta(self):
        """Keine Änderung (0°)."""
        delta = normalize_heading_delta(0.0)
        assert delta == 0.0

    def test_symmetry_positive_negative(self):
        """Symmetrie: +170° und -170° bleiben unverändert."""
        assert normalize_heading_delta(170.0) == 170.0
        assert normalize_heading_delta(-170.0) == -170.0

    def test_output_range_bounds(self):
        """Ausgabe ist immer im Bereich [-180, 180]."""
        test_values = [-540, -360, -340, -181, -180, -45, 0, 45, 180, 181, 340, 360, 540]
        for value in test_values:
            result = normalize_heading_delta(value)
            msg = f"normalize_heading_delta({value}) = {result} außerhalb [-180, 180]"
            assert -180 <= result <= 180, msg


class TestNormalizeHeadingDeltaEdgeCases:
    """Edge-Cases und Spezialfälle."""

    def test_very_large_positive(self):
        """Sehr große positive Werte."""
        # 720° = 2 * 360° → 0°
        delta = normalize_heading_delta(720.0)
        assert delta == 0.0

    def test_very_large_negative(self):
        """Sehr große negative Werte."""
        # -720° = -2 * 360° → 0°
        delta = normalize_heading_delta(-720.0)
        assert delta == 0.0

    def test_fractional_degrees(self):
        """Dezimalwerte funktionieren korrekt."""
        delta = normalize_heading_delta(45.5)
        assert delta == 45.5

        delta = normalize_heading_delta(-45.5)
        assert delta == -45.5

        # Wrap-around mit Dezimalstellen
        delta = normalize_heading_delta(190.5)
        assert delta == -169.5

    def test_consistency_with_abs(self):
        """Absolute Werte sind konsistent."""
        # ±350° sollten beide zu ±10° werden (symmetrisch)
        pos = normalize_heading_delta(350.0)
        neg = normalize_heading_delta(-350.0)
        assert abs(pos) == abs(neg) == 10.0
        assert pos == -10.0
        assert neg == 10.0
