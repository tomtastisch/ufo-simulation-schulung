#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-System für deklarative UFO-Steuerung.

## Überblick

Das Command-System ermöglicht eine deklarative, ereignisbasierte Steuerung der
UFO-Simulation ohne aktive Warteschleifen oder Polling. Statt imperativen
while-Schleifen definieren Autopiloten eine Sequenz von Commands, die von der
Simulation automatisch ausgeführt werden.

## Hauptbestandteile

### types.py (CommandType, Command)
Zentrale Typdefinitionen für das Command-System:
- `CommandType`: Enum aller verfügbaren Command-Typen
- `Command`: Dataclass für einzelne Steuerkommandos

## Architektur

### Import-Hierarchie
- `command.types` → keine Simulationselemente (nur typing)
- `command.types` verwendet TYPE_CHECKING für UfoState-Referenzen
- Kein direkter Import von state zur Laufzeit (nur String-Annotationen)

### Verantwortlichkeiten
- **types.py**: Definiert Struktur und Typen der Commands
- **queue.py** (geplant): Verwaltet Command-Sequenzen
- **executor.py** (geplant): Führt Commands gegen StateManager aus

## Verwendung

```python
from core.simulation.command import CommandType, Command

# Command direkt erstellen
cmd = Command(
    type=CommandType.SET_STATE,
    target='i',
    value=90
)

# Command mit Bedingung
cmd = Command(
    type=CommandType.WAIT_CONDITION,
    condition=lambda s: s.z >= 10.0,
    timeout=5.0
)
```

## Design-Prinzipien

1. **Deklarativ statt imperativ**: Commands beschreiben "was", nicht "wie"
2. **Entkopplung**: Keine direkten Abhängigkeiten zu StateManager oder PhysicsEngine
3. **Typsicherheit**: Vollständige Type-Hints mit TYPE_CHECKING für Zyklusvermeidung
4. **Thread-Safety**: Wird durch CommandQueue und CommandExecutor gewährleistet

## Erweiterbarkeit

Neue CommandType-Werte können einfach zur Enum hinzugefügt werden.
Die Command-Dataclass ist erweiterbar für zusätzliche Parameter.
"""

from .types import Command, CommandType

__all__ = [
    "Command",
    "CommandType",
]
