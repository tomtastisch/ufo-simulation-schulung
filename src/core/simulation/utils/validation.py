#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validierungsfunktionen für Wertebereichs-Prüfungen."""

from __future__ import annotations


def validate_range(value: float, min_val: float, max_val: float, name: str) -> None:
    """Validiert, ob ein Wert innerhalb eines definierten Wertebereichs liegt.

    Liegt der übergebene Wert außerhalb des Intervalls
    ``[min_val, max_val]``, wird ein ``ValueError`` mit einer
    sprechenden Fehlermeldung ausgelöst.

    Args:
        value: Zu prüfender numerischer Wert.
        min_val: Untere (inklusive) Grenze des gültigen Wertebereichs.
        max_val: Obere (inklusive) Grenze des gültigen Wertebereichs.
        name: Parametername oder Bezeichner, der in der Fehlermeldung
            verwendet wird.

    Raises:
        ValueError: Wenn ``value`` kleiner als ``min_val`` oder größer
            als ``max_val`` ist.
    """
    if value < min_val or value > max_val:
        raise ValueError(
            f"{name} muss zwischen {min_val} und {max_val} liegen, ist aber {value}"
        )


def is_in_range(value: float, min_val: float, max_val: float) -> bool:
    """Prüft, ob ein Wert innerhalb eines geschlossenen Wertebereichs liegt.

    Args:
        value: Zu prüfender numerischer Wert.
        min_val: Untere (inklusive) Grenze des gültigen Wertebereichs.
        max_val: Obere (inklusive) Grenze des gültigen Wertebereichs.

    Returns:
        True, wenn ``value`` innerhalb des Intervalls
        ``[min_val, max_val]`` liegt, sonst False.
    """
    return min_val <= value <= max_val


