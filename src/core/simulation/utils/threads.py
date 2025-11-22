#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread-Synchronisation-Utilities für die UFO-Simulation.

DEPRECATED: Dieses Modul existiert nur noch für Rückwärtskompatibilität.
Nutze stattdessen direkt: from core.simulation.synchronization import synchronized

Wird in einer zukünftigen Version entfernt.
"""

from __future__ import annotations

import warnings

# Re-export synchronized decorator from synchronization package
from ..synchronization import synchronized

# Warnung beim Import ausgeben
warnings.warn(
    "utils.threads ist deprecated. "
    "Nutze stattdessen: from core.simulation.synchronization import synchronized",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ['synchronized']
