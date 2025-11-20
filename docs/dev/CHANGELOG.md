# Changelog – UFO-Simulation Schulung

Dieses Dokument protokolliert alle wesentlichen Änderungen am Projekt, sortiert nach Datum (neueste zuerst).

---

## Format-Konventionen

Jeder Changelog-Eintrag folgt diesem Schema:

```markdown
## [YYYY-MM-DD] - Kurztitel der Änderung

### Zusammenfassung

Kurze Beschreibung was geändert wurde und warum.

### Problem/Motivation

Welches Problem wurde gelöst? Was war der Auslöser?

### Lösung/Implementierung

Konkrete technische Umsetzung der Änderung.

### Betroffene Dateien

- `pfad/zu/datei.py`: Kurzbeschreibung der Änderung
- `pfad/zu/anderer.py`: Kurzbeschreibung der Änderung

### Impact

- **Entwickler**: Was müssen Entwickler beachten?
- **Schüler**: Was ändert sich für Schüler?
- **Breaking Changes**: ❌ oder "Keine"

### Referenzen

- Related Tickets: T1, T2
- Dokumentation: docs/dev/xxx.md
```

---

## [2025-11-19–2025-11-20] - Modul-Reorganisation und Dokumentations-Konsolidierung

### Zusammenfassung

Umfassende Reorganisation der `core.simulation` Paketstruktur:

- Exceptions-Modul zu Package-Struktur erweitert
- Neues Infrastructure-Package für Config und Logging erstellt
- Dokumentation konsolidiert: Modul-READMEs entfernt, zentrale __init__.py-Dokumentation
- Alle Module dokumentiert nach einheitlichem Standard

### Problem/Motivation

**Strukturelle Probleme:**

- `exceptions.py` und `config.py`/`logging_setup.py` als einzelne Dateien nicht skalierbar
- Fehlende Vorbereitung für zukünftige Exception-Kategorien (visualization, io, network)
- Keine klare Infrastruktur-Schicht

**Dokumentationsprobleme:**

- Redundanz zwischen README.md und Modul-Docstrings
- Inkonsistente Dokumentationsstile
- Pflegeaufwand durch mehrfache Wartung derselben Informationen
- README.md-Dateien in Modulen führten zu Fragmentierung

### Lösung/Implementierung

#### 1. Exceptions-Modul → Package-Struktur

**Neue Struktur:**

```
src/core/simulation/exceptions/
├── __init__.py          # Zentrale API-Definition
└── simulation.py        # Exception-Klassen
```

**Migration:**

- `exceptions.py` → `exceptions/simulation.py`
- Zentrale API in `__init__.py` definiert
- Vorbereitung für zukünftige Kategorien:
    - `visualization.py` (GUI-Fehler)
    - `io.py` (Datei-/Netzwerkfehler)
    - `network.py` (Kommunikationsfehler)

#### 2. Infrastructure-Package erstellt

**Neue Struktur:**

```
src/core/simulation/infrastructure/
├── __init__.py          # Zentrale API
├── config.py            # SimulationConfig
└── logging_setup.py     # Logging-Setup
```

**Design-Prinzipien:**

- Framework-unabhängig
- Thread-sicher
- Keine Simulationslogik
- Wiederverwendbar in anderen Kontexten

**Zukünftige Erweiterungen vorbereitet:**

- `metrics.py` – Performance-Metriken
- `profiling.py` – Profiling-Tools
- `validation.py` – Input-Validierung
- `serialization.py` – State-Serialisierung

#### 3. Dokumentations-Konsolidierung

**Konzept:**

- **Eine Dokumentationsquelle** pro Modul: die `__init__.py`-Datei
- Modul-Übersicht, Struktur und Beispiele zentral
- Einzeldateien: Nur spezifische Docstrings

**Struktur pro `__init__.py`:**

```python
"""
1. Modulzweck und strukturelle Verantwortlichkeiten
2. Modul-Bestandteile
3. Öffentliche API
4. Verwendungsbeispiele
5. Architektur-Prinzipien
"""
```

**Reduzierung:**

- exceptions: 140 → 51 Zeilen (-63%)
- infrastructure: 172 → 50 Zeilen (-71%)
- state: 185 → 50 Zeilen (-73%)
- synchronization: 160 → 60 Zeilen (-62%)

**Gelöschte READMEs:**

- `src/core/simulation/exceptions/README.md`
- `src/core/simulation/infrastructure/README.md`
- `src/core/simulation/state/README.md`
- `src/core/simulation/synchronization/README.md`

### Betroffene Dateien

**Neu erstellt:**

- `src/core/simulation/exceptions/` (Package)
    - `exceptions/__init__.py`
    - `exceptions/simulation.py`
- `src/core/simulation/infrastructure/` (Package)
    - `infrastructure/__init__.py`
    - `infrastructure/config.py`
    - `infrastructure/logging_setup.py`
- `docs/planning/REFACTORING_INFRASTRUCTURE.md`
- `docs/planning/REFACTORING_DOCUMENTATION.md`

**Verschoben:**

- `exceptions.py` → `exceptions/simulation.py`
- `config.py` → `infrastructure/config.py`
- `logging_setup.py` → `infrastructure/logging_setup.py`

**Gelöscht:**

- `src/core/simulation/exceptions.py`
- `src/core/simulation/config.py`
- `src/core/simulation/logging_setup.py`
- Alle Modul-README.md-Dateien

**Aktualisiert (Imports):**

- `src/core/simulation/__init__.py`
- `src/core/simulation/ufosim.py`
- `tests/test_logging_setup.py`

**Aktualisiert (Dokumentation):**

- `src/core/simulation/exceptions/__init__.py`
- `src/core/simulation/exceptions/simulation.py`
- `src/core/simulation/infrastructure/__init__.py`
- `src/core/simulation/infrastructure/config.py`
- `src/core/simulation/infrastructure/logging_setup.py`
- `src/core/simulation/state/__init__.py`
- `src/core/simulation/state/state.py`
- `src/core/simulation/synchronization/__init__.py`
- `src/core/simulation/synchronization/instance_lock.py`
- `src/core/simulation/synchronization/module_lock.py`

### Impact

**Entwickler:**

- ✅ Klarere Package-Struktur
- ✅ Bessere Skalierbarkeit (Exception-Kategorien, Infrastructure-Komponenten)
- ⚠️ Import-Pfade geändert (aber API bleibt kompatibel):
  ```python
  # Alt
  from core.simulation.exceptions import SimulationError
  from core.simulation.config import SimulationConfig
  
  # Neu (aber alte Imports funktionieren weiter)
  from core.simulation.exceptions import SimulationError  # unverändert
  from core.simulation.infrastructure import SimulationConfig  # oder direkt
  ```
- ✅ Reduzierter Dokumentations-Pflegeaufwand
- ✅ Konsistente Dokumentation über alle Module

**Schüler:**

- Keine Änderungen (nur interne Struktur)

**Breaking Changes:**

- Keine – API bleibt kompatibel durch Re-Exports in `__init__.py`

### Validierung

- ✅ Alle 52 Tests erfolgreich
- ✅ Keine funktionalen Änderungen
- ✅ API-Kompatibilität gewahrt

### Statistik

- **Dateien geändert:** 17
- **Zeilen hinzugefügt:** 924
- **Zeilen entfernt:** 394
- **Netto:** +530 Zeilen (hauptsächlich Dokumentation)
- **Dokumentationsreduktion:** 63–76% in Einzeldateien

### Referenzen

- Related Tickets: T4 (Infrastructure-Basis)
- Commit: `df334a3`
- Dokumentation: `docs/planning/REFACTORING_INFRASTRUCTURE.md`, `docs/planning/REFACTORING_DOCUMENTATION.md`

---

## [2025-11-19] - T6: Mathematische Utilities (utils/maths.py, validation.py, geometry.py)

### Zusammenfassung

Implementierung von drei neuen Utility-Modulen für mathematische, geometrische und Validierungs-Funktionen:

- `utils/maths.py` – Numerische Hilfsfunktionen
- `utils/validation.py` – Eingabe-Validierung
- `utils/geometry.py` – Geometrische Berechnungen

### Problem/Motivation

**Fehlende Abstraktion:**

- Mathematische Operationen (Winkelkonvertierung, Clamping, etc.) waren über Codebase verteilt
- Keine zentrale Validierung von Eingaben
- Geometrische Berechnungen (Distanz, Winkel) in verschiedenen Modulen dupliziert
- Magic Numbers ohne Erklärung

**Wartbarkeitsprobleme:**

- Wiederholter Code
- Schwierige Testbarkeit
- Keine einheitlichen Fehlerbehandlungen

### Lösung/Implementierung

#### 1. utils/maths.py

**Numerische Hilfsfunktionen:**

```python
def deg_to_rad(degrees: float) -> float


    def rad_to_deg(radians: float) -> float


    def wrap_angle_deg(angle: float) -> float


    def wrap_angle_rad(angle: float) -> float


    def clamp(value: float, min_val: float, max_val: float) -> float


    def lerp(a: float, b: float, t: float) -> float


    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float
```

**Features:**

- Physikalisch korrekte Winkelberechnungen
- Robuste Division mit Fallback
- Type-Hints und umfassende Docstrings

#### 2. utils/validation.py

**Eingabe-Validierung:**

```python
def validate_range(value: float, min_val: float, max_val: float, name: str)


    def validate_positive(value: float, name: str)


    def validate_non_negative(value: float, name: str)
```

**Features:**

- Klare Fehlermeldungen
- Konsistente Exceptions
- Wiederverwendbar in allen Modulen

#### 3. utils/geometry.py

**Geometrische Berechnungen:**

```python
def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float


    def angle_between_points(x1: float, y1: float, x2: float, y2: float) -> float
```

**Features:**

- Vektorbasierte Berechnungen
- Benannte Konstanten statt Magic Numbers:
  ```python
  EPSILON_DISTANCE = 1e-10  # Minimale Distanz für Winkelberechnung
  ```

### Betroffene Dateien

**Neu erstellt:**

- `src/core/simulation/utils/maths.py` (189 Zeilen)
- `src/core/simulation/utils/validation.py` (85 Zeilen)
- `src/core/simulation/utils/geometry.py` (78 Zeilen)
- `tests/test_maths.py` (umfassende Tests)
- `tests/test_validation.py`
- `tests/test_geometry.py`

**Aktualisiert:**

- `src/core/simulation/utils/__init__.py` (Exports hinzugefügt)

### Impact

**Entwickler:**

- ✅ Framework-unabhängige mathematische Utilities verfügbar
- ✅ Konsistente Validierung in gesamter Codebase
- ✅ Reduzierung von Code-Duplikation
- ✅ Bessere Testbarkeit durch isolierte Funktionen
- ✅ Keine Magic Numbers mehr

**Schüler:**

- ✅ Können Utility-Funktionen in Tasks verwenden
- ✅ Bessere Fehlermeldungen bei ungültigen Eingaben

**Breaking Changes:**

- Keine – nur neue Funktionalität

### Performance-Optimierungen

- Vermeidung unnötiger Berechnungen (z.B. frühe Rückgaben)
- Verwendung von numpy wo sinnvoll
- Optimierte Winkelberechnungen

### Code-Qualität

- ✅ Umfassende Docstrings (Google-Stil)
- ✅ Type-Hints für alle Funktionen
- ✅ Unit-Tests mit >90% Coverage
- ✅ Performance-Tests für kritische Funktionen

### Referenzen

- Related Tickets: T6
- PR: #13
- Commits: `f2b7013`, `cbee8b3`, `f4f6bc9`, `bfd4179`, `15cbc73`
- Dokumentation: Repository-Konvention eingehalten

---

## [2025-11-19] - T5: Threading Utilities (synchronization/)

### Zusammenfassung

Implementierung eines konsistenten Threading-Systems mit Decorators für Thread-Sicherheit:

- `@synchronized` Decorator für Instanz-Locks
- `@synchronized_global` Decorator für Modul-Locks
- Umfassendes Testing-Framework für Nebenläufigkeit
- Refactoring aller bestehenden Lock-Pattern

### Problem/Motivation

**Inkonsistente Thread-Sicherheit:**

- Lock-Handling manuell in jeder Methode
- Verschiedene Lock-Patterns über Codebase verteilt
- Fehleranfällig und schwer wartbar
- Keine standardisierte Lösung

**Fehlende Tools:**

- Keine Debugging-Tools für Threading-Probleme
- Schwierige Identifikation von Deadlocks
- Keine Performance-Überwachung bei Parallelität

### Lösung/Implementierung

#### 1. Decorator-basiertes Lock-System

**@synchronized (Instanz-Locks):**

```python
from core.simulation.synchronization import synchronized


class MyClass:
    def __init__(self):
        self._lock = threading.RLock()

    @synchronized
    def thread_safe_method(self):
        # Thread-sicher durch Decorator
        pass
```

**@synchronized_global (Modul-Locks):**

```python
from core.simulation.synchronization import synchronized_global

_module_lock = threading.RLock()


@synchronized_global
def module_level_function():
    # Thread-sicher auf Modul-Ebene
    pass
```

**Features:**

- Automatisches Lock-Handling
- RLock für Re-Entrancy
- Klare Fehler wenn Lock fehlt
- Minimaler Overhead

#### 2. Refactoring bestehender Code

**Aktualisiert:**

- `StateManager`: Alle Methoden mit `@synchronized`
- `CommandExecutor`: Lock-Pattern vereinheitlicht
- `logging_setup.py`: `@synchronized_global` für `get_logger()`

**Vorher:**

```python
def method(self):
    with self._lock:
# ... Code ...
```

**Nachher:**

```python
@synchronized
def method(self):
# ... Code ... (Lock automatisch)
```

#### 3. Testing-Framework

**Neue Tools installiert:**

- `pytest-timeout` – Deadlock-Erkennung
- `threadpoolctl` – Thread-Pool Kontrolle
- `py-spy` – Profiling für Threading

**Pytest-Markers:**

```python
@pytest.mark.threading  # Threading-Tests
@pytest.mark.slow  # Langlaufende Tests
@pytest.mark.deadlock  # Deadlock-Tests
```

**Tests:**

- `test_synchronization_instance_lock.py` – Instanz-Lock Tests
- `test_synchronization_module_lock.py` – Modul-Lock Tests
- `test_threading_tools_demo.py` – Demonstrations-Tests

#### 4. Umbenennung utils/ → synchronization/

**Rationale:**

- Klarere semantische Bedeutung
- Bessere Trennung von anderen Utilities
- Vorbereitung für weitere Threading-Tools

**Struktur:**

```
src/core/simulation/synchronization/
├── __init__.py
├── instance_lock.py     # @synchronized
└── module_lock.py       # @synchronized_global
```

### Betroffene Dateien

**Neu erstellt:**

- `src/core/simulation/utils/threads.py` (später → synchronization/)
- `src/core/simulation/synchronization/instance_lock.py`
- `src/core/simulation/synchronization/module_lock.py`
- `tests/test_synchronization_instance_lock.py`
- `tests/test_synchronization_module_lock.py`
- `tests/test_threading_tools_demo.py`

**Aktualisiert:**

- `src/core/simulation/state/manager.py` (StateManager mit @synchronized)
- `src/core/simulation/logging_setup.py` (mit @synchronized_global)
- `requirements.txt` (neue Test-Dependencies)
- `pyproject.toml` (pytest-Markers)

**Umbenannt:**

- `utils/` → `synchronization/` (gesamtes Package)

### Impact

**Entwickler:**

- ✅ Konsistentes Thread-Safety Pattern
- ✅ Reduzierter Boilerplate-Code
- ✅ Bessere Wartbarkeit
- ✅ Umfangreiche Test-Tools
- ⚠️ Import-Pfade geändert:
  ```python
  # Alt (hypothetisch)
  from core.simulation.utils.threads import synchronized
  
  # Neu
  from core.simulation.synchronization import synchronized
  ```

**Schüler:**

- Keine direkten Auswirkungen (interne API)

**Breaking Changes:**

- ⚠️ Package-Umbenennung `utils/` → `synchronization/`
- ✅ API bleibt kompatibel durch Re-Exports

### Qualitätssicherung

- ✅ Umfassende Threading-Tests
- ✅ Deadlock-Erkennung durch pytest-timeout
- ✅ Code-Review durchgeführt
- ✅ Performance-Validierung

### Referenzen

- Related Tickets: T5
- PR: #12
- Commits: `92657f2`, `b4bd754`, `6f561a6`, `ba29984`, `e40b4b4`, `557c97a`, `db7e4e0`
- Tools: pytest-timeout, threadpoolctl, py-spy

---

## [2025-11-18] - T4: Exceptions & Logging Infrastructure

### Zusammenfassung

Implementierung der Basis-Infrastruktur für Fehlerbehandlung und Logging:

- Exception-Hierarchie mit `SimulationError` als Basis
- Thread-sicheres Logging-Setup mit einmaliger Konfiguration
- Vorbereitung für zukünftige Exception-Kategorien

### Problem/Motivation

**Fehlende Exception-Hierarchie:**

- Keine projekt-spezifischen Exception-Klassen
- Schwierige Unterscheidung zwischen verschiedenen Fehlertypen
- Keine konsistente Fehlerbehandlung

**Unstrukturiertes Logging:**

- Logging ad-hoc konfiguriert
- Keine Thread-Sicherheit
- Mehrfache Initialisierungen möglich
- Inkonsistente Log-Formate

### Lösung/Implementierung

#### 1. Exception-Hierarchie (exceptions.py)

**Basis-Klasse:**

```python
class SimulationError(Exception):
    """Basis-Exception für alle Simulationsfehler."""
    pass
```

**Spezialisierte Exceptions:**

```python
class ConfigError(SimulationError):
    """Fehler in der Simulationskonfiguration."""
    pass


class StateValidationError(SimulationError):
    """Fehler bei State-Validierung."""
    pass


class PhysicsError(SimulationError):
    """Fehler in der Physik-Engine."""
    pass
```

**Design-Prinzipien:**

- Klare Hierarchie
- Aussagekräftige Namen
- Erweiterbar für zukünftige Kategorien

#### 2. Thread-sicheres Logging (logging_setup.py)

**Implementierung:**

```python
_logger_cache: dict[str, logging.Logger] = {}
_logging_configured: bool = False
_lock = threading.RLock()


def configure_logging(level: int = logging.INFO) -> None:
    """Konfiguriert Logging einmalig (thread-sicher)."""
    global _logging_configured
    with _lock:
        if _logging_configured:
            return
        # ... Konfiguration ...
        _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Liefert gecachten Logger (thread-sicher)."""
    with _lock:
        if name not in _logger_cache:
            _logger_cache[name] = logging.getLogger(name)
        return _logger_cache[name]
```

**Features:**

- Einmalige Konfiguration (Idempotenz)
- RLock statt Lock (Re-Entrancy)
- Logger-Caching für Performance
- Thread-sicher

#### 3. Race-Condition Fix

**Problem gefunden:**

```python
# Unsicher:
if name not in _logger_cache:
    _logger_cache[name] = logging.getLogger(name)
return _logger_cache[name]
```

**Lösung:**

```python
# Thread-sicher:
with _lock:
    if name not in _logger_cache:
        _logger_cache[name] = logging.getLogger(name)
    return _logger_cache[name]
```

### Betroffene Dateien

**Neu erstellt:**

- `src/core/simulation/exceptions.py` (84 Zeilen)
- `src/core/simulation/logging_setup.py` (145 Zeilen)
- `tests/test_exceptions.py`
- `tests/test_logging_setup.py`

**Aktualisiert:**

- `src/core/simulation/__init__.py` (Exports hinzugefügt)

### Impact

**Entwickler:**

- ✅ Konsistente Exception-Hierarchie verfügbar
- ✅ Thread-sicheres Logging out-of-the-box
- ✅ Klare Fehler-Kategorisierung möglich
- ✅ Logger-Caching für bessere Performance

**Schüler:**

- ✅ Bessere Fehlermeldungen
- ✅ Konsistentes Log-Format

**Breaking Changes:**

- Keine – nur neue Funktionalität

### Qualitätssicherung

- ✅ Thread-Safety validiert
- ✅ Race-Condition behoben
- ✅ Unit-Tests für beide Module
- ✅ RLock-Konsistenz mit Codebase

### Referenzen

- Related Tickets: T4
- PR: #11
- Commits: `1c7e4f7`, `17e9c3f`, `5b3c9e9`
- Follow-up: Modul-Reorganisation (siehe oben)

---

## [2025-11-16] - T3: State-Extraktion mit Immutability-Pattern

### Zusammenfassung

Extraktion des `UfoState` in separates Modul mit vollständiger Immutability:

- `UfoState` als frozen Dataclass
- `StateProxy` für View-Layer
- Lazy Property-Berechnung
- Refactoring von PhysicsEngine und StateManager

### Problem/Motivation

**Strukturelle Probleme:**

- `UfoState` war Teil von `ufosim.py` (tight coupling)
- Keine klare Trennung zwischen State-Modell und State-Management
- Mutable State führte zu unvorhersehbaren Seiteneffekten

**Architektonische Ziele:**

- Immutable State (Copy-on-Write Pattern)
- Klare Verantwortlichkeiten
- Bessere Testbarkeit
- Thread-Safety durch Immutability

### Lösung/Implementierung

#### 1. UfoState als frozen Dataclass

**state/state.py:**

```python
@dataclass(frozen=True)
class UfoState:
    """Immutable UFO-Zustand."""
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float

    # ... weitere Felder ...

    @property
    def position_vector(self) -> np.ndarray:
        """Lazy-berechneter Positions-Vektor."""
        return np.array([self.x, self.y, self.z])
```

**Vorteile:**

- Thread-sicher durch Immutability
- Keine unerwarteten Seiteneffekte
- Klare Copy-Semantik

#### 2. StateProxy für View-Layer

**Zweck:**

- Trennung View-Daten von Kern-State
- Lazy Berechnung komplexer Properties
- Reduzierung der State-Größe

**Implementierung:**

```python
class StateProxy:
    """Read-only View auf UfoState mit lazy Properties."""

    def __init__(self, state: UfoState):
        self._state = state

    @property
    def velocity_magnitude(self) -> float:
        """Berechnet nur wenn benötigt."""
        return np.linalg.norm(self._state.velocity_vector)
```

#### 3. PhysicsEngine Refactoring

**Copy-on-Write Pattern:**

```python
# Alt (mutiert State direkt):
def integrate_step(self, state: UfoState) -> tuple[bool, bool]:
    state.vz += acceleration * dt  # ❌ Mutation


# Neu (immutable):
def integrate_step(self, state: UfoState) -> tuple[UfoState, bool, bool]:
    new_state = dataclasses.replace(
        state,
        vz=state.vz + acceleration * dt
    )
    return new_state, is_landed, crashed  # ✅ Neuer State
```

#### 4. StateManager Refactoring

**Thread-sicheres Update:**

```python
def update_state(self, updater: Callable[[UfoState], UfoState]) -> None:
    """Atomares State-Update."""
    with self._lock:
        self._current_state = updater(self._current_state)
        self._notify_observers()
```

### Betroffene Dateien

**Neu erstellt:**

- `src/core/simulation/state/state.py` (UfoState + StateProxy)
- `tests/test_state.py` (10 neue Tests)

**Aktualisiert:**

- `src/core/simulation/physics/engine.py` (PhysicsEngine)
- `src/core/simulation/state/manager.py` (StateManager)
- `src/core/simulation/ufosim.py` (Integration)

**Dokumentation:**

- `docs/planning/implementation-status.md` (T3 als abgeschlossen)

### Impact

**Entwickler:**

- ✅ Immutable State Pattern etabliert
- ✅ Bessere Thread-Safety
- ✅ Klarere Datenflüsse
- ⚠️ API-Änderung:
  ```python
  # Alt
  physics_engine.integrate_step(state)  # mutiert state
  
  # Neu
  new_state, landed, crashed = physics_engine.integrate_step(state)
  ```

**Schüler:**

- Keine direkten Auswirkungen (interne API)

**Breaking Changes:**

- ⚠️ PhysicsEngine.integrate_step() Signatur geändert
- ⚠️ State-Updates nur noch über dataclasses.replace()

### Qualitätssicherung

- ✅ 10 neue Tests (alle erfolgreich)
- ✅ PhysicsEngine-Tests aktualisiert
- ✅ StateManager-Tests aktualisiert
- ✅ TODO-Kommentare für Refactoring entfernt

### Architektonische Verbesserungen

- **Immutability:** Keine Seiteneffekte mehr
- **Separation of Concerns:** State-Modell unabhängig von Management
- **Testbarkeit:** Isolierte Unit-Tests möglich
- **Thread-Safety:** Durch Immutability inherent thread-sicher

### Referenzen

- Related Tickets: T3
- PR: #10
- Commits: `245f79f`, `86cc29a`, `fdeedea`, `5a2b535`, `d798b4e`, `32669ad`
- Dokumentation: T3-SUMMARY.md

---

## [2025-11-15] - T2: Konfigurationsmodul (config.py)

### Zusammenfassung

Extraktion der Simulationskonfiguration in dediziertes Modul:

- `SimulationConfig` als Dataclass
- `DEFAULT_CONFIG` als Standard-Konfiguration
- Vollständige Typisierung und Dokumentation

### Problem/Motivation

**Konfiguration war hartcodiert:**

- Magic Numbers in `ufosim.py` verteilt
- Keine zentrale Konfiguration
- Schwierig zu testen
- Keine Möglichkeit zur Anpassung ohne Code-Änderung

**Ziele:**

- Zentrale Konfiguration
- Einfache Anpassbarkeit
- Validierung von Parametern
- Dokumentation der Bedeutung jedes Parameters

### Lösung/Implementierung

#### 1. SimulationConfig Dataclass

**config.py:**

```python
@dataclass
class SimulationConfig:
    """Zentrale Konfiguration der UFO-Simulation.
    
    Alle physikalischen und technischen Parameter werden hier definiert.
    """
    # Zeitsteuerung
    dt: float = 0.1  # Sekunden pro Simulationsschritt
    update_interval_ms: int = 100  # GUI-Update-Intervall

    # Physikalische Parameter
    gravity: float = 1.62  # m/s² (Mond-Gravitation)
    max_thrust: float = 45.0  # m/s² maximale Schubkraft

    # Landing-Assistance
    landing_assistance_height: float = 50.0  # m
    landing_assistance_max_tilt: float = 3.0  # Grad

    # Landungskriterien
    landing_max_velocity: float = 2.0  # m/s
    landing_max_tilt: float = 5.0  # Grad

    # ... weitere Parameter ...
```

**Features:**

- Gruppierung nach Kategorien
- Kommentare mit Einheiten
- Default-Werte aus Original-Code
- Type-Hints für alle Felder

#### 2. DEFAULT_CONFIG

```python
DEFAULT_CONFIG = SimulationConfig()
```

**Verwendung:**

```python
# Standard-Konfiguration
sim = UfoSim()

# Angepasste Konfiguration
custom_config = SimulationConfig(gravity=9.81, max_thrust=60.0)
sim = UfoSim(config=custom_config)

# Partielle Anpassung
config = dataclasses.replace(DEFAULT_CONFIG, dt=0.05)
sim = UfoSim(config=config)
```

#### 3. Integration in UfoSim

**ufosim.py:**

```python
class UfoSim:
    def __init__(self, config: SimulationConfig = DEFAULT_CONFIG):
        self.config = config
        self.dt = config.dt
        # ... weitere Initialisierung ...
```

### Betroffene Dateien

**Neu erstellt:**

- `src/core/simulation/config.py` (125 Zeilen)
- `tests/test_config.py`

**Aktualisiert:**

- `src/core/simulation/ufosim.py` (Integration)
- `src/core/simulation/__init__.py` (Export)

### Impact

**Entwickler:**

- ✅ Zentrale Konfiguration verfügbar
- ✅ Einfache Anpassung für Tests
- ✅ Klare Dokumentation aller Parameter
- ✅ Keine Magic Numbers mehr

**Schüler:**

- ✅ Können Simulation einfach anpassen
- ✅ Verständnis durch dokumentierte Parameter

**Breaking Changes:**

- Keine – UfoSim() funktioniert weiter mit Defaults

### Qualitätssicherung

- ✅ Tests erfolgreich
- ✅ Integration in bestehenden Code validiert
- ✅ Dokumentation vollständig

### Referenzen

- Related Tickets: T2
- PR: #6
- Commit: `7444352`

---

## [2025-11-20] - Dokumentations-Reorganisation

### Zusammenfassung

Die gesamte Dokumentation wurde umfassend reorganisiert und konsolidiert, um Übersichtlichkeit zu schaffen und Redundanz
zu eliminieren.

### Problem/Motivation

Die Dokumentation in `docs/planning/` wurde unübersichtlich:

- 10+ separate Dokumente für Setup-Änderungen
- Redundante Informationen über mehrere Dateien verteilt
- Keine klare Zielgruppen-Trennung (Schüler vs. Entwickler)
- Fehlende zentrale Übersicht

### Lösung/Implementierung

#### 1. Neuer Ordner `docs/dev/` erstellt

Zentrale Entwickler-Dokumentation mit einheitlichem Format:

- `CHANGELOG.md` – Konsolidierte Änderungshistorie (dieses Dokument)
- `SETUP.md` – Setup-System-Dokumentation
- `TESTING_TOOLS.md` – Testing- und Debugging-Tools
- `REORGANIZATION_SUMMARY.md` – Detaillierte Dokumentation dieser Reorganisation
- `README.md` – Übersicht mit Format-Konventionen

#### 2. Schüler-Dokumentation erweitert (`docs/description/`)

- `setup-guide.md` – Schüler-freundliche Setup-Anleitung (NEU)
- `README.md` – Übersicht Schüler-Dokumentation (NEU)

#### 3. Planungs-Dokumentation bereinigt (`docs/planning/`)

- `implementation-status.md` – Vollständig überarbeitet mit Status T0-T17
- `refactoring-tracker.md` – Aktualisiert mit Abschluss-Daten
- `README.md` – Übersicht mit Workflow (NEU)
- `_archived/` – 11 obsolete Dokumente archiviert

#### 4. Zentrale Übersicht erstellt

- `docs/README.md` – Navigation für alle Dokumentations-Kategorien (NEU)

### Betroffene Dateien

**Neu erstellt**:

- `docs/README.md`
- `docs/dev/README.md`
- `docs/dev/CHANGELOG.md` (dieses Dokument)
- `docs/dev/SETUP.md`
- `docs/dev/TESTING_TOOLS.md`
- `docs/dev/REORGANIZATION_SUMMARY.md`
- `docs/description/README.md`
- `docs/description/setup-guide.md`
- `docs/planning/README.md`

**Aktualisiert**:

- `docs/planning/implementation-status.md` – Vollständig überarbeitet
- `docs/planning/refactoring-tracker.md` – Status-Spalte aktualisiert

**Archiviert** (nach `docs/planning/_archived/`):

- `CHECKLISTE_ERROR_LOG.md`
- `CHECKLISTE_MINIMIERTE_AUSGABE.md`
- `REFACTORING_BOOTSTRAP_ENV.md`
- `REFACTORING_DOCUMENTATION.md`
- `REFACTORING_INFRASTRUCTURE.md`
- `SETUP_ERROR_LOG_STRATEGIE.md`
- `SETUP_LOG_GITIGNORE.md`
- `SETUP_OUTPUT_MINIMIERUNG.md`
- `TESTING_DEBUGGING_TOOLS.md`
- `setup-usage.md`
- `implementation-status-old.md`

**Konsolidiert**:

- 10 Setup/Refactoring-Dokumente → `docs/dev/CHANGELOG.md` (als Changelog-Einträge)
- `TESTING_DEBUGGING_TOOLS.md` → `docs/dev/TESTING_TOOLS.md` (umbenannt und erweitert)
- `setup-usage.md` → `docs/description/setup-guide.md` (Schüler-fokussiert)

### Impact

**Entwickler**:

- ✅ Klare Trennung: Entwickler-Docs in `docs/dev/`
- ✅ Einheitliches Changelog-Format für alle Änderungen
- ✅ Zentrale Übersicht über alle Dokumentations-Kategorien
- ✅ Migration Guide in `REORGANIZATION_SUMMARY.md`

**Schüler**:

- ✅ Neue schüler-freundliche Setup-Anleitung
- ✅ Klare Trennung von technischer Entwickler-Dokumentation
- ✅ Einfachere Navigation durch READMEs

**Maintainer**:

- ✅ Reduzierte Redundanz (~80% weniger Dokumente in planning/)
- ✅ Bessere Wartbarkeit durch Single Source of Truth
- ✅ Klare Workflows für Dokumentations-Pflege

**Breaking Changes**:

- ⚠️ Dokumenten-Pfade haben sich geändert (siehe Migration Guide in `REORGANIZATION_SUMMARY.md`)
- ✅ Alte Dokumente sind archiviert und weiterhin verfügbar unter `docs/planning/_archived/`

### Statistik

- **Neue Dateien**: 9
- **Aktualisierte Dateien**: 2
- **Archivierte Dateien**: 11
- **Reduzierung in docs/planning**: ~80% (11 → 2 aktive Dokumente)

### Referenzen

- Detaillierte Dokumentation: [docs/dev/REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)
- Planungs-Workflow: [docs/planning/README.md](../planning/README.md)
- Zentrale Übersicht: [docs/README.md](../README.md)

---

## [2025-11-20] - Setup-Ausgabe minimiert mit Progress-Bars

### Zusammenfassung

Die Setup-Ausgabe wurde drastisch reduziert (~73-90% weniger Text) durch Einführung von Progress-Bars für alle
langwierigen Operationen.

### Problem/Motivation

Die Setup-Ausgabe war zu umfangreich und überwältigend für Schüler:

- Projekt-Installation zeigte ~30 Zeilen Build-Details
- Test-Ausführung zeigte jeden einzelnen Test
- Pip-Updates zeigten vollständige Download-Informationen
- Schwierig zu erkennen, ob alles funktioniert oder wo Probleme sind

### Lösung/Implementierung

#### 1. Progress-Bar Klasse

Neue `ProgressBar`-Klasse in `tools/bootstrap_env.py`:

- ASCII-basierter Progress-Bar (keine externen Dependencies)
- Methoden: `update(percent, status)` und `finish(message)`
- Thread-sicher durch stdout-Lock

#### 2. Minimierte Projekt-Installation

- Background-Thread für `pip install -e .`
- Progress-Bar mit simulierten Phasen:
    - 20%: Prüfe Build-Backend
    - 40%: Ermittle Requirements
    - 60%: Erstelle Metadata
    - 80%: Installiere Package
    - 95%: Finalisiere Installation
- Vollständiger Output weiterhin in `setup.log`

#### 3. Minimierte Test-Ausführung

- Background-Thread für `pytest`
- Progress-Bar während Tests laufen
- Nur Zusammenfassung anzeigen
- Bei Fehlern: Letzte 5 relevante Zeilen

#### 4. Minimierte Pip-Updates

- `--quiet` Flag für pip-Befehle
- `capture_output=True` für subprocess
- Nur Erfolgs-/Fehlermeldung sichtbar

### Betroffene Dateien

- `tools/bootstrap_env.py`:
    - Neue Klasse `ProgressBar` hinzugefügt
    - `install_project_editable()`: Background-Thread + Progress-Bar
    - `run_tests()`: Background-Thread + Progress-Bar
    - `update_pip()`, `ensure_pip_index_url()`: Output unterdrückt
- `tests/test_progress_bar.py`: Tests für Progress-Bar erstellt

### Impact

- **Entwickler**: Vollständiger Output weiterhin in `setup.log` verfügbar
- **Schüler**: Deutlich übersichtlichere Setup-Ausgabe, leichter zu verstehen
- **Breaking Changes**: Keine (nur UI-Änderung)

### Messbare Verbesserungen

- Projekt-Installation: ~30 Zeilen → 3 Zeilen (~90% Reduktion)
- Test-Ausführung: ~15 Zeilen → 4 Zeilen (~73% Reduktion)
- Pip-Updates: ~10 Zeilen → 1 Zeile (~90% Reduktion)

### Referenzen

- Tests: `tests/test_progress_bar.py`
- Original-Planung: docs/planning/CHECKLISTE_MINIMIERTE_AUSGABE.md

---

## [2025-11-20] - Error-Only Logging für setup.log

### Zusammenfassung

Die `setup.log` Datei wird nun nur noch bei Fehlern erstellt und enthält ausschließlich Fehlerinformationen.

### Problem/Motivation

Die `setup.log` wurde bei jedem Setup-Durchlauf beschrieben:

- Bei erfolgreichem Setup: Datei voll mit erfolgreichen Installationen
- Bei Fehler: Fehler zwischen vielen erfolgreichen Einträgen versteckt
- Lehrer mussten durch viele Einträge scrollen
- Unübersichtlich bei mehreren Setup-Versuchen

### Lösung/Implementierung

#### Neue Hilfsfunktion

`log_error_to_file(log_file, section, error_info, details="")`:

- Erstellt Log-Datei beim ersten Fehler
- Fügt Header hinzu ("# Setup Error Log")
- Append-Modus für weitere Fehler
- Timestamp für jeden Fehler
- Strukturierte Ausgabe mit Section-Header

#### Geänderte Funktionen

Alle Installations-Funktionen nutzen nun `log_error_to_file()`:

- `install_runtime_requirements()`: Logging nur bei Fehler entfernt
- `install_dev_requirements()`: Logging nur bei Fehler entfernt
- `install_project_editable()`: Logging nur bei Fehler entfernt

### Betroffene Dateien

- `tools/bootstrap_env.py`:
    - Neue Funktion `log_error_to_file()` hinzugefügt
    - Alle Installations-Funktionen angepasst
    - Erfolgs-Logging entfernt

### Impact

- **Entwickler**: Lehrer sehen sofort was schiefgelaufen ist
- **Schüler**: Bei erfolgreichem Setup keine setup.log (sauberes Verzeichnis)
- **Breaking Changes**: Keine (setup.log wird weiterhin bei Fehlern erstellt)

### Referenzen

- Original-Planung: docs/planning/CHECKLISTE_ERROR_LOG.md

---

## [2025-11-20] - setup.log zu .gitignore hinzugefügt

### Zusammenfassung

Die `setup.log` Datei wird nun von Git ignoriert, da sie entwicklerspezifisch ist.

### Problem/Motivation

- Lokale Fehlerprotokolle könnten versehentlich committed werden
- Alte Fehler würden bei `git pull` übernommen
- Unnötiger Clutter im Repository

### Lösung/Implementierung

`setup.log` zur `.gitignore` hinzugefügt unter Sektion "Setup/Bootstrap".

### Betroffene Dateien

- `.gitignore`: `setup.log` hinzugefügt

### Impact

- **Entwickler**: Sauberes Repository, keine Konflikte bei git pull
- **Schüler**: Keine Änderungen (setup.log funktioniert wie zuvor)
- **Breaking Changes**: Keine

### Referenzen

- Original-Planung: docs/planning/SETUP_LOG_GITIGNORE.md

---

## [2025-11-20] - Code-Qualität: bootstrap_env.py Refactoring

### Zusammenfassung

Verbesserung der Code-Qualität durch Type-Safety und Deduplication in `bootstrap_env.py`.

### Problem/Motivation

- Type-Checker warnungen: "Unresolved attribute reference for class 'None'"
- Redundanter Code für Fehlerbehandlung in mehreren Funktionen
- Unklare None-Checks bei subprocess-Ergebnissen

### Lösung/Implementierung

#### 1. Type-Safety Verbesserungen

- Explizite Type Hints: `subprocess.CompletedProcess[str] | None`
- Explizite None-Checks vor Attribut-Zugriff
- Behobene Warnungen für `stderr`, `stdout`, `returncode`

#### 2. Code-Deduplication durch Hilfsfunktionen

Neue Hilfsfunktionen:

- `extract_subprocess_error_details(exc)`: Extrahiert stdout/stderr aus CalledProcessError
- `get_error_message(exc)`: Gibt lesbare Fehlermeldung zurück
- `_extract_test_summary(stdout)`: Extrahiert Test-Zusammenfassung (privat)
- `_extract_test_failure_summary(stdout)`: Extrahiert Fehler-Details (privat)

#### 3. Verbesserte Lesbarkeit

- Threading-Code klarer strukturiert
- Konsistente Fehlerbehandlung
- Bessere Variablennamen

### Betroffene Dateien

- `tools/bootstrap_env.py`:
    - 4 neue Hilfsfunktionen
    - Alle Installations-Funktionen refactored
    - Type Hints ergänzt

### Impact

- **Entwickler**: Wartbarerer Code, keine Type-Checker-Warnungen
- **Schüler**: Keine Änderungen (funktional identisch)
- **Breaking Changes**: Keine

### Referenzen

- Original-Planung: docs/planning/REFACTORING_BOOTSTRAP_ENV.md

---

## [2025-11-19] - Infrastructure-Modul: config und logging_setup

### Zusammenfassung

Die Dateien `config.py` und `logging_setup.py` wurden in ein neues `infrastructure/` Modul verschoben.

### Problem/Motivation

Bessere Organisation zusammengehöriger Infrastruktur-Komponenten, die:

- Keine Simulationslogik enthalten
- Basisdienste für alle Module bereitstellen
- Framework-unabhängig sind
- Thread-sicher sind

### Lösung/Implementierung

#### Neue Struktur

```
src/core/simulation/infrastructure/
├── __init__.py          # Zentrale öffentliche API
├── config.py            # Konfigurationsverwaltung (verschoben)
└── logging_setup.py     # Logging-Setup (verschoben)
```

#### Import-Anpassungen

Alle Imports aktualisiert auf `from .infrastructure import ...`

### Betroffene Dateien

- **Verschoben**:
    - `src/core/simulation/config.py` → `src/core/simulation/infrastructure/config.py`
    - `src/core/simulation/logging_setup.py` → `src/core/simulation/infrastructure/logging_setup.py`
- **Imports aktualisiert**:
    - `src/core/simulation/__init__.py`
    - `src/core/simulation/ufosim.py`
    - `tests/test_logging_setup.py`
- **Neu erstellt**:
    - `src/core/simulation/infrastructure/__init__.py`

### Impact

- **Entwickler**: Imports ändern sich zu `from core.simulation.infrastructure import ...`
- **Schüler**: Keine Änderungen (öffentliche API bleibt stabil)
- **Breaking Changes**: Keine (Rückwärtskompatibilität über `__init__.py`)

### Referenzen

- Original-Planung: docs/planning/REFACTORING_INFRASTRUCTURE.md
- Architektur: docs/specs/architecture/core-simulation-zielbild.md

---

## [2025-11-19] - Dokumentations-Konsolidierung

### Zusammenfassung

Modul-Dokumentation wurde konsolidiert: `__init__.py` enthält umfassende Modul-Docs, einzelne Dateien nur noch
spezifische Docstrings.

### Problem/Motivation

- Redundante Dokumentation in mehreren Dateien
- Unklare "Single Source of Truth" für Architektur-Prinzipien
- README.md-Dateien innerhalb von Modulen duplizieren Information

### Lösung/Implementierung

#### Prinzipien der neuen Struktur

1. **Zentrale Modul-Dokumentation in `__init__.py`**:
    - Modulzweck und strukturelle Verantwortlichkeiten
    - Modul-Bestandteile und öffentliche API
    - Verwendungsbeispiele
    - Architektur-Prinzipien

2. **Spezifische Dokumentation in Einzeldateien**:
    - Kurzer Modul-Docstring (Ein-Zeiler)
    - Präzise Klassen-/Funktions-Docstrings
    - Keine Redundanz

#### Konsolidierte Module

- `exceptions/`: Exception-Hierarchie und Verwendungsbeispiele
- `infrastructure/`: Konfiguration und Logging-Setup

### Betroffene Dateien

- `src/core/simulation/exceptions/__init__.py`: Erweiterte Dokumentation
- `src/core/simulation/exceptions/simulation.py`: Gekürzte Docstrings
- `src/core/simulation/infrastructure/__init__.py`: Erweiterte Dokumentation
- `src/core/simulation/infrastructure/config.py`: Gekürzte Docstrings
- `src/core/simulation/infrastructure/logging_setup.py`: Gekürzte Docstrings

### Impact

- **Entwickler**: Klare "Single Source of Truth" für Modul-Architektur
- **Schüler**: Keine Änderungen (Code-Funktionalität unverändert)
- **Breaking Changes**: Keine

### Referenzen

- Original-Planung: docs/planning/REFACTORING_DOCUMENTATION.md

---

## [2025-11-18] - Refactoring T3: UfoState nach state/state.py

### Zusammenfassung

`UfoState` wurde aus `ufosim.py` in ein separates `state/` Modul extrahiert (Refactoring-Ticket T3).

### Problem/Motivation

Gemäß Architektur-Zielbild soll `UfoState` in einem separaten Modul liegen, um:

- Klare Trennung der Verantwortlichkeiten
- Wiederverwendbarkeit zu erhöhen
- Importhierarchie zu vereinfachen

### Lösung/Implementierung

#### Neue Package-Struktur

```
src/core/simulation/state/
├── __init__.py         # Export von UfoState
└── state.py            # UfoState Dataclass mit Properties
```

#### Architektur-Konformität

- ✅ `state.state` importiert nur `dataclasses`, `numpy`
- ✅ Keine Abhängigkeiten zu höherwertigen Modulen
- ✅ `@dataclass(slots=True, kw_only=True)` wie spezifiziert
- ✅ Alle 18 Felder und 3 Properties beibehalten
- ✅ Rückwärtskompatibilität gewährleistet

### Betroffene Dateien

- **Neu erstellt**:
    - `src/core/simulation/state/__init__.py`
    - `src/core/simulation/state/state.py`
    - `tests/test_state_import.py` (6 Smoke-Tests)
- **Geändert**:
    - `src/core/simulation/ufosim.py`: UfoState entfernt, Import hinzugefügt
    - `src/core/simulation/ufo_main.py`: Import aktualisiert
    - `src/core/simulation/__init__.py`: Import aus state-Paket

### Impact

- **Entwickler**: Import von `UfoState` nun aus `core.simulation.state`
- **Schüler**: Keine Änderungen (Rückwärtskompatibilität über `__init__.py`)
- **Breaking Changes**: Keine

### Tests

- 6 Smoke-Tests in `tests/test_state_import.py`, alle bestanden ✓
- Integration mit `UfoSim` getestet und funktionsfähig ✓

### Referenzen

- Ticket: T3 in docs/planning/refactoring-tracker.md
- Architektur: docs/specs/architecture/core-simulation-zielbild.md
- Import-Regeln: docs/specs/architecture/core-simulation-importregeln.md

---

## [2025-11-18] - Refactoring T1: Importhierarchie dokumentiert

### Zusammenfassung

Importhierarchie für `core.simulation` definiert und dokumentiert (Refactoring-Ticket T1).

### Problem/Motivation

Klare Regeln für Module-Imports notwendig, um:

- Zirkuläre Abhängigkeiten zu vermeiden
- Architektur zu erzwingen
- Neue Entwickler zu orientieren

### Lösung/Implementierung

Dokumentation der Importhierarchie in `docs/specs/architecture/core-simulation-importregeln.md`:

- **Ebene 0**: `exceptions`, `infrastructure`
- **Ebene 1**: `state`, `utils`, `physics`
- **Ebene 2**: `command`, `observer`
- **Ebene 3**: `controller`, `view`

#### Regeln

- Module dürfen nur von niedrigeren Ebenen importieren
- Innerhalb einer Ebene sind Imports verboten
- Zirkuläre Abhängigkeiten sind ausgeschlossen

### Betroffene Dateien

- **Neu erstellt**:
    - `docs/specs/architecture/core-simulation-importregeln.md`

### Impact

- **Entwickler**: Klare Regeln für Module-Organisation
- **Schüler**: Keine Änderungen
- **Breaking Changes**: Keine

### Referenzen

- Ticket: T1 in docs/planning/refactoring-tracker.md
- Branch: feature/refactor-phase1-importregeln

---

## [2025-11-18] - Refactoring T0: Zielbild dokumentiert

### Zusammenfassung

Architektur-Zielbild für `core.simulation` definiert und dokumentiert (Refactoring-Ticket T0).

### Problem/Motivation

Klares Zielbild notwendig für:

- Einheitliche Architektur-Vision
- Koordination zwischen Entwicklern
- Priorisierung von Refactoring-Tickets

### Lösung/Implementierung

Dokumentation des Zielbilds in `docs/specs/architecture/core-simulation-zielbild.md`:

- Package-Struktur mit allen Modulen
- Verantwortlichkeiten jedes Moduls
- Öffentliche API-Definitionen
- Design-Prinzipien

### Betroffene Dateien

- **Neu erstellt**:
    - `docs/specs/architecture/core-simulation-zielbild.md`

### Impact

- **Entwickler**: Klare Architektur-Vision für Refactoring
- **Schüler**: Keine Änderungen
- **Breaking Changes**: Keine

### Referenzen

- Ticket: T0 in docs/planning/refactoring-tracker.md
- Branch: feature/refactor-phase0-zielbild

---

## Template für neue Einträge

```markdown
## [YYYY-MM-DD] - Kurztitel

### Zusammenfassung

...

### Problem/Motivation

...

### Lösung/Implementierung

...

### Betroffene Dateien

- `pfad/zu/datei.py`: ...

### Impact

- **Entwickler**: ...
- **Schüler**: ...
- **Breaking Changes**: ...

### Referenzen

- ...
```

