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

