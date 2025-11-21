#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometrische Transformationsfunktionen für 3D-Koordinaten."""

from __future__ import annotations

import math

EPSILON_NEAR_ORIGIN = 1e-10


def cartesian_to_spherical(x: float, y: float, z: float) -> tuple[float, float, float]:
    """
    Konvertiert kartesische zu sphärischen Koordinaten (r, theta, phi).

    - r: Radius (Abstand vom Ursprung)
    - theta: Polarwinkel von z-Achse [0, π]
    - phi: Azimutwinkel von x-Achse [-π, π]
    """
    r = math.sqrt(x * x + y * y + z * z)

    if r < EPSILON_NEAR_ORIGIN:
        return 0.0, 0.0, 0.0

    theta = math.acos(z / r)
    phi = math.atan2(y, x)

    return r, theta, phi


def spherical_to_cartesian(r: float, theta: float, phi: float) -> tuple[float, float, float]:
    """
    Konvertiert sphärische zu kartesischen Koordinaten (x, y, z).

    - r: Radius
    - theta: Polarwinkel in Radiant
    - phi: Azimutwinkel in Radiant
    """
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)

    x = r * sin_theta * cos_phi
    y = r * sin_theta * sin_phi
    z = r * cos_theta

    return x, y, z


