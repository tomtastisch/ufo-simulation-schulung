#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Numerische Hilfsfunktionen für mathematische Operationen."""

from __future__ import annotations

import math


def deg_to_rad(degrees: float) -> float:
    """
    Konvertiert Winkel von Grad zu Radiant.

    Nutzt math.radians aus der Standardbibliothek für präzise Konvertierung.

    Args:
        degrees: Winkel in Grad

    Returns:
        Winkel in Radiant

    Examples:
        >>> deg_to_rad(0.0)
        0.0
        >>> abs(deg_to_rad(180.0) - math.pi) < 1e-10
        True
        >>> abs(deg_to_rad(90.0) - math.pi/2) < 1e-10
        True
    """
    return math.radians(degrees)


def rad_to_deg(radians: float) -> float:
    """
    Konvertiert Winkel von Radiant zu Grad.

    Nutzt math.degrees aus der Standardbibliothek für präzise Konvertierung.

    Args:
        radians: Winkel in Radiant

    Returns:
        Winkel in Grad

    Examples:
        >>> rad_to_deg(0.0)
        0.0
        >>> abs(rad_to_deg(math.pi) - 180.0) < 1e-10
        True
        >>> abs(rad_to_deg(math.pi/2) - 90.0) < 1e-10
        True
    """
    return math.degrees(radians)


def wrap_angle_deg(angle: float, lower: float = -180.0, upper: float = 180.0) -> float:
    """
    Normalisiert Winkel in Grad auf periodischen Bereich.

    Wickelt Winkel um [lower, upper) herum. Standard: [-180°, 180°).
    Numerisch stabil auch für sehr große Winkel.

    Args:
        angle: Zu normalisierender Winkel in Grad
        lower: Untere Grenze des Zielbereichs (inklusiv)
        upper: Obere Grenze des Zielbereichs (exklusiv)

    Returns:
        Normalisierter Winkel im Bereich [lower, upper)

    Raises:
        ValueError: Wenn lower >= upper

    Examples:
        >>> wrap_angle_deg(0.0)
        0.0
        >>> wrap_angle_deg(181.0)
        -179.0
        >>> wrap_angle_deg(370.0, 0.0, 360.0)
        10.0
    """
    if lower >= upper:
        raise ValueError(f"lower ({lower}) must be strictly less than upper ({upper})")

    period = upper - lower
    normalized = (angle - lower) % period + lower

    return normalized


def wrap_angle_rad(angle: float) -> float:
    """
    Normalisiert Winkel in Radiant auf [-π, π).

    Standard-Normalisierung für Winkel in Radiant in der Physik.

    Args:
        angle: Zu normalisierender Winkel in Radiant

    Returns:
        Normalisierter Winkel im Bereich [-π, π)

    Examples:
        >>> wrap_angle_rad(0.0)
        0.0
        >>> abs(wrap_angle_rad(3 * math.pi) - (-math.pi)) < 1e-10
        True
    """
    angle_deg = rad_to_deg(angle)
    normalized_deg = wrap_angle_deg(angle_deg, -180.0, 180.0)
    return deg_to_rad(normalized_deg)


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Begrenzt Wert auf Minimal- und Maximalwert.

    Stellt sicher, dass Rückgabewert in [min_value, max_value] liegt.

    Args:
        value: Zu begrenzender Wert
        min_value: Minimalwert (untere Grenze)
        max_value: Maximalwert (obere Grenze)

    Returns:
        Begrenzter Wert im Bereich [min_value, max_value]

    Raises:
        ValueError: Wenn min_value > max_value

    Examples:
        >>> clamp(5.0, 0.0, 10.0)
        5.0
        >>> clamp(-5.0, 0.0, 10.0)
        0.0
        >>> clamp(15.0, 0.0, 10.0)
        10.0
    """
    if min_value > max_value:
        raise ValueError(f"min_value ({min_value}) must not be greater than max_value ({max_value})")

    return max(min_value, min(value, max_value))
