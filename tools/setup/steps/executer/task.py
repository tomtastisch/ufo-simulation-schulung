"""
Generische Task-Typen für BatchExecutor.

Dieser Modul definiert die Kern-Abstraktionen für Task-basierte
parallele Ausführung, unabhängig von der konkreten Domäne.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeAlias, TypeVar

TObj = TypeVar("TObj")
TResult = TypeVar("TResult")

TaskCallable: TypeAlias = Callable[[TObj], TResult]


@dataclass(slots=True, frozen=True)
class Task(Generic[TObj, TResult]):
    """
    Generische Arbeitseinheit für BatchExecutor.

    Typ-Parameter:
        TObj: Typ des auszuführenden Objekts (z.B. TestFile, Job-Descriptor)
        TResult: Typ des Ergebnisses (z.B. TestResult, Exit-Code)

    Attribute:
        task_id: Eindeutige, stabile ID (deterministisch aus obj erzeugt)
        display_name: Menschenlesbarer Name für UI
        obj: Das auszuführende Objekt
        callable: Die Funktion, die obj → result transformiert
    """

    task_id: str
    display_name: str
    obj: TObj
    callable: TaskCallable[TObj, TResult]

    def run(self) -> TResult:
        """
        Führt den Task aus und liefert das Ergebnis.

        Returns:
            Das Ergebnis der Callable-Ausführung

        Raises:
            Beliebige Exceptions, die callable(obj) werfen kann
        """
        return self.callable(self.obj)
