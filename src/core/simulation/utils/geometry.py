#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometrische Transformationsfunktionen für 3D-Koordinaten."""

from __future__ import annotations

import math


def cartesian_to_spherical(x: float, y: float, z: float) -> tuple[float, float, float]:
    """
    Konvertiert kartesische zu sphärischen Koordinaten.

    Sphärische Koordinaten: (r, theta, phi)
    - r: Radius (Abstand vom Ursprung)
    - theta: Polarwinkel von z-Achse [0, π]
    - phi: Azimutwinkel von x-Achse [-π, π]

    Args:
        x: X-Koordinate
        y: Y-Koordinate
        z: Z-Koordinate

    Returns:
        Tuple (r, theta, phi) in sphärischen Koordinaten

    Examples:
        >>> r, theta, phi = cartesian_to_spherical(0.0, 0.0, 1.0)
        >>> abs(r - 1.0) < 1e-10
        True
        >>> abs(theta - 0.0) < 1e-10
        True
    """
    r = math.sqrt(x * x + y * y + z * z)

    if r < 1e-10:  # Sehr nahe am Ursprung
        return 0.0, 0.0, 0.0

    theta = math.acos(z / r)
    phi = math.atan2(y, x)

    return r, theta, phi


def spherical_to_cartesian(r: float, theta: float, phi: float) -> tuple[float, float, float]:
    """
    Konvertiert sphärische zu kartesischen Koordinaten.

    Sphärische Koordinaten: (r, theta, phi)
    - r: Radius (Abstand vom Ursprung)
    - theta: Polarwinkel von z-Achse [0, π]
    - phi: Azimutwinkel von x-Achse [-π, π]

    Args:
        r: Radius
        theta: Polarwinkel in Radiant
        phi: Azimutwinkel in Radiant

    Returns:
        Tuple (x, y, z) in kartesischen Koordinaten

    Examples:
        >>> x, y, z = spherical_to_cartesian(1.0, 0.0, 0.0)
        >>> abs(x - 0.0) < 1e-10 and abs(y - 0.0) < 1e-10 and abs(z - 1.0) < 1e-10
        True
    """
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)

    x = r * sin_theta * cos_phi
    y = r * sin_theta * sin_phi
    z = r * cos_theta

    return x, y, z
