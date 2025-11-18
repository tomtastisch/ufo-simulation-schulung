# Import-Hierarchie und Architektur-Regeln: core.simulation

**Letzte Aktualisierung:** 2025-11-18  
**Status:** Verbindliche Regelbasis für Refactoring-Phasen T2–T17  
**Gültigkeit:** Bindend für alle Entwickler und Code-Reviews

---

## 1. Zweck und Zielsetzung

Dieses Dokument definiert die **verbindliche Import-Hierarchie** für das Paket `src/core/simulation/`. Es dient als:

- **Regelwerk zur Vermeidung zyklischer Abhängigkeiten** (Import-Zyklen)
- **Clean-Architecture-Leitfaden** mit klaren Schichtgrenzen
- **Review-Referenz** zur Prüfung von Code-Änderungen
- **Entwicklungs-Richtlinie** für neue Module und Features

### 1.1 Architektonische Ziele

Die Import-Hierarchie verfolgt folgende Kernziele:

1. **Zyklenfreiheit:** Keine zirkulären Abhängigkeiten zwischen Paketen
2. **Klare Schichten:** Jedes Paket hat eine eindeutige Position in der Hierarchie
3. **Unidirektionale Abhängigkeiten:** Importe erfolgen nur in eine Richtung (von oben nach unten)
4. **Testbarkeit:** Untere Schichten sind isoliert testbar ohne obere Schichten
5. **Austauschbarkeit:** Obere Schichten (z.B. GUI) können ersetzt werden, ohne untere Schichten zu ändern

### 1.2 Clean Architecture Prinzipien

Das Design folgt den Clean-Architecture-Prinzipien:

- **Dependency Rule:** Abhängigkeiten zeigen nur nach innen (zu stabileren Schichten)
- **Abstraktion über Konkretisierung:** Interne Schichten kennen keine UI/Framework-Details
- **Single Responsibility:** Jedes Paket hat genau eine fachliche Verantwortung
- **Separation of Concerns:** Klare Trennung zwischen Domänenlogik, Infrastruktur und Präsentation

---

## 2. Paket-Übersicht und Verantwortlichkeiten

Das `core.simulation` Paket besteht aus **8 Teilpaketen** mit klar definierten Verantwortlichkeiten:

### 2.1 `config` – Konfiguration

**Verantwortung:**  
Zentrale Konfiguration aller Simulationsparameter.

**Inhalt:**
- `SimulationConfig` (Dataclass)
- `DEFAULT_CONFIG` (Standardwerte)

**Position in Hierarchie:** **Fundament** (niedrigste Schicht)

**Darf importieren:**
- ✅ Standardbibliothek (`dataclasses`, `typing`)

**Darf NICHT importieren:**
- ❌ Alle anderen Simulationspakete

---

### 2.2 `utils` – Wiederverwendbare Utilities

**Verantwortung:**  
Framework-unabhängige Hilfsfunktionen ohne Domänenlogik.

**Inhalt:**
- `threads.py`: `@synchronized` Decorator
- `maths.py`: Numerische Hilfsfunktionen

**Position in Hierarchie:** **Fundament** (niedrigste Schicht)

**Darf importieren:**
- ✅ Standardbibliothek (`threading`, `math`, `functools`)
- ✅ Numerische Bibliotheken (`numpy`)

**Darf NICHT importieren:**
- ❌ Alle Simulationspakete (state, physics, controller, etc.)
- ❌ `SimulationConfig` oder `UfoState`

**Begründung:**  
Utils sind generisch wiederverwendbar und dürfen keine Domänenabhängigkeiten haben.

---

### 2.3 `state` – Zustandsverwaltung

**Verantwortung:**  
Datenmodell und Thread-sichere Verwaltung des Simulationszustands.

**Inhalt:**
- `state/state.py`: `UfoState` (Datenmodell)
- `state/manager.py`: `StateManager` (Thread-sichere Zustandsverwaltung)

**Position in Hierarchie:** **Domänenschicht** (mittlere Ebene)

#### 2.3.1 `state.state` (UfoState)

**Darf importieren:**
- ✅ `dataclasses`, `numpy`, `typing`

**Darf NICHT importieren:**
- ❌ `StateManager`
- ❌ `PhysicsEngine`, `UfoSim`, `CommandQueue`
- ❌ Alle view/controller-Pakete

#### 2.3.2 `state.manager` (StateManager)

**Darf importieren:**
- ✅ `UfoState` (aus `state.state`)
- ✅ `@synchronized` (aus `utils.threads`)
- ✅ `threading`, `dataclasses.replace`

**Darf NICHT importieren:**
- ❌ `PhysicsEngine`
- ❌ `CommandExecutor`
- ❌ `UfoSim`
- ❌ view/controller-Pakete

---

### 2.4 `physics` – Physik-Engine

**Verantwortung:**  
Physikalische Simulation und numerische Integration.

**Inhalt:**
- `physics/engine.py`: `PhysicsEngine`
- `physics/integrators.py`: Numerische Integratoren (zukünftig)

**Position in Hierarchie:** **Domänenschicht** (mittlere Ebene)

**Darf importieren:**
- ✅ `SimulationConfig` (aus `config`)
- ✅ `UfoState` (aus `state.state`)
- ✅ Numerische Bibliotheken (`numpy`, `math`)
- ✅ `logging`

**Darf NICHT importieren:**
- ❌ `StateManager` (aus `state.manager`)
- ❌ `CommandQueue`, `CommandExecutor`
- ❌ `UfoSim` (aus `controller`)
- ❌ Alle view-Pakete
- ❌ `observer`-Pakete

**Begründung:**  
Physics ist reine Domänenlogik und darf keine Orchestrierungs- oder UI-Komponenten kennen.

---

### 2.5 `command` – Command-System

**Verantwortung:**  
Deklarative Steuerung via Command-Pattern.

**Inhalt:**
- `command/types.py`: `CommandType`, `Command`
- `command/queue.py`: `CommandQueue`
- `command/executor.py`: `CommandExecutor`

**Position in Hierarchie:** **Domänenschicht** (mittlere Ebene)

#### 2.5.1 `command.types`

**Darf importieren:**
- ✅ `enum`, `dataclasses`, `typing`
- ✅ `UfoState` **nur via TYPE_CHECKING** (keine Laufzeit-Abhängigkeit)

**Darf NICHT importieren:**
- ❌ `StateManager`, `PhysicsEngine`, `UfoSim`
- ❌ view/controller/observer-Pakete

#### 2.5.2 `command.queue`

**Darf importieren:**
- ✅ `Command`, `CommandType` (aus `command.types`)
- ✅ `threading`
- ✅ `UfoState` **nur via TYPE_CHECKING**

**Darf NICHT importieren:**
- ❌ `StateManager`, `CommandExecutor`
- ❌ Alle anderen Simulationspakete

#### 2.5.3 `command.executor`

**Darf importieren:**
- ✅ `StateManager` (aus `state.manager`)
- ✅ `CommandQueue`, `CommandType` (aus `command`)
- ✅ `@synchronized` (aus `utils.threads`)
- ✅ `logging`

**Darf NICHT importieren:**
- ❌ `PhysicsEngine`
- ❌ `UfoSim`
- ❌ `observer`-Pakete (außer TYPE_CHECKING bei Bedarf)
- ❌ view/controller-Pakete

**Begründung:**  
CommandExecutor orchestriert State-Änderungen, aber kennt keine Physik, Observer oder UI.

---

### 2.6 `observer` – Observer-Pattern & Analyse

**Verantwortung:**  
Phasenmodell, Manöver-Analyse und State-Beobachtung.

**Inhalt:**
- `observer/observer.py`: `Phase`, `compute_phase`, `StateObserver`, `ManeuverAnalysis`
- `observer/metrics.py`: Erweiterte Metriken (zukünftig)

**Position in Hierarchie:** **Anwendungsschicht** (obere Domäne)

**Darf importieren:**
- ✅ `SimulationConfig` (aus `config`)
- ✅ `UfoState` (aus `state.state`)
- ✅ `numpy`, `collections.deque`, `dataclasses`, `logging`

**Darf NICHT importieren:**
- ❌ `StateManager` (aus `state.manager`)
- ❌ `CommandQueue`, `CommandExecutor`
- ❌ `PhysicsEngine`
- ❌ `UfoSim` (aus `controller`)
- ❌ Alle view-Pakete

**Begründung:**  
Observer ist Lese-only Analyse-Logik und darf keine Steuerungskomponenten kennen.

---

### 2.7 `controller` – Orchestrierung

**Verantwortung:**  
Hauptsteuerung der Simulation (Orchestrator).

**Inhalt:**
- `controller/sim.py`: `UfoSim` (Haupt-API-Klasse)
- `controller/lifecycle.py`: Lifecycle-Management (zukünftig)

**Position in Hierarchie:** **Anwendungsschicht** (Orchestrierung)

**Darf importieren:**
- ✅ `SimulationConfig`, `DEFAULT_CONFIG` (aus `config`)
- ✅ `UfoState` (aus `state.state`)
- ✅ `StateManager` (aus `state.manager`)
- ✅ `PhysicsEngine` (aus `physics.engine`)
- ✅ `CommandQueue`, `CommandExecutor` (aus `command`)
- ✅ `StateObserver`, `ManeuverAnalysis`, `Phase`, `compute_phase` (aus `observer`)
- ✅ `threading`, `logging`
- ✅ **Lazy Import:** `view.pview.UfoPView` (nur bei Bedarf)

**Darf NICHT importieren:**
- ❌ Direkte view-Imports außerhalb lazy-loading

**Besonderheit:**  
Controller ist der zentrale Orchestrator und darf alle unteren Schichten importieren.

---

### 2.8 `view` – GUI-Layer

**Verantwortung:**  
Grafische Darstellung der Simulation (PyQt5).

**Inhalt:**
- `view/viewport.py`: `UfoViewport`
- `view/viewmodel.py`: `SimulationViewModel`
- `view/pview.py`: `UfoPView`
- `view/hud.py`: HUD-Hilfsfunktionen

**Position in Hierarchie:** **Präsentationsschicht** (oberste Schicht)

**Darf importieren:**
- ✅ `UfoSim` (aus `controller.sim`) – **nur in pview.py**
- ✅ `Phase` (aus `observer.observer`) – für Typ-Annotationen
- ✅ `PyQt5` (externe GUI-Bibliothek)
- ✅ `numpy`, `typing`

**Darf NICHT importieren:**
- ❌ `PhysicsEngine`
- ❌ `StateManager`
- ❌ `CommandQueue`, `CommandExecutor`
- ❌ Direkte Zugriffe auf `state.manager` (nur via `UfoSim` API)

**Begründung:**  
View kommuniziert nur über die öffentliche API (`UfoSim`), nicht mit internen Details.

---

## 3. Import-Hierarchie – Matrix

### 3.1 Erlaubte Importrichtungen

Die folgende Matrix zeigt **erlaubte** Importrichtungen (`✅`):

| Importer ↓ / Import-Ziel → | config | utils | state.state | state.manager | physics | command | observer | controller | view |
|----------------------------|--------|-------|-------------|---------------|---------|---------|----------|------------|------|
| **config**                 | ✅     | ❌    | ❌          | ❌            | ❌      | ❌      | ❌       | ❌         | ❌   |
| **utils**                  | ❌     | ✅    | ❌          | ❌            | ❌      | ❌      | ❌       | ❌         | ❌   |
| **state.state**            | ❌     | ❌    | ✅          | ❌            | ❌      | ❌      | ❌       | ❌         | ❌   |
| **state.manager**          | ❌     | ✅    | ✅          | ✅            | ❌      | ❌      | ❌       | ❌         | ❌   |
| **physics**                | ✅     | ❌    | ✅          | ❌            | ✅      | ❌      | ❌       | ❌         | ❌   |
| **command.types**          | ❌     | ❌    | ⚠️¹         | ❌            | ❌      | ✅      | ❌       | ❌         | ❌   |
| **command.queue**          | ❌     | ❌    | ⚠️¹         | ❌            | ❌      | ✅      | ❌       | ❌         | ❌   |
| **command.executor**       | ❌     | ✅    | ❌          | ✅            | ❌      | ✅      | ❌       | ❌         | ❌   |
| **observer**               | ✅     | ❌    | ✅          | ❌            | ❌      | ❌      | ✅       | ❌         | ❌   |
| **controller**             | ✅     | ❌    | ✅          | ✅            | ✅      | ✅      | ✅       | ✅         | ⚠️²  |
| **view**                   | ❌     | ❌    | ❌          | ❌            | ❌      | ❌      | ⚠️³      | ✅         | ✅   |

**Legende:**
- ✅ = Erlaubt
- ❌ = Verboten
- ⚠️¹ = Nur via `TYPE_CHECKING` (keine Laufzeit-Abhängigkeit)
- ⚠️² = Nur lazy import (`if show_view: from ..view.pview import UfoPView`)
- ⚠️³ = Nur Typen (`Phase`) für Annotationen

### 3.2 Verbotene Importrichtungen

Folgende Importrichtungen sind **explizit verboten** und müssen in Code-Reviews verhindert werden:

```
❌ physics → state.manager
❌ physics → controller
❌ physics → view
❌ physics → observer
❌ observer → state.manager
❌ observer → controller
❌ observer → view
❌ observer → command
❌ view → physics
❌ view → state.manager
❌ view → command
❌ command → controller
❌ command → view
❌ command → observer (außer TYPE_CHECKING)
❌ utils → [jegliche Simulationselemente]
```

### 3.3 Hierarchie-Diagramm

Visualisierung der Schichten (Abhängigkeiten zeigen von oben nach unten):

```
┌─────────────────────────────────────────┐
│         view (Präsentation)             │
│  - viewport, viewmodel, pview, hud      │
└────────────────┬────────────────────────┘
                 │ (nur UfoSim API)
┌────────────────▼────────────────────────┐
│      controller (Orchestrierung)        │
│           - sim, lifecycle              │
└─┬───┬───┬───┬───┬───────────────────────┘
  │   │   │   │   │
  │   │   │   │   └──────────────────────┐
  │   │   │   │                          │
  │   │   │   └──────────────┐           │
  │   │   │                  │           │
  │   │   └──────┐           │           │
  │   │          │           │           │
┌─▼───▼──┐  ┌────▼────┐  ┌───▼──────┐ ┌─▼────────┐
│ state  │  │ physics │  │ command  │ │ observer │
│ manager│  │ engine  │  │ executor │ │ observer │
└───┬────┘  └────┬────┘  └────┬─────┘ └────┬─────┘
    │            │             │            │
┌───▼────────────▼─────────────▼────────────▼─────┐
│         state.state (UfoState)                  │
│         config (SimulationConfig)               │
│         utils (threads, maths)                  │
│                                                  │
│      Fundament (keine weiteren Abhängigkeiten)  │
└──────────────────────────────────────────────────┘
```

---

## 4. Konkrete Beispiele

### 4.1 Erlaubte Imports (✅)

#### Beispiel 1: Controller importiert alle Komponenten
```python
# In controller/sim.py
from ..config import SimulationConfig, DEFAULT_CONFIG
from ..state.state import UfoState
from ..state.manager import StateManager
from ..physics.engine import PhysicsEngine
from ..command.queue import CommandQueue
from ..command.executor import CommandExecutor
from ..observer.observer import StateObserver, Phase, compute_phase
```
**✅ Erlaubt:** Controller orchestriert alle unteren Schichten.

#### Beispiel 2: Physics importiert nur State und Config
```python
# In physics/engine.py
from ..config import SimulationConfig
from ..state.state import UfoState
import numpy as np
import logging
```
**✅ Erlaubt:** Physics arbeitet nur mit Datenmodell und Konfiguration.

#### Beispiel 3: Observer importiert nur State und Config
```python
# In observer/observer.py
from ..config import SimulationConfig
from ..state.state import UfoState
from collections import deque
```
**✅ Erlaubt:** Observer analysiert nur Zustandsdaten.

#### Beispiel 4: Command.types mit TYPE_CHECKING
```python
# In command/types.py
from typing import TYPE_CHECKING, Callable, Optional
from enum import Enum

if TYPE_CHECKING:
    from ..state.state import UfoState

class Command:
    condition: Optional[Callable[["UfoState"], bool]] = None
```
**✅ Erlaubt:** TYPE_CHECKING vermeidet Laufzeit-Zyklus.

#### Beispiel 5: View mit lazy import
```python
# In controller/sim.py
def start(self, show_view: bool = False):
    if show_view:
        from ..view.pview import UfoPView  # Lazy import
        self._view = UfoPView(self, viewport)
```
**✅ Erlaubt:** Lazy import verhindert unnötige PyQt5-Abhängigkeit.

---

### 4.2 Verbotene Imports (❌)

#### Anti-Pattern 1: Physics importiert StateManager
```python
# In physics/engine.py
from ..state.manager import StateManager  # ❌ VERBOTEN!

class PhysicsEngine:
    def __init__(self, manager: StateManager):  # ❌ FALSCH
        self._manager = manager
```
**❌ Verboten:** Physics darf StateManager nicht kennen.  
**✅ Korrekt:** Physics arbeitet mit `UfoState` als Parameter.

#### Anti-Pattern 2: Observer importiert Controller
```python
# In observer/observer.py
from ..controller.sim import UfoSim  # ❌ VERBOTEN!

class StateObserver:
    def notify(self, sim: UfoSim):  # ❌ FALSCH
        sim.reset()
```
**❌ Verboten:** Observer darf nicht steuern, nur beobachten.  
**✅ Korrekt:** Observer erhält `UfoState` Snapshots via Callback.

#### Anti-Pattern 3: View importiert Physics
```python
# In view/pview.py
from ..physics.engine import PhysicsEngine  # ❌ VERBOTEN!

class UfoPView:
    def display_physics_debug(self, engine: PhysicsEngine):  # ❌ FALSCH
        pass
```
**❌ Verboten:** View darf nur über `UfoSim` API zugreifen.  
**✅ Korrekt:** View nutzt `UfoSim.get_state_snapshot()`.

#### Anti-Pattern 4: Command importiert Observer
```python
# In command/executor.py
from ..observer.observer import compute_phase  # ❌ VERBOTEN!

class CommandExecutor:
    def check_phase(self, state):
        return compute_phase(state)  # ❌ FALSCH
```
**❌ Verboten:** CommandExecutor darf keine Phasen-Logik haben.  
**✅ Korrekt:** Phasen-Prüfung erfolgt im Controller.

#### Anti-Pattern 5: Utils importiert UfoState
```python
# In utils/maths.py
from ..state.state import UfoState  # ❌ VERBOTEN!

def calculate_speed(state: UfoState) -> float:  # ❌ FALSCH
    return np.linalg.norm([state.vx, state.vy, state.vz])
```
**❌ Verboten:** Utils müssen domänen-unabhängig bleiben.  
**✅ Korrekt:** Utils arbeiten mit generischen Parametern (z.B. `np.ndarray`).

---

## 5. Hinweise für neue Module

### 5.1 Klassifizierung neuer Module

Beim Hinzufügen neuer Module/Unterpakete folgende Fragen stellen:

1. **Gehört es zur Domänenlogik oder Infrastruktur?**
   - Domänenlogik → `state`, `physics`, `observer`
   - Infrastruktur → `utils`, `command`, `logging_setup`

2. **Benötigt es Zugriff auf den Controller?**
   - Ja → Gehört wahrscheinlich in `controller` oder `view`
   - Nein → Gehört in untere Schichten

3. **Ist es UI-spezifisch?**
   - Ja → `view`-Paket
   - Nein → Andere Pakete

4. **Ist es rein lesend (Observer-Pattern)?**
   - Ja → `observer`-Paket
   - Nein → Andere Pakete (z.B. `command` für Schreiboperationen)

5. **Ist es generisch wiederverwendbar ohne Domänen-Kontext?**
   - Ja → `utils`-Paket
   - Nein → Andere Pakete

### 5.2 Entscheidungsbaum

```
Neues Modul/Klasse?
│
├─ Ist es UI/GUI-spezifisch?
│  └─ Ja → view/
│
├─ Orchestriert es mehrere Komponenten?
│  └─ Ja → controller/
│
├─ Führt es Commands aus oder verwaltet State thread-sicher?
│  └─ Ja → command/ oder state.manager
│
├─ Berechnet es physikalische Zustandsübergänge?
│  └─ Ja → physics/
│
├─ Analysiert es nur Zustandsdaten (read-only)?
│  └─ Ja → observer/
│
├─ Ist es reines Datenmodell?
│  └─ Ja → state.state oder config
│
└─ Ist es generische Utility ohne Domänenbezug?
   └─ Ja → utils/
```

### 5.3 Beispiel-Szenarien

#### Szenario 1: Neue Physik-Komponente "Windmodell"

**Frage:** Wo platzieren?  
**Antwort:** `physics/wind.py`

**Begründung:**
- Berechnet physikalische Effekte → `physics`
- Importiert nur `UfoState`, `SimulationConfig`
- Wird von `PhysicsEngine` genutzt

**Erlaubte Imports:**
```python
# physics/wind.py
from ..config import SimulationConfig
from ..state.state import UfoState
```

#### Szenario 2: Neue Analyse "Energieverbrauch"

**Frage:** Wo platzieren?  
**Antwort:** `observer/metrics.py`

**Begründung:**
- Reine Analyse (read-only) → `observer`
- Berechnet Metriken aus Zustandshistorie
- Keine Steuerungslogik

**Erlaubte Imports:**
```python
# observer/metrics.py
from ..config import SimulationConfig
from ..state.state import UfoState
```

#### Szenario 3: Neue UI-Komponente "3D-Ansicht"

**Frage:** Wo platzieren?  
**Antwort:** `view/view3d.py`

**Begründung:**
- UI-spezifisch → `view`
- Nutzt nur `UfoSim` API
- Keine direkten Imports von internen Komponenten

**Erlaubte Imports:**
```python
# view/view3d.py
from ..controller.sim import UfoSim
from ..observer.observer import Phase
```

---

## 6. Anti-Patterns und Warnungen

### 6.1 Typische Anti-Patterns

#### ⚠️ Anti-Pattern 1: God Object in Controller
**Problem:** Controller wird zu groß und übernimmt Logik aus anderen Schichten.

**Symptome:**
- `UfoSim` enthält Physik-Berechnungen
- `UfoSim` enthält Observer-Logik
- Klasse > 500 Zeilen

**Lösung:**
- Physik → `PhysicsEngine`
- Analyse → `StateObserver`
- Controller bleibt reine Orchestrierung

---

#### ⚠️ Anti-Pattern 2: Zirkuläre Importe via Globale Variablen
**Problem:** Import-Zyklen werden durch globale Singletons "gelöst".

**Symptome:**
```python
# physics/engine.py
import core.simulation
global_sim = core.simulation.UfoSim()  # ❌ FALSCH
```

**Lösung:**
- Dependency Injection nutzen
- Parameter statt globale Variablen
- TYPE_CHECKING für Typ-Annotationen

---

#### ⚠️ Anti-Pattern 3: UI-Logik in Domänenschicht
**Problem:** GUI-Code leckt in State/Physics/Observer.

**Symptome:**
```python
# physics/engine.py
from PyQt5.QtCore import QTimer  # ❌ FALSCH
```

**Lösung:**
- GUI bleibt in `view/`
- Physik kennt keine UI-Frameworks
- Kommunikation nur über Callbacks/Observer-Pattern

---

#### ⚠️ Anti-Pattern 4: Observer mit Seiteneffekten
**Problem:** Observer ändert State oder ruft Steuerungs-Methoden auf.

**Symptome:**
```python
# observer/observer.py
class StateObserver:
    def on_state_change(self, state):
        state.thrust = 0  # ❌ FALSCH: Observer mutiert State
        self._sim.reset()  # ❌ FALSCH: Observer steuert Sim
```

**Lösung:**
- Observer sind **read-only**
- Keine State-Mutation
- Keine Controller-Aufrufe
- Nur Analyse und Logging

---

#### ⚠️ Anti-Pattern 5: Utils mit Domänenabhängigkeiten
**Problem:** Utils importieren Simulationselemente.

**Symptome:**
```python
# utils/helpers.py
from ..state.state import UfoState  # ❌ FALSCH
```

**Lösung:**
- Utils bleiben generisch
- Parameter-Typen: `np.ndarray`, `float`, etc.
- Keine Simulationsobjekte

---

### 6.2 Code-Review-Checkliste

Bei Code-Reviews folgende Punkte prüfen:

- [ ] **Keine verbotenen Importe** (siehe Matrix in Abschnitt 3.1)
- [ ] **TYPE_CHECKING korrekt genutzt** (falls nötig)
- [ ] **Lazy Imports für GUI** (view nur bei Bedarf laden)
- [ ] **Observer sind read-only** (keine State-Mutation)
- [ ] **Utils sind domänen-unabhängig** (keine Simulationsobjekte)
- [ ] **Physics kennt nur State + Config** (keine Manager/Controller)
- [ ] **View nutzt nur UfoSim API** (keine direkten Zugriffe auf Interna)
- [ ] **Keine zirkulären Abhängigkeiten** (mypy/IDE zeigt keine Warnungen)

---

## 7. Verknüpfung mit T0-Zielbild

### 7.1 Bezug zum Architektur-Zielbild

Die hier definierten Importregeln sind die **operativen Umsetzungsrichtlinien** für die im Dokument `docs/specs/architecture/core-simulation-zielbild.md` (T0) beschriebene Zielarchitektur.

**Mapping:**

| T0-Dokument (Zielbild)           | T1-Dokument (Importregeln)               |
|----------------------------------|------------------------------------------|
| Abschnitt 2: Paketstruktur       | Abschnitt 2: Paket-Verantwortlichkeiten  |
| Abschnitt 5: Import-Hierarchie   | Abschnitt 3: Import-Matrix               |
| Abschnitt 4: Öffentliche API     | Abschnitt 8: Verletzungen in API         |
| Abschnitt 6: Intern vs. Öffentlich | Abschnitt 6: Anti-Patterns            |

### 7.2 Ergänzende Aspekte zu T0

Während T0 die **Struktur** definiert (Welche Module gibt es?), definiert T1 die **Regeln** (Wer darf wen importieren?).

**Neue Informationen in T1:**
- **Import-Matrix:** Konkrete erlaubte/verbotene Kombinationen
- **Anti-Patterns:** Typische Fehler und deren Vermeidung
- **Entscheidungsbaum:** Klassifizierung neuer Module
- **Code-Review-Checkliste:** Praktische Prüfkriterien

### 7.3 Konsistenz mit T0

Alle Importregeln in diesem Dokument sind **konsistent** mit der in T0 definierten Struktur:

- ✅ Schichten-Hierarchie entspricht T0 Abschnitt 5.1
- ✅ Verbotene Imports entsprechen T0 Abschnitt 5.2
- ✅ Lazy imports für view entsprechen T0 Abschnitt 5.3
- ✅ API-Definitionen entsprechen T0 Abschnitt 4

**Keine Widersprüche** zu T0 identifiziert.

---

## 8. Bekannte Abweichungen in bestehendem Code

### 8.1 Analyse des aktuellen Zustands

**Stand:** 2025-11-18 (vor Refactoring-Phasen T2–T17)

Der aktuelle Code befindet sich noch im **monolithischen Zustand** (`ufosim.py` als Single-File).

**Dateistruktur aktuell:**
```
src/core/simulation/
├── __init__.py
├── ufosim.py          # Monolithische Implementierung
├── autopilot_base.py
└── ufo_main.py
```

### 8.2 Erwartete Verstöße vor Refactoring

Da die Refactoring-Phasen T2–T17 noch nicht durchgeführt wurden, sind folgende **systematische Abweichungen** erwartbar:

1. **Alle Klassen in einer Datei:**
   - `UfoState`, `StateManager`, `PhysicsEngine`, `CommandQueue`, `UfoSim`, `UfoPView` etc. existieren alle in `ufosim.py`
   - **Konsequenz:** Keine Import-Hierarchie kann verletzt werden (alles ist lokal)

2. **Keine Paket-Struktur:**
   - Unterpakete `state/`, `physics/`, `command/`, `observer/`, `view/` existieren noch nicht
   - **Konsequenz:** Import-Regeln können erst nach Extraktion geprüft werden

3. **Potenzielle interne Kopplungen:**
   - Vermutlich nutzt `PhysicsEngine` direkt `StateManager` (wird in T7 zu beheben sein)
   - Möglicherweise kennt `Observer` den `Controller` (wird in T9 zu beheben sein)

### 8.3 Bekannte Abweichungen (dokumentiert für spätere Tickets)

Folgende **konkrete Abweichungen** werden in den Refactoring-Phasen behoben:

| Abweichung | Beschreibung | Zu beheben in | Status |
|------------|--------------|---------------|--------|
| Monolith | Alle Klassen in `ufosim.py` | T2–T14 | ⏳ Geplant |
| Physics → StateManager | PhysicsEngine könnte StateManager kennen | T7 | ⏳ Zu prüfen |
| Observer → Controller | StateObserver könnte UfoSim-Referenz haben | T9 | ⏳ Zu prüfen |
| View → Internals | UfoPView könnte direkt auf StateManager zugreifen | T14 | ⏳ Zu prüfen |
| Utils → State | Hilfsfunktionen könnten UfoState importieren | T5–T6 | ⏳ Zu prüfen |

**Hinweis:**  
Diese Abweichungen sind **erwartbar** vor Refactoring und werden **systematisch** in den Tickets T2–T17 beseitigt.

### 8.4 Prüfung nach Refactoring

Nach Abschluss von **jedem Ticket** (T2–T17) muss geprüft werden:

1. **Import-Check:**
   ```bash
   # Prüfen auf zirkuläre Abhängigkeiten
   python -c "import core.simulation; print('OK')"
   mypy src/core/simulation/
   ```

2. **Matrix-Konformität:**
   - Alle Importe gegen Abschnitt 3.1 (Import-Matrix) prüfen
   - Verbotene Importe aus Abschnitt 3.2 müssen eliminiert sein

3. **Anti-Pattern-Check:**
   - Code-Review-Checkliste aus Abschnitt 6.2 durchgehen
   - Typische Anti-Patterns aus Abschnitt 6.1 vermeiden

---

## 9. Anwendung in Tickets T2–T17

### 9.1 Verwendung als Review-Referenz

Dieses Dokument dient als **verbindliche Referenz** für alle Code-Reviews in Tickets T2–T17:

**Für jeden Pull Request:**
1. Reviewer prüft neue/geänderte Imports gegen **Abschnitt 3.1** (Import-Matrix)
2. Reviewer prüft auf Anti-Patterns aus **Abschnitt 6.1**
3. Reviewer nutzt Checkliste aus **Abschnitt 6.2**

**Für Entwickler:**
1. Vor Commit: Eigene Imports gegen Matrix prüfen
2. Bei neuen Modulen: Entscheidungsbaum aus **Abschnitt 5.2** nutzen
3. Bei Unsicherheit: Konservative Annahme (niedrigere Schicht) wählen

### 9.2 Ticket-spezifische Anwendung

| Ticket | Fokus | Relevante Abschnitte in diesem Dokument |
|--------|-------|----------------------------------------|
| T2 | config.py | 2.1 (config), 3.1 (Matrix: config-Zeile) |
| T3 | state.py | 2.3.1 (state.state), 3.1 (Matrix: state.state-Zeile) |
| T4 | logging/exceptions | Nicht direkt betroffen (keine Importe) |
| T5 | utils/threads.py | 2.2 (utils), 3.1 (Matrix: utils-Zeile) |
| T6 | utils/maths.py | 2.2 (utils), 6.1 (Anti-Pattern 5) |
| T7 | physics/engine.py | 2.4 (physics), 3.1 (Matrix: physics-Zeile), 4.2 (Anti-Pattern 1) |
| T8 | state/manager.py | 2.3.2 (state.manager), 3.1 (Matrix: state.manager-Zeile) |
| T9 | observer/* | 2.6 (observer), 3.1 (Matrix: observer-Zeile), 4.2 (Anti-Pattern 2), 6.1 (Anti-Pattern 4) |
| T10 | command/types.py | 2.5.1 (command.types), 3.1 (Matrix: command.types-Zeile), 4.1 (Beispiel 4: TYPE_CHECKING) |
| T11 | command/queue.py | 2.5.2 (command.queue), 3.1 (Matrix: command.queue-Zeile) |
| T12 | command/executor.py | 2.5.3 (command.executor), 3.1 (Matrix: command.executor-Zeile), 4.2 (Anti-Pattern 4) |
| T13 | controller/sim.py | 2.7 (controller), 3.1 (Matrix: controller-Zeile), 4.1 (Beispiel 1, 5) |
| T14 | view/* | 2.8 (view), 3.1 (Matrix: view-Zeile), 4.2 (Anti-Pattern 3), 6.1 (Anti-Pattern 3) |
| T15 | autopilot | Außerhalb core.simulation (nutzt nur öffentliche API) |
| T16 | __init__.py | Abschnitt 7 (Verknüpfung mit T0), öffentliche API |
| T17 | Tests/Linting | Abschnitt 8.4 (Prüfung nach Refactoring) |

### 9.3 Eskalation bei Unklarheiten

**Falls Importrichtung unklar ist:**

1. **Schritt 1:** Entscheidungsbaum aus **Abschnitt 5.2** nutzen
2. **Schritt 2:** Beispiele aus **Abschnitt 4** konsultieren
3. **Schritt 3:** Konservative Annahme treffen (niedrigere Schicht)
4. **Schritt 4:** In PR-Beschreibung als "Offener Punkt" dokumentieren
5. **Schritt 5:** Tech Reviewer entscheidet final

**Dokumentation von Ausnahmen:**

Falls ein berechtigter Grund für eine Abweichung existiert:
1. **Begründung dokumentieren** (Kommentar im Code)
2. **Alternative Lösungen nennen** (warum nicht möglich)
3. **Reviewer-Freigabe einholen** (expliziter Kommentar im PR)
4. **Dieses Dokument aktualisieren** (Abschnitt 9.4: Genehmigte Ausnahmen)

### 9.4 Genehmigte Ausnahmen

**Stand:** 2025-11-18  
**Status:** Keine genehmigten Ausnahmen

_Dieser Abschnitt wird aktualisiert, falls begründete Abweichungen genehmigt werden._

---

## 10. Offene Punkte und konservative Annahmen

### 10.1 Konservative Annahmen

Folgende **konservative Entscheidungen** wurden bei Unklarheiten getroffen:

1. **TYPE_CHECKING für Command → State:**
   - **Unklarheit:** `introductions.md` nennt TYPE_CHECKING nur als Ausnahme.
   - **Annahme:** `command.types` und `command.queue` dürfen `UfoState` **nur via TYPE_CHECKING** importieren.
   - **Begründung:** Vermeidet Laufzeit-Zyklen, behält Typ-Sicherheit.

2. **Observer → config erlaubt:**
   - **Unklarheit:** `introductions.md` nennt `observer → state.state, config`.
   - **Annahme:** `SimulationConfig` ist erlaubt (für Schwellenwerte bei Phasenberechnung).
   - **Begründung:** Phasen-Logik benötigt Konfigurationsparameter.

3. **View → Phase (Typ-Annotation):**
   - **Unklarheit:** Darf View Observer-Typen importieren?
   - **Annahme:** `Phase` als Typ ist erlaubt (für Annotations), aber nicht `StateObserver` oder `compute_phase`.
   - **Begründung:** View muss Phase-Enum kennen (z.B. für Statusanzeige), aber keine Analyse-Logik.

4. **Utils vollständig domänen-frei:**
   - **Unklarheit:** "Nur Standardlib/numpy" – was ist mit `config`?
   - **Annahme:** Utils dürfen **keinerlei** Simulationselemente importieren (auch nicht `config`).
   - **Begründung:** Maximale Wiederverwendbarkeit.

5. **Lazy import für view obligatorisch:**
   - **Unklarheit:** Muss view immer lazy importiert werden?
   - **Annahme:** Ja, in `controller.sim` nur innerhalb `if show_view:`.
   - **Begründung:** Headless-Betrieb ohne PyQt5-Abhängigkeit.

### 10.2 Offene Fragen für Reviewer

Folgende Punkte sind zur **Diskussion im Review** vorgesehen:

1. **Frage 1:** Soll `observer.metrics.py` (zukünftig) auch `ManeuverAnalysis` erweitern oder separat bleiben?
   - **Aktuell:** `ManeuverAnalysis` in `observer/observer.py`
   - **Offen:** Eigenes Modul `metrics.py` sinnvoll?

2. **Frage 2:** Soll `physics/integrators.py` eigene Integrator-Klassen bekommen oder Funktionen?
   - **Aktuell:** Platzhalter
   - **Offen:** Klassenbasiert oder funktional?

3. **Frage 3:** Soll `controller/lifecycle.py` eigene Lifecycle-States bekommen (ähnlich Phase)?
   - **Aktuell:** Nicht definiert
   - **Offen:** Separates State-Modell oder Erweiterung von `Phase`?

4. **Frage 4:** Darf `autopilot` (außerhalb core.simulation) `Phase` importieren?
   - **Aktuell:** Als "öffentlich" markiert in T0
   - **Offen:** Ist das gewünscht oder soll Autopilot Phase-agnostisch sein?

**Hinweis:**  
Diese Fragen sind **nicht blockierend** für T1 und können in späteren Tickets geklärt werden.

---

## 11. Änderungshistorie

| Datum      | Version | Änderung                              | Autor    |
|------------|---------|---------------------------------------|----------|
| 2025-11-18 | 1.0     | Initiale Erstellung (Ticket T1)       | Copilot  |

---

## 12. Freigabe

Dieses Dokument wurde erstellt im Rahmen von **Ticket T1** und dient als **verbindliche Regelbasis** für alle Refactoring-Tickets T2–T17.

**Status:** ✅ Bereit für Review  
**Reviewer:** Tech Reviewer (ausstehend)  
**Gültig ab:** Nach Freigabe durch Tech Reviewer  
**Gültig bis:** Abschluss Phase 9 (T17)

---

## 13. Zusammenfassung

**Kernaussagen dieses Dokuments:**

1. **Import-Hierarchie ist verbindlich** – Keine Abweichungen ohne Freigabe
2. **Clean Architecture wird durchgesetzt** – Klare Schichtgrenzen
3. **Zyklen werden verhindert** – Unidirektionale Abhängigkeiten
4. **Observer sind read-only** – Keine Seiteneffekte
5. **View nutzt nur API** – Keine direkten Zugriffe auf Interna
6. **Utils sind generisch** – Keine Domänenabhängigkeiten
7. **TYPE_CHECKING für Typ-Sicherheit** – Vermeidung von Laufzeit-Zyklen
8. **Lazy imports für GUI** – Headless-Betrieb ohne PyQt5

**Dieses Dokument ist die Grundlage für alle folgenden Refactoring-Phasen.**

---

**Ende des Dokuments**
