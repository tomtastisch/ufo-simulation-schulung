#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validierungsfunktionen für Wertebereichs-Prüfungen."""

from __future__ import annotations


def validate_range(value: float, min_val: float, max_val: float, name: str) -> None:
    """
    Validiert, dass ein Wert innerhalb eines Bereichs liegt.

    Wirft ValueError wenn der Wert außerhalb des zulässigen Bereichs liegt.

    Args:
        value: Zu validierender Wert
        min_val: Minimalwert (inklusiv)
        max_val: Maximalwert (inklusiv)
        name: Name des Parameters für Fehlermeldung

    Raises:
        ValueError: Wenn value < min_val oder value > max_val

    Examples:
        >>> validate_range(5.0, 0.0, 10.0, "speed")  # OK, kein Fehler
        >>> validate_range(-1.0, 0.0, 10.0, "speed")  # doctest: +SKIP
        Traceback (most recent call last):
        ValueError: speed muss zwischen 0.0 und 10.0 liegen, ist aber -1.0
    """
    if value < min_val or value > max_val:
        raise ValueError(f"{name} muss zwischen {min_val} und {max_val} liegen, ist aber {value}")


def is_in_range(value: float, min_val: float, max_val: float) -> bool:
    """
    Prüft, ob ein Wert innerhalb eines Bereichs liegt.

    Args:
        value: Zu prüfender Wert
        min_val: Minimalwert (inklusiv)
        max_val: Maximalwert (inklusiv)

    Returns:
        True wenn min_val <= value <= max_val, sonst False

    Examples:
        >>> is_in_range(5.0, 0.0, 10.0)
        True
        >>> is_in_range(-1.0, 0.0, 10.0)
        False
        >>> is_in_range(10.0, 0.0, 10.0)
        True
    """
    return min_val <= value <= max_val
