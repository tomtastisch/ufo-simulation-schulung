#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validierungsfunktionen für Wertebereichs-Prüfungen."""

from __future__ import annotations


def validate_range(value: float, min_val: float, max_val: float, name: str) -> None:
    """
    Validiert Wertebereich, wirft ValueError bei Verletzung.

    Args:
        name: Parametername für Fehlermeldung
    """
    if value < min_val or value > max_val:
        raise ValueError(f"{name} muss zwischen {min_val} und {max_val} liegen, ist aber {value}")


def is_in_range(value: float, min_val: float, max_val: float) -> bool:
    """Prüft ob Wert innerhalb [min_val, max_val] liegt."""
    return min_val <= value <= max_val


