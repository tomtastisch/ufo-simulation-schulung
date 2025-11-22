# Refactoring-Tracker – core.simulation

**Letzte Aktualisierung:** 2025-11-22

Dieser Tracker spiegelt den Ablaufplan aus `docs/specs/notes/introductions.md` und gliedert jede Phase in konkrete
Tickets mit Branches, Verantwortlichkeiten und Prüfschritten. Alle Beschreibungen sind bewusst deutsch gehalten.

**Zweck**: Verfolgung des Implementierungsstatus aller Refactoring-Tickets (T0–T17) für das `core.simulation` Paket.

## Übersicht

| Ticket-ID | Abschnitt     | Kurzbeschreibung                                                 | Haupt-Branch                           | Status        | Owner    | Reviewer      | Abgeschlossen am | QA / Prüfschritte                                                 |
|-----------|---------------|------------------------------------------------------------------|----------------------------------------|---------------|----------|---------------|------------------|-------------------------------------------------------------------|
| T0        | Abschnitt 0   | Zielbild & API-Festlegung dokumentieren                          | feature/refactor-phase0-zielbild       | ✅ Merged      | Lead Dev | Tech Reviewer | 2025-11-18       | Self-Check: Strukturdiagramm; Review: Gegenlesen durch Reviewer   |
| T1        | Abschnitt 1   | Importhierarchie definieren & dokumentieren                      | feature/refactor-phase1-importregeln   | ✅ Merged      | Lead Dev | Tech Reviewer | 2025-11-18       | Self-Check: Regelmatrix; Review: Prüfung auf Konsistenz           |
| T2        | Abschnitt 2.1 | `config.py` + `DEFAULT_CONFIG` extrahieren                       | feature/refactor-phase2-config-state   | ✅ Merged      | Lead Dev | Peer Reviewer | 2025-11-15       | Self-Check: Modul läuft standalone; QA: Tests erfolgreich (PR #6) |
| T3        | Abschnitt 2.2 | `UfoState` nach `state/state.py` verlagern                       | copilot/feat-refactor-phase2-state     | ✅ Merged      | Lead Dev | Peer Reviewer | 2025-11-16       | Self-Check: Typprüfungen; QA: Simulationslauf (10 Tests, PR #10)  |
| T4        | Abschnitt 2.3 | `logging_setup.py` & `exceptions.py` anlegen                     | feature/refactor-phase2-config-state   | ✅ Merged      | Lead Dev | Peer Reviewer | 2025-11-18       | Self-Check: Logging-Test; QA: Thread-Safety validiert (PR #11)    |
| T5        | Abschnitt 3.1 | `synchronization/` (`@synchronized`)                             | copilot/feat-refactor-phase3-threads   | ✅ Merged      | Lead Dev | Peer Reviewer | 2025-11-19       | Self-Check: Multithread-Test; QA: umfassende Tests (PR #12)       |
| T6        | Abschnitt 3.2 | `utils/maths.py` (numerische Helfer)                             | copilot/refactor-maths-utils-phase-3-2 | ✅ Merged      | Lead Dev | Peer Reviewer | 2025-11-19       | Self-Check: Unit-Tests; QA: validation.py, geometry.py (PR #13)   |
| T7        | Abschnitt 3.3 | `physics/engine.py` auslagern                                    | feature/refactor-phase3-physics        | ✅ Merged      | Lead Dev | Tech Reviewer | 2025-11-21       | Self-Check: Integrations-Test; QA: Physik-Tests erfolgreich       |
| T8        | Abschnitt 4.1 | `StateManager` nach `state/manager.py`                           | feature/refactor-phase4-state-manager  | ✅ Merged      | Lead Dev | Peer Reviewer | 2025-11-21       | Self-Check: Observer-Pattern; QA: Threading-Tests erfolgreich     |
| T9        | Abschnitt 4.2 | `Phase`, `compute_phase`, `StateObserver`                        | feature/refactor-phase4-state-observer | ✅ Merged      | Lead Dev | Tech Reviewer | 2025-11-22       | Self-Check: Analysen; QA: Unit-Tests erfolgreich                  |
| T10       | Abschnitt 5.1 | `CommandType`, `Command` nach `command/types.py`                 | copilot/feat-refactor-command-types    | 🚧 In Arbeit  | Lead Dev | Peer Reviewer | -                | Self-Check: Typchecker; QA: Test Queue                            |
| T11       | Abschnitt 5.2 | `CommandQueue` nach `command/queue.py`                           | feature/refactor-phase5-command        | ⏹️ Ausstehend | Lead Dev | Peer Reviewer | -                | Self-Check: Szenario-Test; QA: Review                             |
| T12       | Abschnitt 5.3 | `CommandExecutor` nach `command/executor.py`                     | feature/refactor-phase5-command        | ⏹️ Ausstehend | Lead Dev | Tech Reviewer | -                | Self-Check: Integration; QA: Deadlock-Test                        |
| T13       | Abschnitt 6.1 | `UfoSim` als `controller/sim.py` orchestrieren                   | feature/refactor-phase6-controller     | ⏹️ Ausstehend | Lead Dev | Tech Reviewer | -                | Self-Check: Vollständiger Flug; QA: Regressionstest               |
| T14       | Abschnitt 7.1 | View-Module separieren (`viewport`, `viewmodel`, `hud`, `pview`) | feature/refactor-phase7-view           | ⏹️ Ausstehend | Lead Dev | UI Reviewer   | -                | Self-Check: GUI-Manuelltest; QA: Headless-Lauf                    |
| T15       | Abschnitt 8.1 | Autopilot außerhalb Kernpaket halten                             | feature/refactor-phase8-autopilot      | ⏹️ Ausstehend | Lead Dev | Peer Reviewer | -                | Self-Check: API-Aufruf; QA: Schulungs-Task                        |
| T16       | Abschnitt 9.1 | `core/simulation/__init__.py` als API-Gateway                    | feature/refactor-phase9-api-tests      | ⏹️ Ausstehend | Lead Dev | Tech Reviewer | -                | Self-Check: Importtest; QA: Externes Skript                       |
| T17       | Abschnitt 9.2 | Tests & Linting erweitern                                        | feature/refactor-phase9-api-tests      | ⏹️ Ausstehend | Lead Dev | QA Engineer   | -                | Self-Check: pytest lokal; QA: CI-Lauf                             |

## Pflegeprozess

- **Statuspflege**: Spalte „QA / Prüfschritte“ nach jedem Merge mit Datum + Kurzhinweis ergänzen.
- **Branch-Namen**: Schema `feature/refactor-phase{N}-{thema}`; Subbranches
  `feature/refactor-phase{N}-{thema}/sub/{detail}`.
- **Verantwortlichkeiten**: Lead Dev (Hauptimplementierung), Reviewer (Code-Review), QA (Tests/Checks nach Option B:
  Selbsttest + unabhängige Prüfung).
- **Referenz**: Detaillierte Anforderungen siehe `docs/specs/notes/introductions.md` (Abschnittsnummer entspricht
  Ticket-ID). **Architektur-Zielbild**: `docs/specs/architecture/core-simulation-zielbild.md` (erstellt in T0) – 
  verbindliche Referenz für alle Phasen T1–T17.

## Nächste Schritte

1. ✅ T0–T9 abgeschlossen (siehe Detailübersicht unten)
2. 🚧 T10 (`command/types.py` - CommandType, Command) **in Arbeit** im Branch `copilot/feat-refactor-command-types`
3. ⏭️ T11–T12 (CommandQueue, CommandExecutor) als nächste Tickets nach T10
3. Für neue Anforderungen weitere Zeilen ergänzen und Branch-Schema beibehalten

---

## Detaillierte Ticket-Übersicht

### ✅ Phase 0-2: Zielbild, Architektur & Basis-Infrastruktur (T0–T4)

**Umfasst:**

- Phase 0: Zielbild / Endzustand (T0)
- Phase 1: Architektur- und Importregeln (T1)
- Phase 2: Basis: Konfiguration, State, Logging (T2-T4)

#### T0: Zielbild & API-Festlegung ✅

- **Datum:** 2025-11-18
- **Deliverables:**
    - `docs/specs/architecture/core-simulation-zielbild.md` erstellt
    - Vollständige Paketstruktur dokumentiert
    - API-Spezifikation definiert
- **Qualitätssicherung:** Strukturdiagramm validiert, Review durch Tech Reviewer

#### T1: Importhierarchie ✅

- **Datum:** 2025-11-18
- **Deliverables:**
    - `docs/specs/architecture/core-simulation-importregeln.md` erstellt
    - Import-Matrix definiert
    - Dependency-Regeln festgelegt
- **Qualitätssicherung:** Regelmatrix geprüft

#### T2: Konfigurationsmodul ✅

- **Datum:** 2025-11-15
- **PR:** #6 (Commit: `7444352`)
- **Deliverables:**
    - `SimulationConfig` als Dataclass implementiert
    - `DEFAULT_CONFIG` definiert
    - Integration in `ufosim.py`
- **Qualitätssicherung:** Tests erfolgreich

#### T3: State-Extraktion ✅

- **Datum:** 2025-11-16
- **PR:** #10 (Commits: `245f79f`, `86cc29a`, `fdeedea`, `5a2b535`, `d798b4e`)
- **Deliverables:**
    - `UfoState` als frozen Dataclass nach `state/state.py` extrahiert
    - `StateProxy` für View-Layer implementiert
    - Immutability-Pattern eingeführt
    - `PhysicsEngine` und `StateManager` refaktoriert
- **Qualitätssicherung:** 10 neue Tests, alle erfolgreich

#### T4: Exceptions & Logging ✅

- **Datum:** 2025-11-18
- **PR:** #11 (Commits: `1c7e4f7`, `17e9c3f`, `5b3c9e9`)
- **Deliverables:**
    - `exceptions.py` mit Exception-Hierarchie
    - `logging_setup.py` mit thread-sicherer Konfiguration
    - Tests für beide Module
- **Architektonische Änderungen:**
    - Exception-Hierarchie: `SimulationError` als Basis
    - Thread-sicheres Logging mit RLock
- **Qualitätssicherung:** Race-Condition behoben, Thread-Safety validiert

---

### ✅ Phase 3: Utilities & Physik (T5–T7)

**Umfasst:**

- Abschnitt 3.1: utils/threads.py → synchronization/ (T5)
- Abschnitt 3.2: utils/maths.py (T6)
- Abschnitt 3.3: physics/engine.py (T7)

#### T5: Threading Utilities (synchronization/) ✅

- **Datum:** 2025-11-19
- **PR:** #12 (Commits: `92657f2`, `b4bd754`, `6f561a6`, `ba29984`, `e40b4b4`, `557c97a`, `db7e4e0`, etc.)
- **Deliverables:**
    - `@synchronized` Decorator für Instanz-Locks
    - `@synchronized_global` Decorator für Modul-Locks
    - Refactoring aller Lock-Pattern im Codebase
    - pytest-timeout, threadpoolctl, py-spy für Debugging
- **Architektonische Änderungen:**
    - Ursprünglich `utils/threads.py`, umbenannt zu `synchronization/`
    - Konsistente Thread-Safety durch Decorators
    - Trennung von Instanz- und Modul-Locks
- **Qualitätssicherung:** Umfangreiche Threading-Tests, pytest-Markers

#### T6: Mathematische Utilities ✅

- **Datum:** 2025-11-19
- **PR:** #13 (Commits: `f2b7013`, `cbee8b3`, `f4f6bc9`, `bfd4179`, `15cbc73`)
- **Deliverables:**
    - `utils/maths.py` mit numerischen Hilfsfunktionen
    - `utils/validation.py` für Eingabe-Validierung
    - `utils/geometry.py` für geometrische Berechnungen
- **Architektonische Änderungen:**
    - Framework-unabhängige mathematische Utilities
    - Validierungs-Framework
    - Magic Numbers durch benannte Konstanten ersetzt
- **Qualitätssicherung:** Unit-Tests, Performance-Optimierungen, Code-Review

#### T7: Physics Engine ✅

- **Datum:** 2025-11-21
- **Deliverables:**
    - `PhysicsEngine` als eigenständige Klasse nach `physics/engine.py` extrahiert
    - Framework-unabhängige Physik-Berechnungen
    - Integration in `StateManager`
- **Qualitätssicherung:** Integrations-Tests erfolgreich

---

### 📦 Modul-Reorganisation & Dokumentations-Konsolidierung ✅

**Datum:** 2025-11-19–2025-11-20  
**Commits:** `df334a3`, `0820fe3`

**Durchgeführte Arbeiten:**

1. **Exceptions-Modul:** `exceptions.py` → `exceptions/` Package-Struktur
    - `exceptions/__init__.py` (zentrale API)
    - `exceptions/simulation.py` (Exception-Klassen)

2. **Infrastructure-Modul:** Neues Package erstellt
    - `config.py` → `infrastructure/config.py`
    - `logging_setup.py` → `infrastructure/logging_setup.py`
    - `infrastructure/__init__.py` (zentrale API)

3. **Dokumentations-Konsolidierung:**
    - Alle Modul-README.md entfernt
    - Umfassende Dokumentation in `__init__.py`-Dateien
    - Nur eine zentrale README.md im Projekt-Root
    - Dokumentationsreduktion: 63–76%

**Strukturelle Änderungen:**

```
Neu:
- src/core/simulation/exceptions/
- src/core/simulation/infrastructure/

Verschoben:
- config.py → infrastructure/config.py
- logging_setup.py → infrastructure/logging_setup.py

Gelöscht:
- exceptions.py (→ exceptions/simulation.py)
- Alle Modul-READMEs
```

**Validierung:**

- ✅ Alle 52 Tests erfolgreich
- ✅ API-Kompatibilität gewahrt
- ✅ Import-Pfade aktualisiert

---

### ✅ Phase 4: StateManager & Observer (T8–T9)

**Umfasst:**

- Abschnitt 4.1: state/manager.py (StateManager) - T8
- Abschnitt 4.2: observer/observer.py (Phase, compute_phase, ManeuverAnalysis) - T9

**Status:** Abgeschlossen  
**Nächste Phase:** T10 (command/types.py)

#### T8: StateManager ✅

- **Datum:** 2025-11-21
- **Deliverables:**
    - `StateManager` nach `state/manager.py` extrahiert
    - Observer-Pattern für State-Updates
    - Thread-sichere Synchronisation
- **Qualitätssicherung:** Threading-Tests erfolgreich

#### T9: Observer-Modul ✅

- **Datum:** 2025-11-22
- **Deliverables:**
    - `Phase`-Enum in `observer/phase.py`
    - `compute_phase()` für Phasenbestimmung
    - `StateObserver`-Protokoll in `observer/observer.py`
    - `ManeuverAnalysis` für Manövererkennung
    - `normalize_heading_delta()` in `observer/heading_delta.py`
- **Qualitätssicherung:** Unit-Tests erfolgreich (3 Test-Dateien)

---

### 🚧 Phase 5: Command System (T10–T12)

**Status:** In Arbeit (T10)  
**Aktueller Branch:** copilot/feat-refactor-command-types  
**Nächste Tickets:** T11 (CommandQueue), T12 (CommandExecutor)

#### T10: Command Types 🚧

- **Status:** In Arbeit
- **Branch:** copilot/feat-refactor-command-types
- **Startdatum:** 2025-11-22
- **Ziel:**
    - `CommandType`-Enum nach `command/types.py` extrahieren
    - `Command`-Dataclass nach `command/types.py` extrahieren
    - TYPE_CHECKING für UfoState-Referenzen verwenden
- **Geplante Deliverables:**
    - `command/types.py` mit CommandType-Enum
    - `command/types.py` mit Command-Dataclass
    - Unit-Tests für Command-Typen
    - Typchecker-Validierung (mypy)

