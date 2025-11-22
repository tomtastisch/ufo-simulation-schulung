#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalisierung von Heading-Differenzen mit Wrap-around-Behandlung.

Dieses Modul stellt Hilfsfunktionen zur Normalisierung von Winkeldifferenzen
auf den Bereich [-180, 180] Grad bereit.
"""

from __future__ import annotations


def normalize_heading_delta(delta_d: float) -> float:
    """
    Normalisiert die Heading-Differenz auf den Bereich [-180, 180].

    Behandelt Wrap-around-Fälle korrekt, z.B.:
    - 350° → 10° ergibt +20° (nicht +340°)
    - 10° → 350° ergibt -20° (nicht -340°)

    Unterstützt auch mehrfache Umläufe (z.B. 720° → 0°).

    Args:
        delta_d: Rohdifferenz zwischen zwei Heading-Werten in Grad

    Returns:
        Normalisierte Differenz im Bereich [-180, 180] Grad
        (bei exakt ±180° wird -180° bevorzugt)
    """
    # Auf [-180, 180] normalisieren mit Modulo-Arithmetik
    delta_d = delta_d % 360

    # Bei exakt 180° bevorzugen wir -180° für Konsistenz
    if delta_d == 180.0:
        return -180.0

    if delta_d > 180:
        delta_d -= 360
    elif delta_d < -180:
        delta_d += 360

    return delta_d
