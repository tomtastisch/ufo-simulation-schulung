#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-System für deklarative UFO-Steuerung.

Ermöglicht eine deklarative, ereignisbasierte Steuerung der UFO-Simulation
ohne aktive Warteschleifen oder Polling. Statt imperativen while-Schleifen
definieren Autopiloten eine Sequenz von Commands, die von der Simulation
automatisch ausgeführt werden.

Komponenten:
    - CommandType: Enum aller verfügbaren Command-Typen
    - Command: Dataclass für einzelne Steuerkommandos
    - CommandQueue (geplant): Verwaltet Command-Sequenzen
    - CommandExecutor (geplant): Führt Commands gegen StateManager aus

Architektur:
    - command.types → keine Simulationselemente (nur typing)
    - command.types verwendet TYPE_CHECKING für UfoState-Referenzen
    - Kein direkter Import von state zur Laufzeit (nur String-Annotationen)

Design-Prinzipien:
    - Deklarativ statt imperativ: Commands beschreiben "was", nicht "wie"
    - Entkopplung: Keine direkten Abhängigkeiten zu StateManager oder PhysicsEngine
    - Typsicherheit: Vollständige Type-Hints mit TYPE_CHECKING für Zyklusvermeidung
    - Thread-Safety: Wird durch CommandQueue und CommandExecutor gewährleistet
"""

from .types import Command, CommandType

__all__ = [
    "Command",
    "CommandType",
]
