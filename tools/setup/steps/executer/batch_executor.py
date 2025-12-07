"""
Generischer paralleler Batch-Executor.

Führt Tasks parallel aus und meldet Status-Updates an ChainedMap.
Komplett domänenunabhängig – kennt weder Tests, Dateien noch pytest.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from logging import Logger
from typing import Generic, Sequence, TypeVar

from tools.setup.steps.executer.executer_map import ChainedMap, TaskState
from tools.setup.steps.executer.task import Task

TObj = TypeVar("TObj")
TResult = TypeVar("TResult")


# Hinweis: Der Executor verwendet ThreadPoolExecutor, sodass Callables
# direkt auf den Objekten ausgeführt werden können, ohne Pickling-Constraints.


class BatchExecutor(Generic[TObj, TResult]):
    """
    Generischer paralleler Task-Executor.

    Führt eine Liste von Tasks parallel aus und schreibt
    Status-Updates in eine ChainedMap. Komplett domänenunabhängig.

    Typ-Parameter:
        TObj: Typ der auszuführenden Objekte
        TResult: Typ der Ergebnisse
    """

    def __init__(
            self,
            tasks: Sequence[Task[TObj, TResult]],
            chained_map: ChainedMap[TResult],
            max_workers: int = 4,
            logger: Logger | None = None,
    ) -> None:
        """
        Initialisiert den BatchExecutor.

        Args:
            tasks: Sequenz von auszuführenden Tasks
            chained_map: ChainedMap für Status-Updates
            max_workers: Anzahl paralleler Worker
            logger: Optional Logger für Debug-Ausgaben
        """
        self.tasks = tasks
        self.chained_map = chained_map
        self.max_workers = max_workers
        self.logger = logger

    def execute(self) -> None:
        """
        Führt alle Tasks parallel aus.

        Status-Updates werden in ChainedMap geschrieben:
        - RUNNING beim Start
        - DONE bei Erfolg (mit result)
        - FAILED bei Exception (mit error)

        Die Methode blockiert, bis alle Tasks abgeschlossen sind.
        Fehler stoppen die Ausführung nicht, sondern werden in
        ChainedMap als FAILED markiert.
        """
        if not self.tasks:
            return

        if self.logger:
            self.logger.debug(
                f"BatchExecutor: {len(self.tasks)} Tasks, "
                f"{self.max_workers} Worker"
            )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit alle Tasks
            futures = {}
            for task in self.tasks:
                # Setze Status auf RUNNING
                self.chained_map.set_state(
                    task.task_id,
                    task_state=TaskState.RUNNING,
                )

                # Submit Task
                future = executor.submit(task.callable, task.obj)
                futures[future] = task.task_id

            # Sammle Ergebnisse in Abschluss-Reihenfolge
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    # Task fehlgeschlagen
                    self.chained_map.set_state(
                        task_id,
                        task_state=TaskState.FAILED,
                        error=str(exc),
                    )

                    if self.logger:
                        self.logger.debug(f"✗ {task_id}: {exc}")
                else:
                    # Task erfolgreich
                    self.chained_map.set_state(
                        task_id,
                        task_state=TaskState.DONE,
                        task_result=result,
                    )

                    if self.logger:
                        self.logger.debug(f"✓ {task_id}")
