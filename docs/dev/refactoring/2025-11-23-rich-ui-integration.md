# Refactoring: Rich UI Integration für Setup-Tools

**Datum:** 2025-11-23  
**Typ:** Verbesserung/Refactoring  
**Scope:** tools/

## Übersicht

Integration der `rich`-Bibliothek für moderne, formatierte Terminal-Ausgaben in allen Setup- und Analyse-Tools.
Ersetzung von eigenem ASCII-Art und manuellen print-Funktionen durch eine zentrale, wiederverwendbare UI-Schicht.

## Änderungen

### Neue Dateien

#### `tools/ui.py`

Zentrale UI- und Logging-Helfer für Setup-/Tool-Skripte mit folgenden Komponenten:

- **`SetupConsole`**: Statische Methoden für strukturierte Konsolenausgaben
    - `header()`: Prominente Header mit Trennlinien
    - `subheader()`: Unter-Header in Panels
    - `success()`, `error()`, `warning()`, `info()`, `fix()`: Formatierte Meldungen

- **`StepProgress`**: Kontextmanager für Fortschrittsbalken
    - **NICHT** transient (bleibt sichtbar nach Abschluss)
    - `advance(step, status)` für schrittweisen Fortschritt
    - Threading-kompatibel für Hintergrund-Prozesse

- **`ErrorLog`**: Fehlerprotokollierung in setup.log
    - Erstellt Datei nur bei Fehlern
    - Erster Fehler überschreibt, weitere werden angehängt
    - Timestamps und strukturiertes Format

### Geänderte Dateien

#### `requirements.txt`

- Hinzugefügt: `rich>=13.0.0` für Console UI

#### `tools/analyze_imports.py`

**Entfernt:**

- Manuelle ASCII-Banner (`print("=" * 80)`)
- Direkte print-Aufrufe

**Ersetzt durch:**

- `SetupConsole.header()`, `SetupConsole.info()`, etc.
- **Progress-Bar während import-linter läuft** (simuliert, da Subprocess)
- Statische Methoden wo zuvor Instanzmethoden waren:
    - `_build_env_with_src()` → `@staticmethod`
    - `_parse_future_contracts()` → `@staticmethod`
    - `_print_summary()` → `@staticmethod`
- Rückgabe von `(exit_code, output)` statt nur `exit_code` für bessere Integration
- Threading für Hintergrund-Ausführung mit Progress-Anzeige

#### `tools/bootstrap_env.py`

**Entfernt:**

- Alle `print_*` Helfer (header, success, error, warning, info, fix)
- `ProgressBar`-Klasse (ASCII-basiert)
- `log_error_to_file()` Funktion
- Globales `_first_error_in_setup` Flag

**Ersetzt durch:**

- Import von `tools.ui`: `SetupConsole`, `StepProgress`, `ErrorLog`
- `ErrorLog`-Instanz in `main()` erstellt und durchgereicht
- `StepProgress` Kontextmanager in:
    - `_install_requirements_batch()` - zeigt Paket-Installation
    - `install_project_editable()` - zeigt Projekt-Installation
    - `run_tests()` - zeigt Test-Ausführung
- Alle Funktionen aktualisiert mit `SetupConsole.*` statt `print_*`
- Erweiterte Signaturen mit `log: ErrorLog` Parameter wo nötig

## Bugfixes (2025-11-23 Nachmittag)

### 1. `slots=True` Problem

**Problem:** `@dataclass(slots=True)` verhinderte das dynamische Setzen von Attributen in `__post_init__`

**Lösung:**

- Entfernt `slots=True` von `StepProgress` und `ErrorLog`
- `SetupConsole` zu normaler Klasse konvertiert (nur statische Methoden, kein State)

### 2. Progress-Bars nicht sichtbar

**Problem:** `transient=True` ließ Progress-Bars nach Abschluss verschwinden

**Lösung:**

- Geändert zu `transient=False` in `StepProgress.__enter__()`
- Progress-Bars bleiben nun sichtbar für Dokumentation des Fortschritts

### 3. Import-Analyse ohne Progress-Bar

**Problem:** `analyze_imports.py` zeigte keinen Fortschritt während import-linter lief

**Lösung:**

- Threading hinzugefügt: Linter läuft im Hintergrund
- Simulierter Progress-Bar während Linter-Ausführung
- Ausgabe erfolgt nach Abschluss

### 4. setup.log Schreibfehler

**Problem:** setup.log wurde nicht korrekt geschrieben bei Fehlern

**Lösung:**

- `ErrorLog` korrekt implementiert mit `_initialized` Flag
- `write_error()` erstellt Datei beim ersten Fehler, hängt weitere an
- Durchgereicht durch alle Funktionen die Fehler protokollieren müssen

## Vorteile

1. **Weniger Redundanz**: Ein UI/Logging-Modul für alle Tools
2. **Klarere Verantwortlichkeiten**: UI/Logging getrennt von Fachlogik
3. **Moderne Terminal-Ausgaben**: Rich bietet bessere Formatierung
4. **Bessere Wartbarkeit**: Änderungen an UI-Verhalten nur an einer Stelle
5. **Konsistenz**: Einheitliche Ausgaben über alle Tools hinweg
6. **Skalierbarkeit**: Neue Tools können einfach dieselbe UI nutzen
7. **Sichtbarer Fortschritt**: Progress-Bars zeigen Installations-Fortschritt
8. **Fehlerprotokollierung**: setup.log wird nur bei Fehlern erstellt

## Architektonische Prinzipien

- **Single Responsibility**: UI-Logik in `tools.ui`, Fachlogik in den Tools
- **DRY**: Keine Duplikation von Ausgabe-Code
- **Composition**: `ErrorLog` und `StepProgress` als wiederverwendbare Komponenten
- **Type Safety**: Vollständige Type Hints, `from __future__ import annotations`
- **Pythonic**: Kontextmanager für Ressourcen-Management (Progress-Bars)
- **Threading-Safe**: Progress-Bars funktionieren mit Hintergrund-Threads

## Kompatibilität

- **API-Stabilität**: Öffentliche APIs der Tools bleiben stabil
- **Rückwärtskompatibilität**: setup.py ruft unverändert bootstrap_env.py auf
- **Dependencies**: `rich>=13.0.0` in requirements.txt hinzugefügt

## Testing

- [x] `tools/ui.py` importierbar
- [x] `SetupConsole` Ausgaben funktional
- [x] `StepProgress` zeigt Fortschritt korrekt an (nicht transient)
- [x] `ErrorLog` schreibt korrekt in setup.log
- [x] `analyze_imports.py` läuft mit Progress-Bar
- [x] `bootstrap_env.py` zeigt Installation-Progress
- [x] setup.py komplett funktionsfähig
- [x] Keine Syntax-/Type-/Runtime-Fehler

## Nächste Schritte

Optional (nicht in diesem Refactoring):

- Erweiterte rich-Features (Tables, Syntax-Highlighting für Code)
- Konfigurierbare Verbosity-Level
- Live-Updates für lange laufende Prozesse

