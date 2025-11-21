#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Numerische Hilfsfunktionen für mathematische Operationen."""

from __future__ import annotations

import math


def deg_to_rad(degrees: float) -> float:
    """Konvertiert Winkel von Grad zu Radiant."""
    return math.radians(degrees)


def rad_to_deg(radians: float) -> float:
    """Konvertiert Winkel von Radiant zu Grad."""
    return math.degrees(radians)


def wrap_angle_deg(angle: float, lower: float = -180.0, upper: float = 180.0) -> float:
    """
    Normalisiert Winkel in Grad auf periodischen Bereich [lower, upper).

    Standard: [-180°, 180°).
    """
    if lower >= upper:
        raise ValueError(f"lower ({lower}) must be strictly less than upper ({upper})")

    period = upper - lower
    normalized = (angle - lower) % period + lower

    return normalized


def wrap_angle_rad(angle: float) -> float:
    """Normalisiert Winkel in Radiant auf [-π, π)."""
    period = 2 * math.pi
    normalized = (angle + math.pi) % period - math.pi
    return normalized


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Begrenzt Wert auf Bereich [min_value, max_value]."""
    if min_value > max_value:
        raise ValueError(f"min_value ({min_value}) must not be greater than max_value ({max_value})")

    return max(min_value, min(value, max_value))


