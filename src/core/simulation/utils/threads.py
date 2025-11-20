#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thread-Synchronisation-Utilities für die UFO-Simulation."""

from __future__ import annotations

# Re-export synchronized decorator from existing implementation
from ..synchronization.instance_lock import synchronized

__all__ = ['synchronized']

