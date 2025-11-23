# Import-Analyse & Architektur-Validierung

## 📋 Übersicht

Das Projekt verwendet **import-linter** zur automatischen Validierung der Architektur-Regeln.

## 🛠️ Verwendung

### Schnellstart

```bash
# Vollständige Analyse ausführen
python tools/imports.py

# Nur aktive Contracts prüfen
lint-imports

# Mit Details
lint-imports --verbose
```

### Ausgabe-Beispiel

```
================================================================================
UMFASSENDE IMPORT-ANALYSE
================================================================================

================================================================================
1️⃣  IMPORT- UND ARCHITEKTUR-PRÜFUNG (import-linter)
================================================================================

Contracts: 4 kept, 1 broken.

PhysicsEngine kennt keine High-Level-Komponenten BROKEN
  core.simulation.physics.engine -> core.simulation.state.manager

================================================================================
2️⃣  GEPLANTE ARCHITEKTUR-CONTRACTS (Zukünftige Module)
================================================================================

📋 3 geplante Contract(s) dokumentiert:
  • CommandQueue ohne Kern- und View-Abhängigkeit (Phase 5.2, T11)
  • CommandExecutor ohne Observer/Engine/View (Phase 5.3, T12)
  • View ohne direkte Zugriffe auf Kernpakete (Phase 7.1, T14)
```

## 📂 Konfiguration

### Aktive Contracts (`pyproject.toml`)

Contracts für **existierende Module** werden in `pyproject.toml` unter `[tool.importlinter]` definiert:

```toml
[[tool.importlinter.contracts]]
id = "physics-ohne-highlevel"
name = "PhysicsEngine kennt keine High-Level-Komponenten"
type = "forbidden"
source_modules = ["core.simulation.physics.engine"]
forbidden_modules = ["core.simulation.state.manager", ...]
```

**Diese werden automatisch validiert** bei jedem Lauf.

### Zukünftige Contracts (`.importlinter-future.toml`)

Contracts für **noch nicht implementierte Module** werden in `.importlinter-future.toml` dokumentiert:

```toml
[[contracts]]
id = "commandqueue-ohne-kern-und-view"
phase = "5.2"
task = "T11"
source_modules = ["core.simulation.command.queue"]  # Existiert noch nicht
forbidden_modules = [...]
```

**Diese werden NUR angezeigt**, aber nicht validiert.

## 🔄 Workflow: Modul-Migration

Wenn ein geplantes Modul implementiert wird:

### 1. Contract aus `docs/dev/refactoring/future-contracts.md` kopieren

Öffne die Datei und suche den entsprechenden Contract (z.B. T11, T12, T14).

### 2. TOML-Block in `pyproject.toml` einfügen

Kopiere den TOML-Block und füge ihn unter `[[tool.importlinter.contracts]]` ein.

### 3. Contract aus `future-contracts.md` entfernen

Lösche den gesamten Abschnitt (###-Überschrift bis zur nächsten ---).

### 4. Validieren

```bash
python tools/imports.py
```

Der Contract wird nun automatisch validiert.

**Siehe**: `docs/dev/refactoring/future-contracts.md` für detaillierten Workflow

## 📊 Architektur-Regeln

### Layer-Hierarchie (Top → Bottom)

```
core.simulation.view              # Optional (Phase 7, T14)
core.simulation.controller         # Optional (Phase 6, T13)
core.simulation.command
core.simulation.observer
core.simulation.physics
core.simulation.state
core.simulation.utils
core.simulation.infrastructure.config
```

**Regel**: Höhere Layer dürfen niedrigere importieren, aber NICHT umgekehrt.

### Verbotene Abhängigkeiten

| Modul                 | Darf NICHT importieren           | Grund                              |
|-----------------------|----------------------------------|------------------------------------|
| `physics.engine`      | `state.manager`                  | Zirkuläre Abhängigkeit vermeiden   |
| `state.manager`       | `physics`, `observer`, `command` | Low-Level bleibt unabhängig        |
| `observer.observer`   | `physics`, `state.manager`       | Observer nur Daten-Konsument       |
| `utils.*`, `config.*` | Simulation-Typen                 | Wiederverwendbare Low-Level-Module |

## 🎯 Zukünftige Regeln (geplant)

- **T11** (Phase 5.2): `command.queue` ohne Kern-Abhängigkeiten
- **T12** (Phase 5.3): `command.executor` ohne Observer/Engine
- **T14** (Phase 7.1): `view` ohne direkte Kern-Zugriffe

## 🔍 Fehlersuche

### "Module X does not exist"

**Ursache:** Contract in `pyproject.toml` referenziert nicht-existierendes Modul  
**Lösung:** Contract nach `docs/dev/refactoring/future-contracts.md` verschieben (als Dokumentation)

### "Could not read configuration"

**Ursache:** `pyproject.toml` nicht gefunden oder PYTHONPATH falsch  
**Lösung:** Script aus Projekt-Root ausführen oder `analyze_imports.py` verwenden

### Contracts werden nicht gefunden

**Ursache:** Cache-Problem  
**Lösung:** `rm -rf .import_linter_cache/` und erneut ausführen

### Future-Contracts werden nicht angezeigt

**Ursache:** `docs/dev/refactoring/future-contracts.md` fehlt oder hat falsches Format  
**Lösung:** Prüfe ob Datei existiert und Markdown-Struktur korrekt ist (### T##: Name)

## 📚 Weitere Ressourcen

- **Import-Linter Dokumentation**: https://import-linter.readthedocs.io/
- **Refactoring-Tracker**: `docs/planning/refactoring-tracker.md`
- **Architektur-Spezifikation**: `docs/specs/architecture/core-simulation-zielbild.md`

