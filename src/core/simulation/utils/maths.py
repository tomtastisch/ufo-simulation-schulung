"""
Numerische Hilfsfunktionen für mathematische Operationen.

Dieses Modul stellt generische, wiederverwendbare mathematische Hilfsfunktionen
bereit, die keine Abhängigkeiten zu Simulationslogik haben.

Funktionen:
    deg_to_rad: Konvertiert Grad in Radiant
    rad_to_deg: Konvertiert Radiant in Grad
    wrap_angle_deg: Normalisiert Winkel in Grad auf einen Bereich
    wrap_angle_rad: Normalisiert Winkel in Radiant auf [-π, π]
    clamp: Begrenzt einen Wert auf einen Minimal- und Maximalwert

Architektur:
    - Reine Funktionen ohne Seiteneffekte
    - Keine Imports von Simulationslogik (UfoState, UfoSim, SimulationConfig)
    - Nur math-Modul aus Standardbibliothek als Dependency
    - Vollständige Type Hints für alle Parameter und Rückgabewerte
    - Physikalisch/mathematisch korrekte Implementierungen

Verwendung:
    from core.simulation.utils.maths import deg_to_rad, clamp

    angle_rad = deg_to_rad(45.0)
    normalized = wrap_angle_deg(370.0)  # -> 10.0
    limited = clamp(150.0, 0.0, 100.0)  # -> 100.0
"""

from __future__ import annotations

import math


def deg_to_rad(degrees: float) -> float:
    """
    Konvertiert Winkel von Grad zu Radiant.

    Nutzt die präzise math.radians Funktion aus der Standardbibliothek.

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

    Nutzt die präzise math.degrees Funktion aus der Standardbibliothek.

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
    Normalisiert einen Winkel in Grad auf einen periodischen Bereich.

    Wickelt Winkel um den Bereich [lower, upper) herum. Standardmäßig wird
    auf den Bereich [-180, 180) normalisiert, aber andere Bereiche wie
    [0, 360) sind ebenfalls möglich.

    Die Funktion ist numerisch stabil und funktioniert auch mit sehr großen
    Winkeln korrekt.

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
        >>> wrap_angle_deg(180.0)
        180.0
        >>> wrap_angle_deg(181.0)
        -179.0
        >>> wrap_angle_deg(-181.0)
        179.0
        >>> wrap_angle_deg(370.0, 0.0, 360.0)
        10.0
        >>> wrap_angle_deg(720.0)
        0.0
    """
    if lower >= upper:
        raise ValueError(f"lower ({lower}) must be strictly less than upper ({upper})")

    # Bereichsgröße
    period = upper - lower

    # Normalisierung mittels Modulo
    # Verschiebe zuerst in [0, period), dann zurück in [lower, upper)
    normalized = (angle - lower) % period + lower

    return normalized


def wrap_angle_rad(angle: float) -> float:
    """
    Normalisiert einen Winkel in Radiant auf [-π, π].

    Wickelt Winkel um den Bereich [-π, π) herum. Dies ist die Standard-
    Normalisierung für Winkel in Radiant in der Physik.

    Args:
        angle: Zu normalisierender Winkel in Radiant

    Returns:
        Normalisierter Winkel im Bereich [-π, π)

    Examples:
        >>> wrap_angle_rad(0.0)
        0.0
        >>> abs(wrap_angle_rad(math.pi) - math.pi) < 1e-10
        True
        >>> abs(wrap_angle_rad(3 * math.pi) - math.pi) < 1e-10
        True
        >>> abs(wrap_angle_rad(-3 * math.pi) - math.pi) < 1e-10
        True
    """
    # Nutze wrap_angle_deg Implementierung für Konsistenz
    # Konvertiere erst zu Grad, normalisiere, dann zurück zu Radiant
    angle_deg = rad_to_deg(angle)
    normalized_deg = wrap_angle_deg(angle_deg, -180.0, 180.0)
    return deg_to_rad(normalized_deg)


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Begrenzt einen Wert auf einen Minimal- und Maximalwert.

    Stellt sicher, dass der Rückgabewert im Bereich [min_value, max_value]
    liegt. Wenn value kleiner als min_value ist, wird min_value zurückgegeben.
    Wenn value größer als max_value ist, wird max_value zurückgegeben.
    Andernfalls wird value unverändert zurückgegeben.

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
        >>> clamp(10.0, 0.0, 10.0)
        10.0
    """
    if min_value > max_value:
        raise ValueError(f"min_value ({min_value}) must not be greater than max_value ({max_value})")

    return max(min_value, min(value, max_value))
