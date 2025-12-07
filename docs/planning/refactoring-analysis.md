# Refactoring-Analyse: BatchExecutor + ChainedMap + Step Integration

## 1. Identifizierte Probleme

### Problem 1: Fortschrittsberechnung inkonsistent

**Symptom**: Progress-Bar zeigt 1% → 100% Sprung bei 23 Tests.

**Ursache**:

- `estimate_total()` liefert Anzahl **Tests** (23)
- `run_batch_by_file()` führt nach **Dateien** gruppiert aus (z.B. 4 Dateien)
- `progress.advance(1)` wird nur 4× aufgerufen → 4/23 = ~17%, dann sofort auf 100%

**Root Cause**: Granularitäts-Mismatch zwischen Fortschritts-Einheiten und Ausführungs-Einheiten.

### Problem 2: Textanzeige entspricht nicht Spezifikation

**Ist-Zustand**: `"Running / ✓ test_file.py (4/23)"`
**Soll-Zustand**: `"Running / <Name des zuletzt beendeten Tests>"`

**Ursache**: `progress_callback` verwendet `file_short`, nicht den tatsächlichen Test-Namen.

### Problem 3: ChainedMap wird nicht genutzt

**Symptom**: ChainedMap existiert, aber Executor verwendet direkten Callback.

**Ursache**: Fehlende Integration zwischen Executor → ChainedMap → Step/UI.

### Problem 4: Keine Snapshot-basierte Verarbeitung

**Symptom**: Keine inkrementelle Snapshot-Logik via `get_next()`.

**Ursache**: Step implementiert keine Snapshot-Polling-Schleife.

### Problem 5: Executor ist nicht generisch

**Symptom**: `run_batch_by_file` ist domänenspezifisch (kennt Tests, Dateien, pytest).

**Ursache**: Fehlende Abstraktionsebene.

---

## 2. Architektur-Vorschlag

### Schichtenmodell

```
┌─────────────────────────────────────────────┐
│  Step (RunTestsStep)                        │
│  - Domänenlogik (was ist ein Test?)        │
│  - Konfiguration (max_workers, etc.)        │
│  - Snapshot-Polling-Schleife                │
│  - UI-Update (Progress-Bar + Text)          │
└─────────────────┬───────────────────────────┘
                  │
                  │ verwendet
                  ↓
┌─────────────────────────────────────────────┐
│  TaskList                                   │
│  - Nimmt Objekte + Callable                 │
│  - Erzeugt Task[TObj, TResult]-Liste        │
│  - Verwendet build_task_id + build_display  │
└─────────────────┬───────────────────────────┘
                  │
                  │ liefert Tasks an
                  ↓
┌─────────────────────────────────────────────┐
│  BatchExecutor[TObj, TResult]               │
│  - Generisch, keine Domänenlogik            │
│  - Führt Tasks parallel aus                 │
│  - Meldet Status an ChainedMap              │
└─────────────────┬───────────────────────────┘
                  │
                  │ schreibt in
                  ↓
┌─────────────────────────────────────────────┐
│  ChainedMap[TResult]                        │
│  - Thread-sicherer Cache                    │
│  - Snapshot-Verwaltung                      │
│  - API: get_latest, get_next, is_latest     │
└─────────────────────────────────────────────┘
```

### Datenfluss

1. **Step → TaskList**:
    - Objekte (`TestFile`, etc.) + Callable
    - → `Task[TObj, TResult]` Liste

2. **Step → ChainedMap**:
    - `seed(tasks)` mit (task_id, display_name)

3. **Step → BatchExecutor**:
    - Startet Executor mit Task-Liste + ChainedMap

4. **BatchExecutor → ChainedMap**:
    - `set_state(RUNNING)` beim Start
    - `set_state(DONE/FAILED)` nach Completion

5. **Step: Polling-Schleife**:
    - `snapshot = get_latest()`
    - Dann in Schleife: `next_snap = get_next(after_id)`
    - Bei jedem Snapshot: UI updaten

---

## 3. Refactoring-Plan

### Phase 1: Generische Task-Infrastruktur

**Ziel**: Domänenunabhängige Task-Typen und TaskList.

**Schritte**:

1. **Task-Modul erstellen** (`tools/setup/steps/executer/task.py`):
    - `TaskCallable[TObj, TResult] = Callable[[TObj], TResult]`
    - `@dataclass Task[TObj, TResult]`:
        - `task_id: str`
        - `display_name: str`
        - `obj: TObj`
        - `callable: TaskCallable[TObj, TResult]`

2. **TaskList-Modul erstellen** (`tools/setup/steps/executer/task_list.py`):
    - `build_task_list(objects, callable, id_builder, name_builder) -> Sequence[Task]`

3. **Context-Utils erweitern** (`tools/setup/utils/context.py`):
    - `build_task_id(obj: Any) -> str` (deterministisch)
    - `build_display_name(obj: Any) -> str` (human-readable)

### Phase 2: BatchExecutor generifizieren

**Ziel**: Executor wird generisch `BatchExecutor[TObj, TResult]`.

**Schritte**:

1. **Executor umbauen** (`tools/setup/steps/executer/executor.py`):
    - Klasse `BatchExecutor[TObj, TResult]`
    - Constructor: `(tasks, chained_map, max_workers, logger)`
    - Methode: `execute() -> None`
    - Keine Domänenlogik (kein pytest, keine Dateien)

2. **Worker-Funktion generisch machen**:
    - `_worker(task: Task[TObj, TResult]) -> TResult | Exception`

3. **ChainedMap-Integration**:
    - Bei Task-Start: `chained_map.set_state(task_id, RUNNING)`
    - Bei Success: `chained_map.set_state(task_id, DONE, result=result)`
    - Bei Failure: `chained_map.set_state(task_id, FAILED, error=str(exc))`

### Phase 3: ChainedMap erweitern

**Ziel**: Vollständige Snapshot-API + Abschlussreihenfolge.

**Schritte**:

1. **Snapshot erweitern**:
    - `last_completed_id: str | None` → bereits vorhanden ✓
    - Sicherstellen, dass `last_completed_id` bei jedem DONE/FAILED gesetzt wird

2. **Helper-Methoden**:
    - `count_completed(snapshot) -> int` (DONE + FAILED)
    - `get_last_completed_record(snapshot) -> TaskStateRecord | None`

### Phase 4: RunTestsStep anpassen

**Ziel**: Step nutzt generische Infrastruktur + Snapshot-Polling.

**Schritte**:

1. **prepare() anpassen**:
    - Unverändert: liefert `tuple[(file, qname), ...]`

2. **estimate_total() korrigieren**:
    - **Statt**: `len(tests)` (Anzahl Tests)
    - **Jetzt**: Anzahl **Dateien** (= Anzahl Tasks)

3. **_step_impl() umbauen**:
    - Gruppiere Tests → Test-Dateien
    - Erzeuge `TestFile`-Objekte mit allen Tests pro Datei
    - Erstelle Callable `run_test_file: TestFile → TestFileResult`
    - Nutze `build_task_list()` → `tasks`
    - Seede ChainedMap: `chained_map.seed(tasks)`
    - Starte `BatchExecutor(tasks, chained_map, max_workers)`
    - **Snapshot-Polling-Schleife**:
      ```python
      snapshot_id = 0
      while True:
          next_snap = chained_map.get_next(snapshot_id)
          if next_snap is None:
              break
          snapshot_id = next_snap.snapshot_id
          
          # UI-Update
          count = count_completed(next_snap)
          progress.advance(1)  # nur wenn neuer Snapshot
          
          last_rec = get_last_completed_record(next_snap)
          if last_rec:
              progress.set_status(f"Running / {last_rec.display_name}")
          
          # Fehler-Check
          if last_rec and last_rec.task_state == FAILED:
              # Abbruch wie gewohnt
              break
      ```

4. **Initialzustand**:
    - Vor erstem Snapshot: `progress.set_status("Running / –")`

### Phase 5: Unit-Tests

**Ziel**: Prüfung aller Komponenten.

**Tests**:

1. **test_chained_map.py**:
    - Seed, set_state, Snapshot-Reihenfolge
    - `get_next()` liefert korrekte Abschlussreihenfolge
    - `last_completed_id` korrekt

2. **test_batch_executor.py**:
    - Generischer Executor mit Dummy-Tasks
    - ChainedMap-Integration
    - Parallele Ausführung
    - Fehlerbehandlung

3. **test_task_list.py**:
    - `build_task_list()` erzeugt korrekte Tasks
    - `build_task_id()` ist deterministisch
    - `build_display_name()` ist stabil

4. **test_run_tests_step_integration.py**:
    - End-to-End: prepare → TaskList → Executor → Snapshots
    - Progress-Bar + Text-Format korrekt
    - Fehlerfall (FAILED) wird erkannt

---

## 4. Typen und Generics

### Task-System

```python
TObj = TypeVar("TObj")
TResult = TypeVar("TResult")

TaskCallable: TypeAlias = Callable[[TObj], TResult]

@dataclass(frozen=True)
class Task(Generic[TObj, TResult]):
    task_id: str
    display_name: str
    obj: TObj
    callable: TaskCallable[TObj, TResult]
    
    def run(self) -> TResult:
        return self.callable(self.obj)
```

### BatchExecutor

```python
class BatchExecutor(Generic[TObj, TResult]):
    def __init__(
        self,
        tasks: Sequence[Task[TObj, TResult]],
        chained_map: ChainedMap[TResult],
        max_workers: int = 4,
        logger: Logger | None = None,
    ) -> None: ...
    
    def execute(self) -> None:
        """Führt alle Tasks parallel aus, schreibt in ChainedMap."""
```

### Domänen-spezifische Typen (in RunTestsStep)

```python
@dataclass(frozen=True)
class TestFile:
    """Ein Test-Modul mit allen darin enthaltenen Tests."""
    file_relpath: str
    qualified_names: list[str]

@dataclass(frozen=True)
class TestFileResult:
    ok: bool
    cause: str | None
    details: str
```

---

## 5. Vorteile der Lösung

1. **Korrekte Fortschrittsberechnung**:
    - `estimate_total()` = Anzahl Dateien
    - `advance()` wird genau pro Datei aufgerufen
    - 1% pro Datei, kontinuierlich

2. **Korrektes Text-Format**:
    - `last_completed_record.display_name` = tatsächlicher Test-Name
    - Format: `"Running / <Testname>"`

3. **Generisch wiederverwendbar**:
    - BatchExecutor kann für beliebige Tasks genutzt werden
    - Keine pytest/Test-Logik im Executor

4. **Snapshot-basiert**:
    - Abschlussreihenfolge wird korrekt abgebildet
    - UI immer konsistent mit tatsächlichem Stand

5. **Fehlerbehandlung konsistent**:
    - FAILED-Status über Snapshots erkannt
    - Gewohnter Abbruch-Pfad

6. **Thread-sicher**:
    - ChainedMap mit Locks
    - Keine Race-Conditions

7. **Testbar**:
    - Alle Komponenten isoliert testbar
    - Klare Schnittstellen

---

## 6. Migration-Strategie

**Reihenfolge**:

1. Task + TaskList implementieren
2. ChainedMap-Tests erweitern
3. BatchExecutor umbauen
4. RunTestsStep migrieren
5. Alte `run_batch_by_file()` als Legacy markieren/deprecaten
6. Integration-Tests

**Backward-Kompatibilität**:

- Alte `run_batch_by_file()` bleibt vorerst bestehen
- Neue Implementierung parallel einführen
- Nach Stabilisierung: alte Version entfernen

