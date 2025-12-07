"""
Unit-Tests für generischen BatchExecutor + ChainedMap + Task-System.

Prüft:
- ChainedMap: seed, set_state, Snapshots, Abschlussreihenfolge
- Task-System: build_task_list, Task.run()
- BatchExecutor: Parallele Ausführung, ChainedMap-Integration, Fehlerbehandlung
- Snapshot-Helper: count_completed, get_last_completed_record, has_failures
- End-to-End: Vollständige Ablauf mit Snapshot-Polling
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from tools.setup.steps.executer import (
    BatchExecutor,
    ChainedMap,
    Snapshot,
    Task,
    TaskState,
    build_task_list,
    count_completed,
    get_last_completed_record,
    has_failures,
)
from tools.setup.utils.task_naming import build_display_name, build_task_id


# ============================================================
# Test-Domänen-Objekte (Dummy-Implementierung)
# ============================================================


@dataclass(frozen=True)
class DummyJob:
    """Einfaches Test-Objekt für BatchExecutor."""

    job_id: str
    duration: float  # Simulierte Ausführungszeit in Sekunden
    should_fail: bool = False


@dataclass(frozen=True)
class DummyResult:
    """Ergebnis eines DummyJob."""

    job_id: str
    success: bool
    message: str


def run_dummy_job(job: DummyJob) -> DummyResult:
    """
    Simuliert Ausführung eines Jobs.

    Args:
        job: Auszuführender Job

    Returns:
        DummyResult mit Erfolg/Fehler

    Raises:
        RuntimeError: Wenn job.should_fail=True
    """
    time.sleep(job.duration)

    if job.should_fail:
        raise RuntimeError(f"Job {job.job_id} fehlgeschlagen (simuliert)")

    return DummyResult(
        job_id=job.job_id,
        success=True,
        message=f"Job {job.job_id} erfolgreich",
    )


# ============================================================
# Tests: ChainedMap
# ============================================================


def test_chained_map_seed():
    """ChainedMap.seed() initialisiert korrekt mit PENDING-Status."""
    cm: ChainedMap[DummyResult] = ChainedMap()

    tasks = [
        ("task_1", "Job 1"),
        ("task_2", "Job 2"),
        ("task_3", "Job 3"),
    ]

    snapshot = cm.seed(tasks)

    # Snapshot #0 wurde erzeugt
    assert snapshot.snapshot_id == 0
    assert cm.latest_snapshot_id == 0
    assert cm.total_tasks == 3

    # Alle Tasks sind PENDING
    assert snapshot.last_completed_id is None
    for task_id, display_name in tasks:
        record = snapshot.records[task_id]
        assert record.task_id == task_id
        assert record.display_name == display_name
        assert record.task_state == TaskState.PENDING
        assert record.task_result is None
        assert record.error is None


def test_chained_map_set_state_running():
    """set_state() mit RUNNING erzeugt neuen Snapshot."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("task_1", "Job 1")])

    snapshot = cm.set_state("task_1", task_state=TaskState.RUNNING)

    assert snapshot.snapshot_id == 1
    assert cm.latest_snapshot_id == 1

    record = snapshot.records["task_1"]
    assert record.task_state == TaskState.RUNNING
    # last_completed_id bleibt None, da RUNNING nicht abgeschlossen ist
    assert snapshot.last_completed_id is None


def test_chained_map_set_state_done():
    """set_state() mit DONE markiert Task als abgeschlossen."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("task_1", "Job 1")])

    result = DummyResult("task_1", True, "Erfolg")
    snapshot = cm.set_state("task_1", task_state=TaskState.DONE, task_result=result)

    assert snapshot.snapshot_id == 1
    record = snapshot.records["task_1"]
    assert record.task_state == TaskState.DONE
    assert record.task_result == result
    # last_completed_id wurde gesetzt
    assert snapshot.last_completed_id == "task_1"


def test_chained_map_set_state_failed():
    """set_state() mit FAILED speichert Fehler."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("task_1", "Job 1")])

    snapshot = cm.set_state("task_1", task_state=TaskState.FAILED, error="Test-Fehler")

    record = snapshot.records["task_1"]
    assert record.task_state == TaskState.FAILED
    assert record.error == "Test-Fehler"
    assert snapshot.last_completed_id == "task_1"


def test_chained_map_get_next():
    """get_next() liefert Snapshots in Abschlussreihenfolge."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("task_1", "Job 1"), ("task_2", "Job 2")])

    # Snapshot #0 (seed)
    snapshot_0 = cm.get_latest()
    assert snapshot_0.snapshot_id == 0

    # Task 1: RUNNING → Snapshot #1
    cm.set_state("task_1", task_state=TaskState.RUNNING)
    snapshot_1 = cm.get_next(after_id=0)
    assert snapshot_1 is not None
    assert snapshot_1.snapshot_id == 1

    # Task 1: DONE → Snapshot #2
    cm.set_state("task_1", task_state=TaskState.DONE)
    snapshot_2 = cm.get_next(after_id=1)
    assert snapshot_2 is not None
    assert snapshot_2.snapshot_id == 2
    assert snapshot_2.last_completed_id == "task_1"

    # Kein weiterer Snapshot nach #2
    assert cm.get_next(after_id=2) is None


def test_chained_map_is_latest():
    """is_latest() prüft korrekt."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("task_1", "Job 1")])

    assert cm.is_latest(0) is True
    cm.set_state("task_1", task_state=TaskState.DONE)
    assert cm.is_latest(0) is False
    assert cm.is_latest(1) is True


# ============================================================
# Tests: Snapshot-Helper
# ============================================================


def test_count_completed():
    """count_completed() zählt DONE + FAILED."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("t1", "Job 1"), ("t2", "Job 2"), ("t3", "Job 3")])

    snapshot = cm.get_latest()
    assert count_completed(snapshot) == 0

    cm.set_state("t1", task_state=TaskState.DONE)
    snapshot = cm.get_latest()
    assert count_completed(snapshot) == 1

    cm.set_state("t2", task_state=TaskState.FAILED)
    snapshot = cm.get_latest()
    assert count_completed(snapshot) == 2

    cm.set_state("t3", task_state=TaskState.RUNNING)
    snapshot = cm.get_latest()
    assert count_completed(snapshot) == 2  # RUNNING zählt nicht


def test_get_last_completed_record():
    """get_last_completed_record() liefert korrekten Record."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("t1", "Job 1"), ("t2", "Job 2")])

    snapshot = cm.get_latest()
    assert get_last_completed_record(snapshot) is None

    cm.set_state("t1", task_state=TaskState.DONE)
    snapshot = cm.get_latest()
    record = get_last_completed_record(snapshot)
    assert record is not None
    assert record.task_id == "t1"
    assert record.task_state == TaskState.DONE


def test_has_failures():
    """has_failures() erkennt FAILED-Tasks."""
    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([("t1", "Job 1"), ("t2", "Job 2")])

    snapshot = cm.get_latest()
    assert has_failures(snapshot) is False

    cm.set_state("t1", task_state=TaskState.DONE)
    snapshot = cm.get_latest()
    assert has_failures(snapshot) is False

    cm.set_state("t2", task_state=TaskState.FAILED)
    snapshot = cm.get_latest()
    assert has_failures(snapshot) is True


# ============================================================
# Tests: Task-System
# ============================================================


def test_task_run():
    """Task.run() führt Callable korrekt aus."""
    job = DummyJob("job_1", duration=0.001)
    task = Task(
        task_id="job_1",
        display_name="Job 1",
        obj=job,
        callable=run_dummy_job,
    )

    result = task.run()
    assert isinstance(result, DummyResult)
    assert result.job_id == "job_1"
    assert result.success is True


def test_build_task_list():
    """build_task_list() erzeugt korrekte Task-Liste."""
    jobs = [
        DummyJob("job_1", 0.001),
        DummyJob("job_2", 0.001),
    ]

    tasks = build_task_list(
        objects=jobs,
        call=run_dummy_job,
        id_builder=lambda j: j.job_id,
        name_builder=lambda j: f"Job {j.job_id}",
    )

    assert len(tasks) == 2
    assert tasks[0].task_id == "job_1"
    assert tasks[0].display_name == "Job job_1"
    assert tasks[0].obj == jobs[0]
    assert tasks[0].callable == run_dummy_job


def test_context_utils():
    """build_task_id() und build_display_name() funktionieren."""
    job = DummyJob("job_1", 0.001)

    # build_task_id: sollte repr(job) sein (kein spezielles Attribut)
    task_id = build_task_id(job)
    assert "job_1" in task_id

    # build_display_name: str(job)
    display_name = build_display_name(job)
    assert "job_1" in display_name


# ============================================================
# Tests: BatchExecutor
# ============================================================


def test_batch_executor_success():
    """BatchExecutor führt alle Tasks erfolgreich aus."""
    jobs = [
        DummyJob("job_1", duration=0.01),
        DummyJob("job_2", duration=0.01),
        DummyJob("job_3", duration=0.01),
    ]

    tasks = build_task_list(
        objects=jobs,
        call=run_dummy_job,
        id_builder=lambda j: j.job_id,
        name_builder=lambda j: f"Job {j.job_id}",
    )

    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([(t.task_id, t.display_name) for t in tasks])

    executor = BatchExecutor(
        tasks=tasks,
        chained_map=cm,
        max_workers=2,
    )

    executor.execute()

    # Alle Tasks sollten DONE sein
    snapshot = cm.get_latest()
    assert count_completed(snapshot) == 3
    assert has_failures(snapshot) is False

    for job in jobs:
        record = snapshot.records[job.job_id]
        assert record.task_state == TaskState.DONE
        assert record.task_result is not None
        assert record.task_result.success is True


def test_batch_executor_failure():
    """BatchExecutor behandelt Fehler korrekt."""
    jobs = [
        DummyJob("job_1", duration=0.01, should_fail=False),
        DummyJob("job_2", duration=0.01, should_fail=True),  # ← Fehler
        DummyJob("job_3", duration=0.01, should_fail=False),
    ]

    tasks = build_task_list(
        objects=jobs,
        call=run_dummy_job,
        id_builder=lambda j: j.job_id,
        name_builder=lambda j: f"Job {j.job_id}",
    )

    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([(t.task_id, t.display_name) for t in tasks])

    executor = BatchExecutor(
        tasks=tasks,
        chained_map=cm,
        max_workers=2,
    )

    executor.execute()

    # Alle Tasks sind abgeschlossen (2 DONE, 1 FAILED)
    snapshot = cm.get_latest()
    assert count_completed(snapshot) == 3
    assert has_failures(snapshot) is True

    # job_2 ist FAILED
    record_2 = snapshot.records["job_2"]
    assert record_2.task_state == TaskState.FAILED
    assert "fehlgeschlagen" in record_2.error

    # job_1 und job_3 sind DONE
    assert snapshot.records["job_1"].task_state == TaskState.DONE
    assert snapshot.records["job_3"].task_state == TaskState.DONE


# ============================================================
# Integration-Test: End-to-End mit Snapshot-Polling
# ============================================================


def test_end_to_end_snapshot_polling():
    """
    Simuliert vollständigen Ablauf:
    - TaskList erzeugen
    - ChainedMap seeden
    - BatchExecutor starten
    - Snapshot-Polling-Schleife
    - UI-Updates (simuliert via Assertions)

    **Kritisch**: Verifiziert, dass ALLE abgeschlossenen Tasks in der
    korrekten Abschlussreihenfolge über get_next() angezeigt werden.
    """
    jobs = [
        DummyJob("job_1", duration=0.02),
        DummyJob("job_2", duration=0.03),
        DummyJob("job_3", duration=0.01),  # ← Sollte als erstes fertig sein
    ]

    # 1. TaskList erzeugen
    tasks = build_task_list(
        objects=jobs,
        call=run_dummy_job,
        id_builder=lambda j: j.job_id,
        name_builder=lambda j: f"Job {j.job_id}",
    )

    # 2. ChainedMap seeden
    cm: ChainedMap[DummyResult] = ChainedMap()
    initial_snapshot = cm.seed([(t.task_id, t.display_name) for t in tasks])
    assert initial_snapshot.snapshot_id == 0

    # 3. BatchExecutor starten (in separatem Thread)
    import threading

    def run_executor():
        executor = BatchExecutor(
            tasks=tasks,
            chained_map=cm,
            max_workers=2,
        )
        executor.execute()

    executor_thread = threading.Thread(target=run_executor, daemon=True)
    executor_thread.start()

    # 4. Snapshot-Polling-Schleife (wie in Step._step_impl)
    snapshot_id = 0
    completed_in_order: list[str] = []  # ← Namen in Abschlussreihenfolge
    progress_values: list[int] = []
    snapshot_count = 0

    # Maximal 10 Sekunden warten
    timeout = time.time() + 10.0

    while time.time() < timeout:
        next_snap = cm.get_next(snapshot_id)

        if next_snap is None:
            # Prüfe, ob alle Tasks fertig sind
            latest = cm.get_latest()
            if count_completed(latest) == len(tasks):
                break
            # Noch nicht fertig → kurz warten
            time.sleep(0.01)
            continue

        # Neuer Snapshot verfügbar
        snapshot_id = next_snap.snapshot_id
        snapshot_count += 1

        # UI-Update simulieren
        count = count_completed(next_snap)
        progress_values.append(count)

        # **KRITISCH**: Hole den letzten abgeschlossenen Task
        last_rec = get_last_completed_record(next_snap)
        if last_rec:
            # Dies ist der Task, der JETZT abgeschlossen wurde
            completed_in_order.append(last_rec.display_name)

        # Fehler-Check
        if has_failures(next_snap):
            break

    # Executor-Thread beenden
    executor_thread.join(timeout=2.0)

    # ========================================
    # Assertions: Verifiziere Abschlussreihenfolge
    # ========================================

    final_snapshot = cm.get_latest()
    assert count_completed(final_snapshot) == 3
    assert has_failures(final_snapshot) is False

    # **KRITISCH**: Mindestens 3 Snapshots (RUNNING + DONE für jeden Task)
    # In der Praxis: seed (0), dann pro Task: RUNNING + DONE = 6 Snapshots
    assert snapshot_count >= 3, f"Zu wenige Snapshots: {snapshot_count}"

    # **KRITISCH**: Progress-Werte müssen monoton steigend sein
    assert len(progress_values) >= 3
    assert progress_values == sorted(progress_values), "Progress nicht monoton steigend"
    assert progress_values[-1] == 3

    # **KRITISCH**: completed_in_order muss ALLE 3 Jobs enthalten
    assert len(completed_in_order) == 3, (
        f"Nicht alle Tasks wurden angezeigt! "
        f"Erwartet: 3, Erhalten: {len(completed_in_order)}"
    )

    # **KRITISCH**: Alle Job-Namen müssen vorhanden sein
    expected_names = {"Job job_1", "Job job_2", "Job job_3"}
    actual_names = set(completed_in_order)
    assert actual_names == expected_names, (
        f"Fehlende oder falsche Namen! "
        f"Erwartet: {expected_names}, Erhalten: {actual_names}"
    )

    # **KRITISCH**: Jeder Name darf nur EINMAL vorkommen
    assert len(completed_in_order) == len(set(completed_in_order)), (
        f"Duplikate in completed_in_order: {completed_in_order}"
    )

    # **ZUSATZ**: Verifiziere, dass job_3 (kürzeste Duration) vermutlich
    # zuerst fertig wurde (nicht garantiert bei Parallelisierung, aber wahrscheinlich)
    # Dies ist nur ein informativer Check, kein Hard-Requirement
    print(f"Abschlussreihenfolge: {completed_in_order}")

    # Job_3 sollte mit höher Wahrscheinlichkeit als erstes fertig sein
    # (0.01s vs. 0.02s und 0.03s)
    first_completed = completed_in_order[0]
    print(f"Zuerst abgeschlossen: {first_completed}")
    # Kein Assert hier, da Timing nicht deterministisch ist


def test_snapshot_polling_with_failure():
    """
    Polling-Schleife erkennt Fehler und bricht ab.
    """
    jobs = [
        DummyJob("job_1", duration=0.01, should_fail=False),
        DummyJob("job_2", duration=0.02, should_fail=True),  # ← Fehler
    ]

    tasks = build_task_list(
        objects=jobs,
        call=run_dummy_job,
        id_builder=lambda j: j.job_id,
        name_builder=lambda j: f"Job {j.job_id}",
    )

    cm: ChainedMap[DummyResult] = ChainedMap()
    cm.seed([(t.task_id, t.display_name) for t in tasks])

    import threading

    def run_executor():
        executor = BatchExecutor(
            tasks=tasks,
            chained_map=cm,
            max_workers=2,
        )
        executor.execute()

    executor_thread = threading.Thread(target=run_executor, daemon=True)
    executor_thread.start()

    # Polling-Schleife mit Fehler-Erkennung
    snapshot_id = 0
    detected_failure = False
    timeout = time.time() + 5.0

    while time.time() < timeout:
        next_snap = cm.get_next(snapshot_id)
        if next_snap is None:
            time.sleep(0.01)
            continue

        snapshot_id = next_snap.snapshot_id

        # Fehler-Check
        if has_failures(next_snap):
            detected_failure = True
            break

    executor_thread.join(timeout=2.0)

    # Fehler wurde erkannt
    assert detected_failure is True

    final_snapshot = cm.get_latest()
    assert has_failures(final_snapshot) is True


def test_snapshot_sequence_completeness():
    """
    **KRITISCHER TEST**: Verifiziert, dass get_next() ALLE abgeschlossenen
    Tasks in der korrekten Reihenfolge liefert.

    Testet:
    1. Jeder abgeschlossene Task erzeugt genau EINEN Snapshot mit last_completed_id
    2. get_next() liefert Snapshots in der richtigen Reihenfolge
    3. Kein Task wird übersprungen
    4. Jeder Task erscheint genau einmal
    """
    # 5 Jobs mit unterschiedlichen Laufzeiten
    jobs = [
        DummyJob("job_A", duration=0.05),  # Langsam
        DummyJob("job_B", duration=0.01),  # Schnell
        DummyJob("job_C", duration=0.03),  # Mittel
        DummyJob("job_D", duration=0.02),  # Schneller als C
        DummyJob("job_E", duration=0.04),  # Langsamer als C
    ]

    tasks = build_task_list(
        objects=jobs,
        call=run_dummy_job,
        id_builder=lambda j: j.job_id,
        name_builder=lambda j: f"Job {j.job_id}",
    )

    cm: ChainedMap[DummyResult] = ChainedMap()
    initial_snap = cm.seed([(t.task_id, t.display_name) for t in tasks])

    # Seed erzeugt Snapshot #0
    assert initial_snap.snapshot_id == 0
    assert initial_snap.last_completed_id is None

    # Starte BatchExecutor
    import threading

    def run_executor():
        executor = BatchExecutor(
            tasks=tasks,
            chained_map=cm,
            max_workers=3,  # 3 parallele Worker
        )
        executor.execute()

    executor_thread = threading.Thread(target=run_executor, daemon=True)
    executor_thread.start()

    # ========================================
    # Sammle ALLE Snapshots via get_next()
    # ========================================

    all_snapshots: list[Snapshot[DummyResult]] = [initial_snap]
    snapshot_id = 0
    timeout = time.time() + 10.0

    while time.time() < timeout:
        next_snap = cm.get_next(snapshot_id)

        if next_snap is None:
            # Prüfe ob fertig
            latest = cm.get_latest()
            if count_completed(latest) == len(tasks):
                break
            time.sleep(0.01)
            continue

        all_snapshots.append(next_snap)
        snapshot_id = next_snap.snapshot_id

    executor_thread.join(timeout=2.0)

    # ========================================
    # Verifiziere Snapshot-Sequenz
    # ========================================

    # Mindestens 1 (seed) + 5 (DONE) = 6 Snapshots
    # In Praxis: seed + (RUNNING + DONE) * 5 = 11 Snapshots
    assert len(all_snapshots) >= 6, f"Zu wenige Snapshots: {len(all_snapshots)}"

    print(f"\nAnzahl Snapshots: {len(all_snapshots)}")

    # Extrahiere alle last_completed_id in Reihenfolge
    completed_sequence: list[str] = []

    for snap in all_snapshots:
        if snap.last_completed_id is not None:
            # Dieser Snapshot markiert einen Abschluss
            completed_sequence.append(snap.last_completed_id)

    print(f"Abschluss-Sequenz: {completed_sequence}")

    # **KRITISCH 1**: Genau 5 Abschlüsse
    assert len(completed_sequence) == 5, (
        f"Erwartet 5 Abschlüsse, erhalten: {len(completed_sequence)}"
    )

    # **KRITISCH 2**: Alle Job-IDs müssen vorhanden sein
    expected_ids = {"job_A", "job_B", "job_C", "job_D", "job_E"}
    actual_ids = set(completed_sequence)
    assert actual_ids == expected_ids, (
        f"Fehlende/Falsche IDs! Erwartet: {expected_ids}, Erhalten: {actual_ids}"
    )

    # **KRITISCH 3**: Keine Duplikate
    assert len(completed_sequence) == len(set(completed_sequence)), (
        f"Duplikate gefunden: {completed_sequence}"
    )

    # **KRITISCH 4**: Verifiziere get_last_completed_record() Konsistenz
    for i, snap in enumerate(all_snapshots):
        if snap.last_completed_id is not None:
            last_rec = get_last_completed_record(snap)
            assert last_rec is not None, f"Snapshot {i}: last_rec ist None trotz last_completed_id"
            assert last_rec.task_id == snap.last_completed_id, (
                f"Snapshot {i}: Inkonsistenz! "
                f"last_completed_id={snap.last_completed_id}, "
                f"last_rec.task_id={last_rec.task_id}"
            )
            assert last_rec.task_state in (TaskState.DONE, TaskState.FAILED), (
                f"Snapshot {i}: Task {last_rec.task_id} hat State {last_rec.task_state}, "
                f"sollte DONE oder FAILED sein"
            )

    # **KRITISCH 5**: Snapshot-IDs müssen sequenziell sein
    for i in range(len(all_snapshots)):
        assert all_snapshots[i].snapshot_id == i, (
            f"Snapshot-ID Lücke bei Index {i}: "
            f"Erwartet {i}, Erhalten {all_snapshots[i].snapshot_id}"
        )

    print("✅ Alle Abschlüsse wurden korrekt über get_next() geliefert!")
