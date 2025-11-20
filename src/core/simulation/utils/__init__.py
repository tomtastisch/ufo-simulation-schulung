"""
Lock-Decorators für die UFO-Simulation.

Dieses Paket enthält wiederverwendbare Decorators für Thread-Sicherheit,
die keine direkten Abhängigkeiten zu den Simulationsklassen haben.

Verfügbare Decorators:
    - `synchronized`: Für Instanzmethoden (verwendet `self._lock`)
    - `synchronized_module`: Für Modul-Level-Funktionen (expliziter Lock-Parameter)

Verwendung:

    **Instanzmethoden:**
        >>> from core.simulation.utils import synchronized
        >>> class MyClass:
        ...     def __init__(self):
        ...         self._lock = threading.RLock()
        ...     @synchronized
        ...     def method(self): pass

    **Modul-Level-Funktionen:**
        >>> from core.simulation.utils import synchronized_module
        >>> _lock = threading.RLock()
        >>> @synchronized_module(_lock)
        ... def function(): pass
"""
import threading

from .instance_lock import synchronized
from .module_lock import synchronized_module

__all__ = [
    "synchronized",
    "synchronized_module",
]
