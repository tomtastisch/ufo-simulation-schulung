# Architektur-Zielbild: core.simulation

**Letzte Aktualisierung:** 2025-11-18  
**Status:** Referenzdokument für Refactoring-Phase (Tickets T0–T17)  
**Gültigkeit:** Verbindliche Zielvorgabe, keine Diskussionsgrundlage

---

## 1. Zweck und Geltungsbereich

Dieses Dokument definiert die **Zielarchitektur** des Pakets `src/core/simulation/` nach Abschluss aller Refactoring-Phasen (T1–T17). Es dient als:

- **Verbindliche Referenz** für alle Entwickler und Reviewer während des Refactorings
- **Architektonisches Leitbild** für die Trennung von Verantwortlichkeiten
- **API-Spezifikation** für externe Nutzer des Simulationspakets
- **Qualitätskriterium** zur Bewertung der Implementierung

Die hier beschriebene Struktur gilt als **finaler Endzustand**. Alle Tickets T1–T17 arbeiten schrittweise auf diesen Zustand hin. Abweichungen von diesem Zielbild sind nur nach expliziter Freigabe durch den Lead Developer zulässig.

---

## 2. Paketstruktur – Überblick

Das Paket `src/core/simulation/` wird in **8 Teilpakete** gegliedert, ergänzt durch **3 zentrale Module** auf oberster Ebene:

```
src/core/simulation/
├── __init__.py              # Öffentliche API-Definition (exports)
├── config.py                # Konfiguration (SimulationConfig, DEFAULT_CONFIG)
├── exceptions.py            # Projekt-spezifische Exceptions
├── logging_setup.py         # Logging-Konfiguration
│
├── utils/                   # Wiederverwendbare Utilities (framework-unabhängig)
│   ├── __init__.py
│   ├── threads.py           # Threading-Utilities (@synchronized)
│   └── maths.py             # Numerische Hilfsfunktionen
│
├── state/                   # Zustandsverwaltung
│   ├── __init__.py
│   ├── state.py             # UfoState (Datenmodell)
│   └── manager.py           # StateManager (Thread-sichere Zustandsverwaltung)
│
├── physics/                 # Physik-Engine
│   ├── __init__.py
│   ├── engine.py            # PhysicsEngine (Integrator, Physik-Logik)
│   └── integrators.py       # Numerische Integratoren (optional, zukünftig)
│
├── command/                 # Command-System (deklarative Steuerung)
│   ├── __init__.py
│   ├── types.py             # CommandType (Enum), Command (Dataclass)
│   ├── queue.py             # CommandQueue
│   └── executor.py          # CommandExecutor
│
├── observer/                # Observer-Pattern & Analyse
│   ├── __init__.py
│   ├── observer.py          # Phase, compute_phase, StateObserver
│   └── metrics.py           # ManeuverAnalysis (optional erweitert)
│
├── controller/              # Orchestrierung (Simulation-Hauptschleife)
│   ├── __init__.py
│   ├── sim.py               # UfoSim (Hauptklasse)
│   └── lifecycle.py         # Lifecycle-Management (optional, zukünftig)
│
└── view/                    # GUI-Layer (PyQt5)
    ├── __init__.py
    ├── viewport.py          # UfoViewport (Viewport-Logik)
    ├── viewmodel.py         # SimulationViewModel (View-Daten)
    ├── pview.py             # UfoPView (PyQt5-View)
    ├── hud.py               # HUD-Hilfsfunktionen
    └── resources/           # Statische Ressourcen (optional)
```

---

## 3. Teilpakete – Verantwortlichkeiten

### 3.1 `config.py`

**Zweck:**  
Zentrale Konfiguration der Simulation. Alle Parameter, die das Verhalten der Simulation steuern, werden hier definiert.

**Inhalt:**
- `SimulationConfig` (Dataclass mit allen Simulationsparametern)
- `DEFAULT_CONFIG` (Standard-Konfigurationsobjekt)

**Abhängigkeiten:**
- Nur Standardbibliothek und `dataclasses`
- **Keine** Abhängigkeit zu anderen Simulationspaketen

**Öffentlich:**
- ✅ `SimulationConfig`
- ✅ `DEFAULT_CONFIG`

---

### 3.2 `exceptions.py`

**Zweck:**  
Definition projekt-spezifischer Fehlerklassen.

**Inhalt:**
- `SimulationError` (Basis-Exception)
- `ConfigError` (Konfigurationsfehler)
- Optional: `StateValidationError`, `PhysicsError` etc.

**Abhängigkeiten:**
- Nur Standardbibliothek (`Exception`)

**Öffentlich:**
- ⚠️ Intern verwendbar, aber nicht Teil der offiziellen API
- Externe Nutzer können generische `Exception` verwenden

---

### 3.3 `logging_setup.py`

**Zweck:**  
Zentrale Konfiguration des Logging-Systems.

**Inhalt:**
- `configure_logging()` – Einmalige Konfiguration beim Import
- `get_logger(name: str) -> logging.Logger` – Logger-Factory

**Abhängigkeiten:**
- Nur `logging` aus Standardbibliothek

**Öffentlich:**
- ⚠️ Intern verwendet
- Externe Nutzer konfigurieren ihr eigenes Logging

---

### 3.4 `utils/` – Wiederverwendbare Utilities

**Zweck:**  
Sammlung von reinen, wiederverwendbaren Hilfsfunktionen ohne Domänenlogik.

#### 3.4.1 `utils/threads.py`

**Inhalt:**
- `@synchronized` – Decorator für Thread-sichere Methoden
- Voraussetzung: Klasse besitzt `_lock`-Attribut (`threading.RLock`)

**Abhängigkeiten:**
- Nur `threading`, `functools`, `typing`

**Öffentlich:**
- ⚠️ Intern verwendet (z.B. in `StateManager`, `CommandExecutor`)

#### 3.4.2 `utils/maths.py`

**Inhalt:**
- `deg_to_rad(deg: float) -> float`
- `wrap_angle_deg(angle: float) -> float`
- `clamp(value: float, min_val: float, max_val: float) -> float`
- Weitere numerische Hilfsfunktionen

**Abhängigkeiten:**
- `math`, `numpy` (optional)
- **Keine** Abhängigkeit zu Simulationsobjekten

**Öffentlich:**
- ⚠️ Intern verwendet

---

### 3.5 `state/` – Zustandsverwaltung

#### 3.5.1 `state/state.py`

**Zweck:**  
Datenmodell für den Simulationszustand.

**Inhalt:**
- `UfoState` (Dataclass)
  - Attribute: `x`, `y`, `z`, `vx`, `vy`, `vz`, `d`, `i`, `v`, `thrust`, `tilt_angle`, `is_landed`, `crashed`
  - Properties: `position_vector`, `velocity_vector`, `acceleration_vector`

**Abhängigkeiten:**
- `dataclasses`, `numpy`, `typing`
- **Keine** Abhängigkeit zu `StateManager`, `PhysicsEngine`, `UfoSim`

**Öffentlich:**
- ✅ `UfoState`

#### 3.5.2 `state/manager.py`

**Zweck:**  
Thread-sichere Verwaltung und Synchronisation des Simulationszustands.

**Inhalt:**
- `StateManager`
  - `get_state()` – Thread-sicherer Zugriff auf aktuellen Zustand (Snapshot)
  - `update_state(updater: Callable[[UfoState], UfoState])` – Atomare State-Änderung
  - `reset()` – Zustand zurücksetzen
  - `register_observer()`, `unregister_observer()` – Observer-Pattern
  - `wait_for_condition(condition: Callable, timeout: float)` – Warten auf Bedingung

**Abhängigkeiten:**
- `UfoState` (aus `state.state`)
- `@synchronized` (aus `utils.threads`)
- `threading`, `dataclasses.replace`

**Öffentlich:**
- ⚠️ Intern verwendet durch `UfoSim`
- Externe Nutzer greifen über `UfoSim.get_state_snapshot()` zu

---

### 3.6 `physics/` – Physik-Engine

#### 3.6.1 `physics/engine.py`

**Zweck:**  
Physikalische Simulation und Integration des Zustands.

**Inhalt:**
- `PhysicsEngine`
  - `integrate_step(state: UfoState) -> tuple[bool, bool]`
    - Berechnet neuen Zustand basierend auf physikalischen Gesetzen
    - Rückgabe: `(is_landed, crashed)`
  - Interne Methoden:
    - `_apply_landing_assistance()`
    - `_update_velocity()`
    - `_update_direction()`
    - `_update_inclination()`
    - `_update_position()`
    - `_handle_landing()`

**Abhängigkeiten:**
- `SimulationConfig` (aus `config`)
- `UfoState` (aus `state.state`)
- `numpy`, `math`, `logging`

**Öffentlich:**
- ⚠️ Intern verwendet durch `UfoSim`

#### 3.6.2 `physics/integrators.py`

**Zweck:**  
Numerische Integratoren (zukünftige Erweiterung).

**Inhalt:**
- Verschiedene Integrations-Algorithmen (Euler, Runge-Kutta, etc.)

**Status:**
- ⚠️ Optional, aktuell nicht implementiert
- Reserviert für zukünftige Erweiterungen

---

### 3.7 `command/` – Command-System

#### 3.7.1 `command/types.py`

**Zweck:**  
Definition von Command-Typen.

**Inhalt:**
- `CommandType` (Enum):
  - `SET_STATE`, `LOG_MESSAGE`, `EXECUTE_FUNC`, `WAIT_CONDITION`
- `Command` (Dataclass)
  - Felder: `type`, `data`, `func`, `condition`, `timeout`

**Abhängigkeiten:**
- `enum`, `dataclasses`, `typing`
- `UfoState` nur via `TYPE_CHECKING` (keine Laufzeit-Abhängigkeit)

**Öffentlich:**
- ⚠️ Intern verwendet
- Externe Nutzer nutzen `UfoSim.create_command_queue()` API

#### 3.7.2 `command/queue.py`

**Zweck:**  
Verwaltung einer Befehlssequenz.

**Inhalt:**
- `CommandQueue`
  - `set_state(updater: Callable)` – State-Änderung einfügen
  - `wait_until(condition: Callable, timeout: float)` – Warten auf Bedingung
  - `execute(func: Callable)` – Funktion ausführen
  - `log(message: str)` – Log-Nachricht einfügen
  - `wait_for_completion()` – Blockierend bis Queue abgearbeitet
  - Interne Verwaltung: `_commands`, `_completed_index`, `_completion_event`

**Abhängigkeiten:**
- `Command`, `CommandType` (aus `command.types`)
- `threading`, `typing`

**Öffentlich:**
- ✅ Indirekt via `UfoSim.create_command_queue()`

#### 3.7.3 `command/executor.py`

**Zweck:**  
Ausführung von Command-Queues gegen den Simulationszustand.

**Inhalt:**
- `CommandExecutor`
  - `process_commands(queue: CommandQueue, current_state: UfoState)`
    - Arbeitet Commands sequentiell ab
    - Nutzt `StateManager.update_state()` für `SET_STATE`
    - Evaluiert Bedingungen für `WAIT_CONDITION`

**Abhängigkeiten:**
- `StateManager` (aus `state.manager`)
- `CommandQueue`, `CommandType` (aus `command`)
- `@synchronized` (aus `utils.threads`)

**Öffentlich:**
- ⚠️ Intern verwendet durch `UfoSim`

---

### 3.8 `observer/` – Observer & Analyse

#### 3.8.1 `observer/observer.py`

**Zweck:**  
Phasenmodell und Manöver-Analyse.

**Inhalt:**
- `Phase` (Literal/Enum):
  - `"idle"`, `"takeoff"`, `"flying"`, `"landing"`, `"landed"`, `"crashed"`
- `compute_phase(state: UfoState, config: SimulationConfig) -> Phase`
  - Ermittelt aktuelle Phase aus Zustand
  - Prioritätsbasierte Regeln
- `StateObserver`
  - Sammelt Zustandsverlauf (History)
  - Analysiert Trends (Steigen, Sinken, Stagnation)
  - Methode: `analyze(state: UfoState) -> None`
- `ManeuverAnalysis` (Dataclass)
  - Felder: `is_ascending`, `is_descending`, `is_turning`, `heading_change`, `is_stagnant`, etc.

**Abhängigkeiten:**
- `SimulationConfig` (aus `config`)
- `UfoState` (aus `state.state`)
- `numpy`, `collections.deque`, `dataclasses`

**Öffentlich:**
- ✅ `Phase`
- ✅ `ManeuverAnalysis`
- ⚠️ `compute_phase` und `StateObserver` intern verwendet

#### 3.8.2 `observer/metrics.py`

**Zweck:**  
Erweiterte Metriken (optional, zukünftig).

**Status:**
- ⚠️ Reserviert für zukünftige Erweiterungen

---

### 3.9 `controller/` – Orchestrierung

#### 3.9.1 `controller/sim.py`

**Zweck:**  
Haupt-Orchestrator der Simulation. Zentrale Klasse für externe Nutzer.

**Inhalt:**
- `UfoSim`
  - **Öffentliche API:**
    - `__init__(config: SimulationConfig = DEFAULT_CONFIG)`
    - `start(destinations: List[Tuple], autopilot_callback: Optional[Callable], speedup: int, show_view: bool)`
    - `get_state_snapshot() -> UfoState`
    - `get_phase() -> Phase`
    - `get_maneuver_analysis() -> ManeuverAnalysis`
    - `get_maneuver_description() -> str`
    - `create_command_queue() -> CommandQueue`
    - `execute_command_queue(queue: CommandQueue)`
    - `wait_for_condition(condition: Callable, timeout: float) -> bool`
    - `format_flight_data() -> str`
    - `reset()`
    - `terminate()`
  
  - **Interne Komponenten:**
    - `self._state_manager: StateManager`
    - `self._physics_engine: PhysicsEngine`
    - `self._command_executor: CommandExecutor`
    - `self.observer: StateObserver`
    - `self._sim_thread: threading.Thread`
    - `self._autopilot_thread: threading.Thread` (optional)
    - `self._view: UfoPView` (optional, lazy import)

  - **Interne Methoden:**
    - `__run_sim()` – Hauptschleife (Physics + Command-Execution)
    - `__run_autopilot()` – Autopilot-Thread
    - `__initialize_view()` – GUI-Initialisierung (lazy)

**Abhängigkeiten:**
- Alle Pakete (orchestriert):
  - `config`, `state`, `physics`, `command`, `observer`
  - `view` (lazy import, nur bei GUI)

**Öffentlich:**
- ✅ `UfoSim` (zentrale API-Klasse)

#### 3.9.2 `controller/lifecycle.py`

**Zweck:**  
Lifecycle-Management (Starten, Pausieren, Stoppen) – optional.

**Status:**
- ⚠️ Reserviert für zukünftige Erweiterungen

---

### 3.10 `view/` – GUI-Layer

#### 3.10.1 `view/viewport.py`

**Zweck:**  
Viewport-Koordinatentransformation.

**Inhalt:**
- `UfoViewport`
  - `configure_for_points(points: List[Tuple])`
  - `to_screen(x: float, y: float) -> Tuple[float, float]`

**Abhängigkeiten:**
- Nur `numpy`, `typing`

**Öffentlich:**
- ⚠️ Intern verwendet durch `UfoPView`

#### 3.10.2 `view/viewmodel.py`

**Zweck:**  
View-Daten für GUI-Darstellung.

**Inhalt:**
- `SimulationViewModel`
  - `from_simulation(sim: UfoSim) -> SimulationViewModel`
  - Kapselt Zugriff auf `UfoSim` für View

**Abhängigkeiten:**
- `UfoSim` (aus `controller.sim`)

**Öffentlich:**
- ⚠️ Intern verwendet durch `UfoPView`

#### 3.10.3 `view/pview.py`

**Zweck:**  
PyQt5-basierte Visualisierung.

**Inhalt:**
- `UfoPView(QMainWindow)`
  - `__init__(sim: UfoSim, viewport: UfoViewport)`
  - `update_display()`
  - `show_crash_screen()`

**Abhängigkeiten:**
- `PyQt5` (externe Bibliothek)
- `SimulationViewModel`, `UfoViewport`
- `HUD`-Hilfsfunktionen

**Öffentlich:**
- ⚠️ Intern verwendet durch `UfoSim.start(show_view=True)`

#### 3.10.4 `view/hud.py`

**Zweck:**  
HUD-Hilfsfunktionen für PyQt5.

**Inhalt:**
- `create_circle_item(...) -> QGraphicsEllipseItem`
- `create_text_item(...) -> QGraphicsTextItem`

**Abhängigkeiten:**
- `PyQt5`

**Öffentlich:**
- ⚠️ Intern verwendet

#### 3.10.5 `view/resources/`

**Zweck:**  
Statische Ressourcen (Icons, Bilder, etc.) – optional.

**Status:**
- ⚠️ Reserviert für zukünftige Erweiterungen

---

## 4. Öffentliche API

Die **einzige öffentlich dokumentierte und garantierte Schnittstelle** für externe Nutzer besteht aus:

### 4.1 Exportierte Symbole (`src/core/simulation/__init__.py`)

```python
from .config import SimulationConfig, DEFAULT_CONFIG
from .state.state import UfoState
from .controller.sim import UfoSim
from .observer.observer import ManeuverAnalysis, Phase

__all__ = [
    "SimulationConfig",
    "DEFAULT_CONFIG",
    "UfoState",
    "UfoSim",
    "ManeuverAnalysis",
    "Phase",
]
```

### 4.2 Nutzung durch externe Module

**Erlaubter Import:**
```python
from core.simulation import UfoSim, SimulationConfig, UfoState, Phase, ManeuverAnalysis
```

**Verbotener direkter Import (interne Details):**
```python
# ❌ Nicht erlaubt:
from core.simulation.physics.engine import PhysicsEngine
from core.simulation.state.manager import StateManager
from core.simulation.command.executor import CommandExecutor
```

### 4.3 Typische Nutzungsszenarien

#### Szenario 1: Einfacher Simulationslauf

```python
from core.simulation import UfoSim

sim = UfoSim()
sim.start(
    destinations=[(0, 0, 0), (100, 100, 50), (200, 0, 0)],
    autopilot_callback=my_autopilot_function,
    speedup=1,
    show_view=True
)
```

#### Szenario 2: Zustandsabfrage

```python
state = sim.get_state_snapshot()
print(f"Position: {state.x}, {state.y}, {state.z}")

phase = sim.get_phase()
print(f"Phase: {phase}")

analysis = sim.get_maneuver_analysis()
print(f"Ascending: {analysis.is_ascending}")
```

#### Szenario 3: Command-Queue

```python
queue = sim.create_command_queue()
queue.set_state(lambda s: dataclasses.replace(s, thrust=50))
queue.wait_until(lambda s: s.z > 100, timeout=10)
queue.log("Reached altitude")
sim.execute_command_queue(queue)
queue.wait_for_completion()
```

---

## 5. Import-Hierarchie und Abhängigkeiten

### 5.1 Erlaubte Import-Richtungen

Die folgende Hierarchie **muss** eingehalten werden, um zyklische Abhängigkeiten zu vermeiden:

```
view → controller (+ observer-Typen: Phase)
controller → physics, state, command, observer, config
observer → state.state, config
physics → state.state, config
command → state (nur TYPE_CHECKING), config
state.manager → state.state, utils.threads
utils → [nur Standardlib, numpy]
config → [nur Standardlib, dataclasses]
```

### 5.2 Verbotene Import-Richtungen

Folgende Importe sind **explizit verboten**:

```
❌ physics → state.manager
❌ physics → controller
❌ physics → view
❌ observer → controller
❌ observer → view
❌ view → physics
❌ view → state.manager
❌ command → controller
❌ command → view
❌ command → observer (außer TYPE_CHECKING)
❌ utils → [jegliche Simulationselemente]
```

### 5.3 Zyklusvermeidung

- **TYPE_CHECKING-Imports:** Für reine Typ-Annotationen darf `typing.TYPE_CHECKING` genutzt werden, um Laufzeit-Zyklen zu vermeiden.
- **Lazy Imports:** GUI-Module (`view`) werden in `controller.sim` nur bei Bedarf geladen (`if show_view: from ..view.pview import UfoPView`).

---

## 6. Trennung: Intern vs. Öffentlich

### 6.1 Öffentlich (Garantiert stabil)

Folgende Komponenten sind **öffentlich dokumentiert** und dürfen von externen Modulen genutzt werden:

| Komponente          | Modul                  | Beschreibung                          |
|---------------------|------------------------|---------------------------------------|
| `SimulationConfig`  | `config`               | Konfigurationsobjekt                  |
| `DEFAULT_CONFIG`    | `config`               | Standard-Konfiguration                |
| `UfoState`          | `state.state`          | Zustandsdatenmodell                   |
| `UfoSim`            | `controller.sim`       | Haupt-API-Klasse                      |
| `Phase`             | `observer.observer`    | Phasen-Enum/Literal                   |
| `ManeuverAnalysis`  | `observer.observer`    | Manöver-Analyseergebnis               |

### 6.2 Intern (Implementierungsdetail)

Alle anderen Module und Klassen sind **interne Implementierungsdetails** und können sich ohne Vorwarnung ändern:

- `StateManager`, `PhysicsEngine`, `CommandQueue`, `CommandExecutor`
- `StateObserver`, `compute_phase`
- Alle `view`-Module (`UfoPView`, `UfoViewport`, etc.)
- Alle `utils`-Module (`@synchronized`, `maths`)
- `exceptions`, `logging_setup`

---

## 7. Threading-Modell

### 7.1 Thread-Übersicht

Die Simulation nutzt **bis zu 3 Threads**:

1. **Haupt-Thread (Main)**
   - Initialisierung
   - GUI-Eventloop (falls `show_view=True`)

2. **Simulations-Thread (`_sim_thread`)**
   - `UfoSim.__run_sim()`
   - Physik-Integration (`PhysicsEngine.integrate_step`)
   - Command-Execution (`CommandExecutor.process_commands`)
   - Observer-Benachrichtigungen

3. **Autopilot-Thread (`_autopilot_thread`)**
   - `UfoSim.__run_autopilot()`
   - Ruft `autopilot_callback` periodisch auf

### 7.2 Synchronisation

- **StateManager:** Thread-sicherer Zugriff via `threading.RLock` und `@synchronized`
- **CommandQueue:** Thread-sichere Command-Verwaltung via `threading.Event`
- **Observer-Benachrichtigungen:** Callbacks erhalten Snapshots (Kopien), keine direkten Referenzen

### 7.3 Headless vs. GUI

- **Headless-Modus (`show_view=False`):**
  - Kein GUI-Import
  - Nur Sim-Thread + Autopilot-Thread
  
- **GUI-Modus (`show_view=True`):**
  - Lazy Import von `view.pview`
  - GUI läuft im Haupt-Thread (PyQt5-Anforderung)
  - Sim-Thread kommuniziert via Thread-sicheren ViewModel

---

## 8. Abhängigkeiten zu externen Bibliotheken

### 8.1 Erforderliche Abhängigkeiten

| Bibliothek | Version  | Verwendung                                    |
|------------|----------|-----------------------------------------------|
| `numpy`    | ≥1.24    | Vektorrechnung, numerische Operationen        |
| `PyQt5`    | ≥5.15    | GUI-Darstellung (optional, nur bei show_view) |

### 8.2 Optionale Abhängigkeiten

- Keine geplant

### 8.3 Standardbibliothek

Folgende Module aus der Python-Standardbibliothek werden verwendet:

- `dataclasses`, `typing`, `enum`
- `threading`, `collections`, `logging`
- `math`, `sys`, `os`

---

## 9. Offene Punkte und Annahmen

### 9.1 Offene Punkte

Folgende Aspekte sind im aktuellen Zielbild noch nicht final geklärt:

1. **`physics/integrators.py`:**
   - Aktuell nur Platzhalter für zukünftige numerische Integratoren
   - Umsetzung in späteren Phasen (nach T17)

2. **`controller/lifecycle.py`:**
   - Geplant für Pause/Resume-Funktionalität
   - Nicht in initialen Tickets T1–T17 enthalten

3. **`observer/metrics.py`:**
   - Reserviert für erweiterte Metriken (z.B. Energieverbrauch, Effizienz)
   - Implementierung nach T17

4. **`view/resources/`:**
   - Struktur für statische Ressourcen (Icons, Bilder)
   - Aktuell nicht benötigt, aber für zukünftige Erweiterungen reserviert

### 9.2 Konservative Annahmen

Folgende Annahmen wurden getroffen, wo Vorgaben nicht eindeutig waren:

1. **Logging:**
   - Logging-Konfiguration erfolgt zentral in `logging_setup.py`
   - Externe Nutzer können eigenes Logging konfigurieren (keine Interferenz)

2. **Exception-Handling:**
   - Simulationsfehler werden via `SimulationError` geworfen
   - Externe Nutzer können generische `Exception` fangen, wenn sie `SimulationError` nicht kennen

3. **Command-Queue Thread-Safety:**
   - Command-Queues sind Thread-sicher
   - Mehrere Threads können gleichzeitig Queues erstellen und abarbeiten

4. **GUI-Import:**
   - PyQt5 wird **lazy** importiert (nur bei `show_view=True`)
   - Headless-Betrieb funktioniert ohne PyQt5-Installation (Import-Error wird abgefangen)

---

## 10. Bezug zu Refactoring-Phasen

Dieses Dokument dient als **Referenz für alle Tickets T1–T17**. Die Phasen aus `docs/specs/notes/introductions.md` bauen schrittweise auf dieses Zielbild hin:

| Phase   | Tickets | Fokus                                        |
|---------|---------|----------------------------------------------|
| Phase 0 | T0      | Zielbild dokumentieren (dieses Dokument)     |
| Phase 1 | T1      | Import-Hierarchie definieren                 |
| Phase 2 | T2–T4   | Basis (config, state, logging)               |
| Phase 3 | T5–T7   | Utilities & Physik                           |
| Phase 4 | T8–T9   | StateManager & Observer                      |
| Phase 5 | T10–T12 | Command-System                               |
| Phase 6 | T13     | Controller (UfoSim)                          |
| Phase 7 | T14     | View-Layer                                   |
| Phase 8 | T15     | Autopilot-Integration                        |
| Phase 9 | T16–T17 | Tests, Linting, API-Gateway                  |

**Wichtig:**  
Jedes Ticket muss sicherstellen, dass die hier definierten **Abhängigkeitsregeln** (Abschnitt 5) und **API-Definitionen** (Abschnitt 4) eingehalten werden.

---

## 11. Qualitätskriterien

Nach Abschluss aller Phasen (T1–T17) müssen folgende Kriterien erfüllt sein:

### 11.1 Architektur

- ✅ Alle 8 Teilpakete existieren mit definierter Struktur
- ✅ Import-Hierarchie ist zyklenfrei
- ✅ Öffentliche API ist stabil und dokumentiert
- ✅ Interne Module sind klar abgegrenzt

### 11.2 Tests

- ✅ Unit-Tests für jedes Modul (State, Physics, Observer, Command, Controller)
- ✅ Integrationstests für vollständige Simulationsläufe
- ✅ Threading-Tests (keine Race-Conditions, Deadlocks)
- ✅ Headless-Tests (ohne PyQt5)

### 11.3 Code-Qualität

- ✅ `mypy` ohne Fehler (Type-Safety)
- ✅ `flake8` ohne kritische Verstöße (PEP-8)
- ✅ Docstrings für alle öffentlichen Klassen/Funktionen
- ✅ Keine hartkodierten Magic Numbers (außer physikalischen Konstanten)

### 11.4 Kompatibilität

- ✅ Bestehende Autopilot-Beispiele funktionieren unverändert
- ✅ Schulungsaufgaben (task/autopilot) sind kompatibel
- ✅ GUI und Headless-Modus funktionieren beide

---

## 12. Änderungshistorie

| Datum      | Version | Änderung                              | Autor    |
|------------|---------|---------------------------------------|----------|
| 2025-11-18 | 1.0     | Initiale Erstellung (Ticket T0)       | Copilot  |

---

## 13. Freigabe

Dieses Dokument wurde erstellt im Rahmen von **Ticket T0** und dient als **verbindliche Referenz** für alle weiteren Refactoring-Tickets.

**Status:** ✅ Freigegeben für T1–T17  
**Reviewer:** Ausstehend (Tech Reviewer erforderlich)  
**Gültig bis:** Abschluss Phase 9 (T17)

---

**Ende des Dokuments**
