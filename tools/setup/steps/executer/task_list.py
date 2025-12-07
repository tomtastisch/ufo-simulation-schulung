"""
Task-Listen-Builder für BatchExecutor.

Erzeugt aus einer Sequenz von Objekten und einem gemeinsamen Callable
eine Liste von Task[TObj, TResult]-Instanzen.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import TypeVar

from tools.setup.steps.executer.task import Task, TaskCallable

TObj = TypeVar("TObj")
TResult = TypeVar("TResult")

IdBuilder: type = Callable[[TObj], str]
NameBuilder: type = Callable[[TObj], str]


def build_task_list(
        objects: Iterable[TObj],
        call: TaskCallable[TObj, TResult],
        id_builder: IdBuilder,
        name_builder: NameBuilder,
) -> Sequence[Task[TObj, TResult]]:
    """
    Erzeugt eine Task-Liste aus Objekten und einem gemeinsamen Callable.

    Für alle Objekte wird dasselbe Callable verwendet, nur das zugrundeliegende
    Objekt variiert. Die task_id und display_name werden über die übergebenen
    Builder-Funktionen erzeugt.

    Args:
        objects: Iterable von auszuführenden Objekten (z.B. TestFile, Job)
        call: Gemeinsame Funktion für alle Tasks: obj → result
        id_builder: Funktion zur Erzeugung stabiler, eindeutiger Task-IDs
        name_builder: Funktion zur Erzeugung menschenlesbarer Namen

    Returns:
        Sequenz von Task[TObj, TResult]-Instanzen in der Reihenfolge der Objekte
    """
    tasks: list[Task[TObj, TResult]] = []

    for obj in objects:
        task_id = id_builder(obj)
        display_name = name_builder(obj)

        task = Task(
            task_id=task_id,
            display_name=display_name,
            obj=obj,
            callable=call,  # Parameter 'call' wird an Attribut 'callable' übergeben
        )
        tasks.append(task)

    return tasks
