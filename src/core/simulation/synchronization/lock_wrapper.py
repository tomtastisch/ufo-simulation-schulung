#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Öffentliche API für Lock-Wrapper-Utilities."""

from __future__ import annotations

from ._lock_wrapper import (
    _acquire_lock as acquire_lock,
    create_lock_wrapper,
)

__all__ = [
    "acquire_lock",
    "create_lock_wrapper",
]
