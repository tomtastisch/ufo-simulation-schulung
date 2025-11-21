# Changelog – UFO-Simulation-Schulung

Chronologische Auflistung aller Änderungen (neueste zuerst).

---

## [2025-11-21] - Lock-Verwendung validiert und nested locks behoben

### Zusammenfassung

Projektweite Validierung aller Lock-Verwendungen zur Sicherstellung korrekter Decorator-Nutzung. Zwei nested locks in `_UfoLegacySync` gefunden und behoben durch Umstellung auf `@conditional` Decorator.

### Problem/Motivation

Nach Einführung der zentralen Lock-Decorators sollte sichergestellt werden, dass:
1. Alle Locks via Decorators verwendet werden (keine manuellen Patterns)
2. Keine nested locks existieren
3. Keine veralteten Lock-Patterns im Projekt verbleiben

### Durchgeführte Analyse

**Geprüfte Komponenten**:
- StateManager ✅
- _UfoLegacySync ❌ → ✅ (2 Probleme behoben)
- CommandQueue ✅
- CommandExecutor ✅
- logging_setup ✅

**Suchmuster**:
- `threading.(Lock|RLock|Condition)` - Lock-Erstellungen
- `\.acquire()` / `\.release()` - Manuelle Acquisitions
- `with .*_lock:` - Manuelle Lock-Statements
- `notify_all()` - Condition-Variable-Nutzung
- `@synchronized` / `@conditional` - Decorator-Verwendung

### Gefundene Probleme

#### 1. _UfoLegacySync.update_state() - Nested Lock
**Problem**:
```python
@synchronized  # ← self._lock acquired
def update_state(self, update_func):
    self._state = update_func(self._state)
    self._condition.notify_all()  # ← Nutzt intern self._lock! NESTED!
```

**Lösung**:
```python
def update_state(self, update_func):
    snapshot = self._update_state_atomic(update_func)
    self._notify_observers(snapshot)

@conditional  # ← Nutzt self._condition direkt, kein nested lock
def _update_state_atomic(self, update_func):
    self._state = update_func(self._state)
    self._condition.notify_all()  # ✓ Korrekt
    return dataclass_replace(self._state)
```

#### 2. _UfoLegacySync.reset() - Nested Lock
**Problem**: Identisch zu update_state()  
**Lösung**: Analog umgestellt auf `@conditional` via `_reset_atomic()`

### Betroffene Dateien

**Geändert**:
- `src/core/simulation/ufosim.py`
  - Import von `@conditional` hinzugefügt
  - `_UfoLegacySync.update_state()` refactored
  - `_UfoLegacySync._update_state_atomic()` neu (mit `@conditional`)
  - `_UfoLegacySync.reset()` refactored
  - `_UfoLegacySync._reset_atomic()` neu (mit `@conditional`)

**Dokumentation**:
- `docs/dev/lock-usage-validation.md` (vollständige Analyse)

### Validierungsergebnisse

**Lock-Statistik projektweit**:
- RLocks: 5
- Conditions: 2
- `@synchronized`: 17 Verwendungen ✅
- `@conditional`: 4 Verwendungen ✅
- `@synchronized_module`: 2 Verwendungen ✅
- Manuelle Locks: 0 ✅
- Nested Locks: 0 ✅ (2 behoben)

**Multi-Lock-Pattern (korrekt)**:
- `CommandExecutor.process_commands()`: `@synchronized` + `with queue.lock:` 
  → Zwei verschiedene Objekte, kein nested lock ✅

### Best Practices - Eingehalten

1. ✅ Alle Locks via Decorators
2. ✅ Keine manuellen `acquire()/release()`
3. ✅ Keine manuellen `with self._lock:` Statements
4. ✅ Alle `notify_all()` unter `@conditional`
5. ✅ Exception-Safety durch automatisches Lock-Release

### Breaking Changes

**Keine** - Nur interne Implementierung geändert, API bleibt gleich.

### Referenzen

- **Dokumentation**: `docs/dev/lock-usage-validation.md`
- **Related**: Lock-Wrapper-Refactoring [2025-11-21]
- **Pattern**: @conditional für Condition-Variable-Methoden

---

## [2025-11-21] - Test-Struktur-Reorganisation nach Best Practice

### Zusammenfassung

Reorganisation der Test-Verzeichnisstruktur zur Spiegelung der Quellcode-Struktur gemäß Python-Best-Practices. Alle Tests wurden in eine hierarchische Ordnerstruktur verschoben, die der `src/`-Struktur entspricht.

### Problem/Motivation

Die Test-Dateien lagen alle flach im `tests/`-Root-Verzeichnis:
- Schwer nachvollziehbar welcher Test zu welchem Modul gehört
- Skaliert nicht bei wachsender Codebasis
- Verstößt gegen Python Testing Best Practices
- Keine klare Trennung nach Komponenten

### Lösung/Implementierung

#### Neue Struktur (spiegelt `src/core/simulation/`)

```
tests/
├── conftest.py
└── core/
    └── simulation/
        ├── exceptions/          # ← test_exceptions.py
        ├── infrastructure/      # ← test_logging_setup.py
        ├── physics/            # ← test_physics_engine.py
        ├── state/              # ← 4 Test-Dateien
        ├── synchronization/    # ← 4 Test-Dateien
        └── utils/              # ← 5 Test-Dateien
```

#### Durchgeführte Änderungen

**Verschobene Dateien** (15 Tests):
- `test_exceptions.py` → `core/simulation/exceptions/`
- `test_logging_setup.py` → `core/simulation/infrastructure/`
- `test_physics_engine.py` → `core/simulation/physics/`
- `test_state_*.py` (4 Dateien) → `core/simulation/state/`
- `test_*_lock.py` (4 Dateien) → `core/simulation/synchronization/`
- `test_*.py` (5 Utils) → `core/simulation/utils/`

**Umbenannt** (Konsistenz):
- `test_synchronization_instance_lock.py` → `test_instance_lock.py`
- `test_synchronization_module_lock.py` → `test_module_lock.py`

**Neue Dateien**:
- 8x `__init__.py` in Test-Verzeichnissen (korrekte Python-Package-Struktur)

### Vorteile

1. **Nachvollziehbarkeit**: 1:1 Mapping zwischen `src/` und `tests/`
2. **Best Practice**: Standard Python Testing Layout
3. **Skalierbarkeit**: Neue Module → neue Test-Verzeichnisse
4. **IDE-Support**: Bessere Navigation zwischen Code und Tests
5. **Übersichtlichkeit**: Klare Komponenten-Trennung

### Pytest-Kompatibilität

**Keine Änderungen notwendig**:
- ✅ `pyproject.toml`: `testpaths = ["tests"]` funktioniert (rekursive Suche)
- ✅ `setup.py`: Keine hardcodierten Pfade, funktioniert weiterhin
- ✅ Alle 16 Test-Dateien werden gefunden
- ✅ Keine Breaking Changes

### Betroffene Dateien

**Verschoben**: 15 Test-Dateien  
**Umbenannt**: 2 Test-Dateien  
**Neu erstellt**: 8x `__init__.py` (Test-Package-Struktur)  
**Dokumentation**: `docs/dev/test-structure-reorganization.md`

### Breaking Changes

**Keine** - Alle Test-Befehle funktionieren weiterhin:
```bash
pytest                                    # Alle Tests
pytest tests/core/simulation/utils/       # Modul-Tests
pytest tests/.../test_maths.py            # Spezifische Datei
```

### Referenzen

- **Python Testing Best Practices**: Tests spiegeln Quellcode-Struktur
- **pytest Documentation**: Hierarchical test discovery
- **PEP 8**: Package/Module naming conventions

---

## [2025-11-21] - Zentrale Lock-Wrapper-Utility (DRY-Refactoring)

### Zusammenfassung

Extraktion der gemeinsamen Lock-Wrapper-Logik aus den drei Decorators (`@synchronized`, `@conditional`, `@synchronized_module`) in eine zentrale Utility-Funktion zur Vermeidung von Code-Duplikation.

### Problem/Motivation

Die drei Lock-Decorators hatten nahezu identische Implementierungen:
- Alle nutzten `@wraps(method/func)`
- Alle hatten `try/finally` oder `with` für Lock-Management
- Alle waren exception-sicher
- **Unterschied**: Nur **welches Lock** verwendet wird

Dies verstieß gegen das **DRY-Prinzip** (Don't Repeat Yourself).

### Lösung/Implementierung

#### Zentrale `_lock_wrapper.py`
- Neue Funktion: `create_lock_wrapper(lock_getter)` - Factory für Lock-Decorators
- Context Manager: `_acquire_lock(lock)` - Einheitliche Lock-Acquisition
- Generisch: Funktioniert mit `Lock`, `RLock` und `Condition`
- Exception-sicher: Lock wird immer freigegeben

#### Refactored Decorators
Alle drei Decorators nutzen jetzt `create_lock_wrapper()`:

```python
# @synchronized
return create_lock_wrapper(lambda self, *args, **kwargs: self._lock)(method)

# @conditional  
return create_lock_wrapper(lambda self, *args, **kwargs: self._condition)(method)

# @synchronized_module
return create_lock_wrapper(lambda *args, **kwargs: lock)(func)
```

### Betroffene Dateien

**Neu erstellt**:
- `src/core/simulation/synchronization/_lock_wrapper.py`: Zentrale Lock-Utilities
- `tests/test_lock_wrapper.py`: Tests für Lock-Wrapper (9 Tests)

**Refactored**:
- `src/core/simulation/synchronization/instance_lock.py`: Nutzt `create_lock_wrapper()`
- `src/core/simulation/synchronization/conditional_lock.py`: Nutzt `create_lock_wrapper()`
- `src/core/simulation/synchronization/module_lock.py`: Nutzt `create_lock_wrapper()`

**Dokumentation**:
- `src/core/simulation/synchronization/__init__.py`: Dokumentation aktualisiert

### Code-Metriken

| Metrik | Vorher | Nachher | Verbesserung |
|--------|--------|---------|--------------|
| Lock-Wrapper Implementierungen | 3 | 1 | **-67%** |
| Zeilen Code (Decorators) | ~80 | ~40 | **-50%** |
| Code-Duplikation | ~60 Zeilen | 0 Zeilen | **-100%** |
| Test-Coverage | 3 separate | 1 zentral | **Vereinfacht** |

### Architektur-Prinzipien

- ✅ **DRY** (Don't Repeat Yourself): Keine Code-Duplikation mehr
- ✅ **Single Responsibility**: Zentrale Funktion für Lock-Wrapper-Logik
- ✅ **Composition**: Factory-Pattern für Decorator-Erstellung
- ✅ **Type Safety**: Generische Type Hints mit `Callable[..., Any]`

### Breaking Changes

**Keine** - Die öffentliche API (`@synchronized`, `@conditional`, `@synchronized_module`) bleibt vollständig kompatibel. Die `_lock_wrapper.py` ist privat (Prefix `_`) und nicht Teil der öffentlichen API.

### Referenzen

- **Diskussion**: User-Request zur Vermeidung von Redundanz in Decorator-Implementierungen
- **Pattern**: Factory Pattern für Decorator-Erstellung

---

## [2025-11-21] - Einführung von @conditional Decorator und ConditionWaiter

### Zusammenfassung

Implementierung eines zentralen `@conditional` Decorators für Methoden mit Condition-Variable-Unterstützung sowie Extraktion der redundanten `wait_for_condition()` Logik in eine wiederverwendbare `ConditionWaiter` Utility-Klasse.

### Problem/Motivation

1. **Nested Locks**: `update_state()` und `reset()` hatten nested lock Anti-Pattern (manuelles `with self._lock:` + `self._condition.notify_all()`)
2. **Code-Duplikation**: Identische `wait_for_condition()` Implementierung in StateManager und _UfoLegacySync (38 Zeilen Duplikation)
3. **Fehlende Abstraktion**: Kein dedizierter Decorator für Condition-Variable-basierte Methoden

### Lösung/Implementierung

#### 1. @conditional Decorator
- Neue Datei: `src/core/simulation/synchronization/conditional_lock.py`
- Decorator für Methoden die mit `threading.Condition` arbeiten
- Nutzt `self._condition.acquire()/release()` direkt
- Verhindert nested locks bei `notify_all()` Aufrufen
- Kompatibel mit RLock (wiedereintrittsfähig)

#### 2. ConditionWaiter Utility
- Neue Datei: `src/core/simulation/utils/condition_waiter.py`
- Stateless Utility-Klasse mit statischer Methode `wait_for_condition()`
- Generisch via TypeVar (funktioniert mit beliebigen State-Typen)
- Zentrale, wiederverwendbare Implementierung

#### 3. StateManager Refactoring
- `update_state()`: Nutzt private `@conditional` Methode `_update_state_atomic()`
- `reset()`: Nutzt private `@conditional` Methode `_reset_atomic()`
- `wait_for_condition()`: Delegiert an `ConditionWaiter.wait_for_condition()`
- Observer werden weiterhin außerhalb des Locks benachrichtigt (Deadlock-Vermeidung)

### Betroffene Dateien

**Neu erstellt**:
- `src/core/simulation/synchronization/conditional_lock.py`: @conditional Decorator
- `src/core/simulation/utils/condition_waiter.py`: ConditionWaiter Utility
- `tests/test_conditional_lock.py`: Tests für @conditional (9 Tests)
- `tests/test_condition_waiter.py`: Tests für ConditionWaiter (9 Tests)

**Geändert**:
- `src/core/simulation/state/manager.py`: Refactored mit @conditional
- `src/core/simulation/ufosim.py`: wait_for_condition delegiert an ConditionWaiter
- `src/core/simulation/synchronization/__init__.py`: Export von conditional
- `src/core/simulation/utils/__init__.py`: Export von ConditionWaiter

### Breaking Changes

Keine – Bestehende API bleibt vollständig kompatibel.

---

## [2025-11-19] - Dokumentations-Konsolidierung

### Zusammenfassung

Konsolidierung der Dokumentationsstruktur nach definierten Richtlinien mit klarer Trennung zwischen Entwickler-, Schüler- und Planungs-Dokumentation.

### Betroffene Dateien

**Neu erstellt**:
- `docs/guidelines/general-gd.md`: Allgemeine Dokumentations- und Code-Richtlinien
- `docs/planning/implementation-status.md`: Implementierungsstatus aller Refactoring-Tasks
- `docs/planning/refactoring-tracker.md`: Detailliertes Tracking mit Verantwortlichkeiten

**Reorganisiert**:
- Infrastructure-Dokumentation nach `docs/specs/architecture/`
- Setup-Anleitungen nach `docs/description/`
- Entwickler-Dokumentation nach `docs/dev/`

---

## [2025-11-18] - Refactoring T3: UfoState nach state/state.py

### Zusammenfassung

Migration von `UfoState` aus `ufosim.py` in dediziertes Modul `src/core/simulation/state/state.py` gemäß definierter Architektur.

### Implementierung

- Neue Datei: `src/core/simulation/state/state.py`
- Neues Package: `src/core/simulation/state/__init__.py`
- UfoState als frozen dataclass mit vollständigen Type Hints
- Alle Imports aktualisiert

### Tests

- 6 Smoke-Tests in `tests/test_state_import.py`
- Modul-Unabhängigkeit verifiziert

**Referenzen:**
- Implementierung: `src/core/simulation/state/state.py`
- Tests: `tests/test_state_import.py`

---

## [2025-11-18] - Refactoring T1: Importhierarchie dokumentiert

### Zusammenfassung

Definition und Dokumentation der 4-stufigen Importhierarchie für `core.simulation` Package.

### Hierarchie

- **Ebene 0**: `exceptions`, `infrastructure` (keine Abhängigkeiten)
- **Ebene 1**: `state`, `utils`, `physics` (nur Ebene 0)
- **Ebene 2**: `command`, `observer` (Ebene 0-1)
- **Ebene 3**: `controller`, `view` (alle Ebenen)

### Regeln

- Imports nur von niedrigeren Ebenen
- Keine zirkulären Abhängigkeiten
- Lazy Imports für TYPE_CHECKING

**Referenzen:**
- Dokumentation: `docs/specs/architecture/core-simulation-importregeln.md`

---

## [2025-11-18] - Refactoring T0: Zielbild dokumentiert

### Zusammenfassung

Erstellung des Architektur-Zielbilds für die UFO-Simulation mit allen geplanten Modulen und deren Verantwortlichkeiten.

### Ergebnis

- Package-Struktur mit 12 Modulen definiert
- Verantwortlichkeiten dokumentiert
- Öffentliche API-Definitionen festgelegt
- Design-Prinzipien formuliert (Clean Architecture, SOLID)

**Referenzen:**
- Zielbild: `docs/specs/architecture/core-simulation-zielbild.md`

---

