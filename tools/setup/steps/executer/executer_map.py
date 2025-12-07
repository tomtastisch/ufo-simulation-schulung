from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto
from threading import Lock
from typing import Generic, Iterable, Mapping, MutableMapping, TypeVar

TResult = TypeVar("TResult")


class TaskState(Enum):
    """Mögliche Lebenszyklus-Phasen eines Tasks."""

    PENDING = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()


@dataclass(slots=True, frozen=True)
class TaskStateRecord(Generic[TResult]):
    """Thread-sicherer Status-Eintrag eines Tasks."""

    task_id: str
    display_name: str
    task_state: TaskState
    task_result: TResult | None = None
    error: str | None = None


@dataclass(slots=True, frozen=True)
class Snapshot(Generic[TResult]):
    """Immutabler Gesamtzustand aller Tasks zu einem Zeitpunkt."""

    snapshot_id: int
    records: Mapping[str, TaskStateRecord[TResult]]
    last_completed_id: str | None = None


class ChainedMap(Generic[TResult]):
    """
    Thread-sicherer Cache + Snapshot-API zwischen Executor und UI.

    Semantik der Snapshots:
    - Für jedes `set_state(...)` wird ein neuer Snapshot erzeugt.
      Das kann sowohl bei RUNNING- als auch bei DONE/FAILED-Übergängen passieren.
    - Für die UI/Progress-Anzeige sind in der Regel nur Abschlüsse relevant.
      Diese erkennt man daran, dass `snapshot.last_completed_id` nicht None ist.
    - Die Abschlussreihenfolge ist maßgeblich für Fortschritt und Textanzeige.
      Verwenden Sie dazu die Helper `count_completed(...)` und
      `get_last_completed_record(...)`.
    """

    def __init__(self) -> None:
        self._records: MutableMapping[str, TaskStateRecord[TResult]] = {}
        self._snapshots: MutableMapping[int, Snapshot[TResult]] = {}
        self._next_snapshot_id = 0
        self._latest_snapshot_id = -1
        self._lock = Lock()

    @property
    def total_tasks(self) -> int:
        """Anzahl aktuell bekannter Tasks."""

        return len(self._records)

    @property
    def latest_snapshot_id(self) -> int:
        """Snapshot-ID des jüngsten Eintrags (-1, solange nichts registriert wurde)."""

        return self._latest_snapshot_id

    def seed(self, tasks: Iterable[tuple[str, str]]) -> Snapshot[TResult]:
        """Registriert alle Tasks mit PENDING-State und erzeugt Snapshot #0."""

        with self._lock:
            if self._records:
                raise ValueError("ChainedMap ist bereits initialisiert")

            for task_id, display_name in tasks:
                self._records[task_id] = TaskStateRecord(
                    task_id=task_id,
                    display_name=display_name,
                    task_state=TaskState.PENDING,
                )

            return self._create_snapshot(last_completed_id=None)

    def set_state(
            self,
            task_id: str,
            *,
            task_state: TaskState,
            task_result: TResult | None = None,
            error: str | None = None,
            completed: bool | None = None,
    ) -> Snapshot[TResult]:
        """Aktualisiert den Task-State und erzeugt einen neuen Snapshot."""

        with self._lock:
            record = self._records.get(task_id)
            if record is None:
                raise KeyError(f"Unbekannte task_id: {task_id}")

            updated = replace(
                record,
                task_state=task_state,
                task_result=task_result,
                error=error,
            )
            self._records[task_id] = updated

            completed_flag = (
                completed
                if completed is not None
                else task_state in (TaskState.DONE, TaskState.FAILED)
            )

            return self._create_snapshot(
                last_completed_id=task_id if completed_flag else None,
            )

    def get_latest(self) -> Snapshot[TResult]:
        """Liefert den aktuellsten Snapshot (RuntimeError, falls leer)."""

        with self._lock:
            if self._latest_snapshot_id == -1:
                raise RuntimeError("ChainedMap wurde noch nicht initialisiert")
            return self._snapshots[self._latest_snapshot_id]

    def get_next(self, after_id: int) -> Snapshot[TResult] | None:
        """Liefert den nachfolgenden Snapshot oder None."""

        with self._lock:
            return self._snapshots.get(after_id + 1)

    def is_latest(self, snapshot_id: int) -> bool:
        """True, wenn snapshot_id noch dem aktuellen Stand entspricht."""

        with self._lock:
            return snapshot_id == self._latest_snapshot_id

    def _create_snapshot(self, last_completed_id: str | None) -> Snapshot[TResult]:
        snapshot_id = self._next_snapshot_id
        self._next_snapshot_id += 1

        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            records=dict(self._records),
            last_completed_id=last_completed_id,
        )
        self._snapshots[snapshot_id] = snapshot
        self._latest_snapshot_id = snapshot_id
        return snapshot


# Snapshot-Helper-Funktionen (außerhalb der Klasse)


def count_completed(snapshot: Snapshot[TResult]) -> int:
    """
    Zählt die Anzahl abgeschlossener Tasks (DONE + FAILED).

    Args:
        snapshot: Der zu analysierende Snapshot

    Returns:
        Anzahl der Tasks mit State DONE oder FAILED
    """
    return sum(
        1
        for record in snapshot.records.values()
        if record.task_state in (TaskState.DONE, TaskState.FAILED)
    )


def get_last_completed_record(
        snapshot: Snapshot[TResult],
) -> TaskStateRecord[TResult] | None:
    """
    Liefert den TaskStateRecord des zuletzt abgeschlossenen Tasks.

    Args:
        snapshot: Der zu analysierende Snapshot

    Returns:
        TaskStateRecord des letzten abgeschlossenen Tasks oder None
    """
    if snapshot.last_completed_id is None:
        return None
    return snapshot.records.get(snapshot.last_completed_id)


def has_failures(snapshot: Snapshot[TResult]) -> bool:
    """
    Prüft, ob der Snapshot fehlgeschlagene Tasks enthält.

    Args:
        snapshot: Der zu analysierende Snapshot

    Returns:
        True, wenn mindestens ein Task FAILED ist
    """
    return any(
        record.task_state == TaskState.FAILED
        for record in snapshot.records.values()
    )
