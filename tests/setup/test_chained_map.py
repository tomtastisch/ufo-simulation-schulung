from __future__ import annotations

from tools.setup.steps.executer.executer_map import ChainedMap, TaskState


def test_chained_map_snapshot_flow() -> None:
    cm: ChainedMap[str] = ChainedMap()
    initial = cm.seed((("task-a", "A"), ("task-b", "B")))
    assert initial.snapshot_id == 0
    assert initial.records["task-a"].task_state is TaskState.PENDING

    snap1 = cm.set_state("task-a", task_state=TaskState.RUNNING)
    assert snap1.snapshot_id == 1
    assert snap1.records["task-a"].task_state is TaskState.RUNNING

    snap2 = cm.set_state("task-a", task_state=TaskState.DONE, task_result="ok")
    assert snap2.last_completed_id == "task-a"

    snap3 = cm.set_state(
        "task-b",
        task_state=TaskState.FAILED,
        error="boom",
    )
    assert snap3.records["task-b"].error == "boom"


def test_chained_map_get_next() -> None:
    cm: ChainedMap[None] = ChainedMap()
    cm.seed((("x", "X"),))
    cm.set_state("x", task_state=TaskState.RUNNING, completed=False)
    snap_done = cm.set_state("x", task_state=TaskState.DONE)

    latest = cm.get_latest()
    assert latest.snapshot_id == snap_done.snapshot_id
    prev = cm.get_next(snap_done.snapshot_id - 1)
    assert prev is snap_done
    assert cm.is_latest(latest.snapshot_id)
