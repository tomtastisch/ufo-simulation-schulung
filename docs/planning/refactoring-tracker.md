# Refactoring-Tracker – core.simulation

**Letzte Aktualisierung:** 2025-11-20

Dieser Tracker spiegelt den Ablaufplan aus `docs/specs/notes/introductions.md` und gliedert jede Phase in konkrete
Tickets mit Branches, Verantwortlichkeiten und Prüfschritten. Alle Beschreibungen sind bewusst deutsch gehalten.

**Zweck**: Verfolgung des Implementierungsstatus aller Refactoring-Tickets (T0–T17) für das `core.simulation` Paket.

## Übersicht

| Ticket-ID | Abschnitt     | Kurzbeschreibung                                                 | Haupt-Branch                           | Status          | Owner    | Reviewer      | Abgeschlossen am | QA / Prüfschritte                                                |
|-----------|---------------|------------------------------------------------------------------|----------------------------------------|-----------------|----------|---------------|------------------|------------------------------------------------------------------|
| T0        | Abschnitt 0   | Zielbild & API-Festlegung dokumentieren                          | feature/refactor-phase0-zielbild       | ✅ Merged        | Lead Dev | Tech Reviewer | 2025-11-18       | Self-Check: Strukturdiagramm; Review: Gegenlesen durch Reviewer  |
| T1        | Abschnitt 1   | Importhierarchie definieren & dokumentieren                      | feature/refactor-phase1-importregeln   | ✅ Merged        | Lead Dev | Tech Reviewer | 2025-11-18       | Self-Check: Regelmatrix; Review: Prüfung auf Konsistenz          |
| T2        | Abschnitt 2.1 | `config.py` + `DEFAULT_CONFIG` extrahieren                       | feature/refactor-phase2-config-state   | ⏳ Validierung   | Lead Dev | Peer Reviewer | -                | Self-Check: Modul läuft standalone; QA: Tests gegen alte Version |
| T3        | Abschnitt 2.2 | `UfoState` nach `state/state.py` verlagern                       | copilot/feat-refactor-phase2-state     | ✅ Implementiert | Lead Dev | Peer Reviewer | 2025-11-19       | Self-Check: Typprüfungen; QA: Simulationslauf (6 Tests passed)   |
| T4        | Abschnitt 2.3 | `logging_setup.py` & `exceptions.py` anlegen                     | feature/refactor-phase2-config-state   | ✅ Merged        | Lead Dev | Peer Reviewer | 2025-11-19       | Self-Check: Logging-Test; QA: Fehlerpfad prüfen                  |
| T5        | Abschnitt 3.1 | `utils/threads.py` (`@synchronized`)                             | feature/refactor-phase3-utils-physics  | ⏹️ Ausstehend   | Lead Dev | Peer Reviewer | -                | Self-Check: Multithread-Test; QA: Code-Review                    |
| T6        | Abschnitt 3.2 | `utils/maths.py` (numerische Helfer)                             | feature/refactor-phase3-utils-physics  | ⏹️ Ausstehend   | Lead Dev | Peer Reviewer | -                | Self-Check: Unit-Tests; QA: Review                               |
| T7        | Abschnitt 3.3 | `physics/engine.py` auslagern                                    | feature/refactor-phase3-utils-physics  | ⏹️ Ausstehend   | Lead Dev | Tech Reviewer | -                | Self-Check: Integrations-Test; QA: Physik-Regressionstest        |
| T8        | Abschnitt 4.1 | `StateManager` nach `state/manager.py`                           | feature/refactor-phase4-state-observer | ⏹️ Ausstehend   | Lead Dev | Peer Reviewer | -                | Self-Check: Observer-Benachrichtigungen; QA: Threading-Test      |
| T9        | Abschnitt 4.2 | `Phase`, `compute_phase`, `StateObserver`                        | feature/refactor-phase4-state-observer | ⏹️ Ausstehend   | Lead Dev | Tech Reviewer | -                | Self-Check: Analysen; QA: Unit-Tests                             |
| T10       | Abschnitt 5.1 | `CommandType`, `Command` nach `command/types.py`                 | feature/refactor-phase5-command        | ⏹️ Ausstehend   | Lead Dev | Peer Reviewer | -                | Self-Check: Typchecker; QA: Test Queue                           |
| T11       | Abschnitt 5.2 | `CommandQueue` nach `command/queue.py`                           | feature/refactor-phase5-command        | ⏹️ Ausstehend   | Lead Dev | Peer Reviewer | -                | Self-Check: Szenario-Test; QA: Review                            |
| T12       | Abschnitt 5.3 | `CommandExecutor` nach `command/executor.py`                     | feature/refactor-phase5-command        | ⏹️ Ausstehend   | Lead Dev | Tech Reviewer | -                | Self-Check: Integration; QA: Deadlock-Test                       |
| T13       | Abschnitt 6.1 | `UfoSim` als `controller/sim.py` orchestrieren                   | feature/refactor-phase6-controller     | ⏹️ Ausstehend   | Lead Dev | Tech Reviewer | -                | Self-Check: Vollständiger Flug; QA: Regressionstest              |
| T14       | Abschnitt 7.1 | View-Module separieren (`viewport`, `viewmodel`, `hud`, `pview`) | feature/refactor-phase7-view           | ⏹️ Ausstehend   | Lead Dev | UI Reviewer   | -                | Self-Check: GUI-Manuelltest; QA: Headless-Lauf                   |
| T15       | Abschnitt 8.1 | Autopilot außerhalb Kernpaket halten                             | feature/refactor-phase8-autopilot      | ⏹️ Ausstehend   | Lead Dev | Peer Reviewer | -                | Self-Check: API-Aufruf; QA: Schulungs-Task                       |
| T16       | Abschnitt 9.1 | `core/simulation/__init__.py` als API-Gateway                    | feature/refactor-phase9-api-tests      | ⏹️ Ausstehend   | Lead Dev | Tech Reviewer | -                | Self-Check: Importtest; QA: Externes Skript                      |
| T17       | Abschnitt 9.2 | Tests & Linting erweitern                                        | feature/refactor-phase9-api-tests      | ⏹️ Ausstehend   | Lead Dev | QA Engineer   | -                | Self-Check: pytest lokal; QA: CI-Lauf                            |

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

1. Status-Spalte aktualisieren, sobald T0/T1 abgeschlossen sind.
2. Für neue Anforderungen weitere Zeilen ergänzen und Branch-Schema beibehalten.

