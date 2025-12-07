from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from tools.setup.steps.executer import (
    BatchExecutor,
    ChainedMap,
    build_task_list,
    count_completed,
    get_last_completed_record,
    TaskState,
)
from tools.setup.utils.task_naming import build_task_id, build_display_name


class DummyProgress:
    """Minimaler Progress-Recorder mit API-Subset von ProgressStep."""

    def __init__(self) -> None:
        self.advances: list[int] = []
        self.statuses: list[str] = []

    def advance(self, steps: int = 1) -> None:
        self.advances.append(steps)

    def set_status(self, text: str) -> None:
        self.statuses.append(text)


@dataclass(frozen=True)
class Job:
    name: str
    delay: float
    fail: bool = False


@dataclass(frozen=True)
class JobResult:
    name: str
    ok: bool


def run_job(job: Job) -> JobResult:
    time.sleep(job.delay)
    if job.fail:
        raise RuntimeError(f"failed {job.name}")
    return JobResult(name=job.name, ok=True)


def _poll_until_done(cm: ChainedMap[JobResult], total: int, progress: DummyProgress) -> None:
    sid = cm.get_latest().snapshot_id
    completed_prev = 0

    while True:
        nxt = cm.get_next(sid)
        if nxt is None:
            latest = cm.get_latest()
            if count_completed(latest) == total:
                break
            time.sleep(0.005)
            continue
        sid = nxt.snapshot_id
        last_rec = get_last_completed_record(nxt)
        if last_rec is None:
            # RUNNING-Snapshot → ignorieren für Progress/Text
            continue

        completed_now = count_completed(nxt)
        delta = max(0, completed_now - completed_prev)
        if delta:
            progress.advance(delta)
        progress.set_status(f"Running / {last_rec.display_name}")
        completed_prev = completed_now


def test_ui_running_text_and_progress_consistency():
    jobs = [
        Job("A", 0.03),
        Job("B", 0.06),
        Job("C", 0.01),
    ]

    tasks = build_task_list(
        objects=jobs,
        call=run_job,
        id_builder=build_task_id,
        name_builder=build_display_name,
    )

    cm: ChainedMap[JobResult] = ChainedMap()
    cm.seed([(t.task_id, t.display_name) for t in tasks])

    progress = DummyProgress()
    progress.set_status("Running / –")

    t = threading.Thread(target=lambda: BatchExecutor(tasks, cm).execute(), daemon=True)
    t.start()

    _poll_until_done(cm, len(tasks), progress)

    # Genau drei Abschlüsse → insgesamt Summe der advances ist 3
    assert sum(progress.advances) == len(tasks)
    # Alle Statusmeldungen müssen mit dem geforderten Präfix beginnen
    assert progress.statuses[0].startswith("Running / ")
    assert progress.statuses[-1].startswith("Running / ")


def test_ui_failure_detection_and_abort():
    jobs = [
        Job("A", 0.02),
        Job("B", 0.01, fail=True),
        Job("C", 0.03),
    ]

    tasks = build_task_list(jobs, run_job, build_task_id, build_display_name)
    cm: ChainedMap[JobResult] = ChainedMap()
    cm.seed([(t.task_id, t.display_name) for t in tasks])

    progress = DummyProgress()
    progress.set_status("Running / –")

    t = threading.Thread(target=lambda: BatchExecutor(tasks, cm).execute(), daemon=True)
    t.start()

    sid = cm.get_latest().snapshot_id
    failed_seen = False
    while True:
        nxt = cm.get_next(sid)
        if nxt is None:
            latest = cm.get_latest()
            if any(r.task_state == TaskState.FAILED for r in latest.records.values()):
                failed_seen = True
                break
            if count_completed(latest) == len(tasks):
                break
            time.sleep(0.005)
            continue
        sid = nxt.snapshot_id
        if any(r.task_state == TaskState.FAILED for r in nxt.records.values()):
            failed_seen = True
            break

    assert failed_seen
