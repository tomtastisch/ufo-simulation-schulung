#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-Typen für deklarative Steuerung."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from ..state.state import UfoState


class CommandType(Enum):
    """
    Typ der Steuerkommandos.
    
    Definiert alle verfügbaren Command-Typen für die deklarative
    Autopilot-Steuerung der Simulation.
    """
    
    SET_STATE = auto()  # Setze State-Attribut direkt
    WAIT_CONDITION = auto()  # Warte auf Bedingung
    EXECUTE_FUNC = auto()  # Führe Funktion aus
    LOG_MESSAGE = auto()  # Gib Nachricht aus


@dataclass
class Command:
    """
    Einzelnes Steuerkommando.

    Statt Warteschleifen definierst du eine Sequenz von Commands.
    Die Simulation führt diese automatisch aus.
    
    Attributes:
        type: Der Typ des Commands (SET_STATE, WAIT_CONDITION, etc.)
        target: State-Attribut (für SET_STATE)
        value: Wert (für SET_STATE)
        condition: Bedingung (für WAIT_CONDITION) - nimmt UfoState als Parameter
        func: Funktion (für EXECUTE_FUNC)
        message: Nachricht (für LOG_MESSAGE)
        timeout: Timeout für WAIT_CONDITION in Sekunden
        
    Note:
        UfoState wird nur über TYPE_CHECKING importiert, um Importzyklen
        zwischen command/ und state/ zu vermeiden. Die condition Callable
        verwendet String-Annotation für den UfoState-Parameter.
    """
    
    type: CommandType
    target: Optional[str] = None  # State-Attribut (für SET_STATE)
    value: Optional[Any] = None  # Wert (für SET_STATE)
    condition: Optional[Callable[["UfoState"], bool]] = None  # Bedingung (für WAIT_CONDITION)
    func: Optional[Callable[[], Any]] = None  # Funktion (für EXECUTE_FUNC)
    message: Optional[str] = None  # Nachricht (für LOG_MESSAGE)
    timeout: Optional[float] = None  # Timeout für WAIT_CONDITION
