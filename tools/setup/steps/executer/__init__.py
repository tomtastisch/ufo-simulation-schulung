"""
Executor-Module für parallelisierte Task-Ausführung.

Bietet generische, thread-sichere Infrastruktur für parallele
Batch-Verarbeitung mit Fortschritts-Tracking via Snapshots.

Komponenten:
- Task: Generische Arbeitseinheit
- TaskList: Builder für Task-Listen
- BatchExecutor: Paralleler Task-Executor
- ChainedMap: Thread-sicherer Snapshot-Cache
- TaskState/TaskStateRecord/Snapshot: Status-Typen
"""

from .batch_executor import BatchExecutor
from .executer_map import (
    ChainedMap,
    Snapshot,
    TaskState,
    TaskStateRecord,
    count_completed,
    get_last_completed_record,
    has_failures,
)
from .task import Task, TaskCallable
from .task_list import build_task_list

__all__ = [
    # Task-System
    "Task",
    "TaskCallable",
    "build_task_list",
    # Executor
    "BatchExecutor",
    # ChainedMap + Snapshots
    "ChainedMap",
    "Snapshot",
    "TaskState",
    "TaskStateRecord",
    "count_completed",
    "get_last_completed_record",
    "has_failures",
]
