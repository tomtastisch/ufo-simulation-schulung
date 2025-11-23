# Zukünftige Import-Linter Contracts

Dokumentiert geplante Architektur-Contracts für Module, die noch nicht implementiert sind.

## Zweck

Diese Datei dient der **Dokumentation** zukünftiger Architektur-Regeln. Die hier beschriebenen
Contracts werden NICHT aktiv validiert, sondern nur informativ angezeigt.

Sobald ein Modul implementiert ist, wird der entsprechende Contract in `pyproject.toml` unter
`[tool.importlinter]` übertragen und aktiv validiert.

---

## Geplante Contracts

### T11: CommandQueue ohne Kern- und View-Abhängigkeit

**Phase:** 5.2  
**Status:** Geplant  
**Modul:** `core.simulation.command.queue`

**Architektur-Regel:**

CommandQueue ist eine reine Datenstruktur für Command-Objekte und darf keine Abhängigkeiten
zu höheren Schichten (Observer, Physics, State, View, Controller) haben.

**Import-Linter Contract:**

```toml
[[tool.importlinter.contracts]]
id = "commandqueue-ohne-kern-und-view"
name = "CommandQueue ohne Kern- und View-Abhängigkeit"
type = "forbidden"
source_modules = [
    "core.simulation.command.queue",
]
forbidden_modules = [
    "core.simulation.state.manager",
    "core.simulation.physics",
    "core.simulation.observer",
    "core.simulation.controller",
    "core.simulation.view",
]
```

**Erlaubte Abhängigkeiten:**

- `core.simulation.command.types` (Command-Typen)
- Standard-Bibliothek (`typing`, `collections`, etc.)

**Migration:** Sobald `command/queue.py` existiert, Contract in `pyproject.toml` einfügen.

---

### T12: CommandExecutor ohne Observer/Engine/View

**Phase:** 5.3  
**Status:** Geplant  
**Modul:** `core.simulation.command.executor`

**Architektur-Regel:**

CommandExecutor führt Commands aus und darf keine direkten Abhängigkeiten zu Observer,
PhysicsEngine oder View haben. Kommunikation erfolgt über StateManager und CommandQueue.

**Import-Linter Contract:**

```toml
[[tool.importlinter.contracts]]
id = "commandexecutor-ohne-observer-engine-view"
name = "CommandExecutor ohne Observer/Engine/View"
type = "forbidden"
source_modules = [
    "core.simulation.command.executor",
]
forbidden_modules = [
    "core.simulation.physics",
    "core.simulation.observer",
    "core.simulation.controller",
    "core.simulation.view",
]
```

**Erlaubte Abhängigkeiten:**

- `core.simulation.command.types` (Command-Typen)
- `core.simulation.command.queue` (Queue-Zugriff)
- `core.simulation.state` (Zustandsänderungen)
- Standard-Bibliothek

**Migration:** Sobald `command/executor.py` existiert, Contract in `pyproject.toml` einfügen.

---

### T14: View ohne direkte Zugriffe auf Kernpakete

**Phase:** 7.1  
**Status:** Geplant  
**Modul:** `core.simulation.view`

**Architektur-Regel:**

Die View-Schicht darf nicht direkt auf Kernpakete (State, Physics, Command, Observer) zugreifen.
Alle Daten müssen über Controller bereitgestellt werden (Model-View-Controller Pattern).

**Import-Linter Contract:**

```toml
[[tool.importlinter.contracts]]
id = "view-ohne-direkte-kernzugriffe"
name = "View ohne direkte Zugriffe auf Kernpakete"
type = "forbidden"
source_modules = [
    "core.simulation.view",
]
forbidden_modules = [
    "core.simulation.state",
    "core.simulation.physics",
    "core.simulation.command",
    "core.simulation.observer",
]
```

**Erlaubte Abhängigkeiten:**

- `core.simulation.controller` (View ↔ Controller Kommunikation)
- PyQt6-Bibliotheken
- Standard-Bibliothek

**Migration:** Sobald `view/` Package existiert, Contract in `pyproject.toml` einfügen.

---

## Workflow: Contract-Aktivierung

### Schritt 1: Modul implementieren

Implementiere das geplante Modul gemäß Refactoring-Tracker und Architektur-Spezifikation.

### Schritt 2: Contract übertragen

1. Kopiere den TOML-Block aus dieser Datei
2. Füge ihn in `pyproject.toml` unter `[[tool.importlinter.contracts]]` ein
3. Entferne die Kommentare zu Phase/Status (nicht TOML-kompatibel)

### Schritt 3: Contract aus dieser Datei entfernen

Lösche den entsprechenden Abschnitt aus dieser Dokumentation, da der Contract nun aktiv ist.

### Schritt 4: Validieren

```bash
python tools/imports.py
```

Der Contract wird nun automatisch bei jeder Analyse geprüft.

---

## Anzeige

Die geplanten Contracts werden automatisch von `tools/analyze_imports.py` ausgewertet und angezeigt:

```bash
$ python tools/imports.py

================================================================================
2️⃣  GEPLANTE ARCHITEKTUR-CONTRACTS (Zukünftige Module)
================================================================================

📋 3 geplante Contract(s) dokumentiert:
  • CommandQueue ohne Kern- und View-Abhängigkeit (Phase 5.2, T11)
  • CommandExecutor ohne Observer/Engine/View (Phase 5.3, T12)
  • View ohne direkte Zugriffe auf Kernpakete (Phase 7.1, T14)
```

---

## Weitere Ressourcen

- **Refactoring-Tracker:** `docs/planning/refactoring-tracker.md`
- **Architektur-Spezifikation:** `docs/specs/architecture/core-simulation-zielbild.md`
- **Import-Analyse-Dokumentation:** `docs/dev/import-analysis.md`
- **Import-Linter Dokumentation:** https://import-linter.readthedocs.io/

