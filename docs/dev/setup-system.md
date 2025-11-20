# Setup-System – Entwickler-Dokumentation

Diese Dokumentation beschreibt das Setup-System (`tools/bootstrap_env.py`) und dient als Referenz für Entwickler.

---

## Übersicht

Das Setup-System automatisiert die Projekt-Einrichtung für Schüler und besteht aus:

- **Entry Point**: `setup.py` (Wrapper für `tools/bootstrap_env.py`)
- **Hauptlogik**: `tools/bootstrap_env.py` (komplettes Setup-System)
- **Output**: `setup.log` (nur bei Fehlern)
- **Tests**: `tests/test_progress_bar.py`, `tests/test_error_log.py`

---

## Architektur

### Komponenten

```
┌─────────────┐
│  setup.py   │  ← Entry Point (ruft bootstrap_env.py auf)
└──────┬──────┘
       │
       v
┌────────────────────────┐
│ bootstrap_env.py       │  ← Hauptlogik
├────────────────────────┤
│ - ProgressBar          │  ← UI-Komponente
│ - install_*()          │  ← Installations-Funktionen
│ - run_tests()          │  ← Test-Ausführung
│ - log_error_to_file()  │  ← Error-Logging
└────────────────────────┘
       │
       v
┌────────────────────────┐
│    setup.log           │  ← Output (nur bei Fehlern)
└────────────────────────┘
```

### Design-Prinzipien

1. **Minimale Ausgabe**: Progress-Bars statt vollständiger Logs
2. **Error-Only Logging**: `setup.log` nur bei Fehlern
3. **Thread-Safety**: Background-Threads für lange Operationen
4. **Keine externen Dependencies**: Nur stdlib
5. **Testbarkeit**: Alle Komponenten getestet

---

## Features

### 1. Progress-Bar-System

#### Klasse: `ProgressBar`

```python
class ProgressBar:
    """Einfacher ASCII-Progress-Bar für Terminal-Ausgabe.
    
    Thread-sicher durch stdout-Lock.
    """
    
    def __init__(self, width: int = 24):
        """Initialisiert Progress-Bar mit gegebener Breite."""
        
    def update(self, percent: int, status: str = "") -> None:
        """Aktualisiert Progress-Bar auf given Prozent mit Status-Text."""
        
    def finish(self, message: str = "✓ Fertig") -> None:
        """Beendet Progress-Bar mit 100% und Nachricht."""
```

#### Verwendung

```python
progress = ProgressBar()
progress.update(0, "Starte Installation...")
progress.update(50, "Installiere Package...")
progress.finish("✓ Installation abgeschlossen")
```

#### Output

```
   [████████████░░░░░░░░░░░░] 50% Installiere Package...
   [████████████████████████] 100% ✓ Installation abgeschlossen
```

---

### 2. Error-Only Logging

#### Funktion: `log_error_to_file()`

```python
def log_error_to_file(
    log_file: Path,
    section: str,
    error_info: str,
    details: str = ""
) -> None:
    """Schreibt Fehlerinformationen in Log-Datei (nur bei Fehlern).
    
    Args:
        log_file: Pfad zur Log-Datei
        section: Abschnittsname (z.B. "Runtime-Dependency: numpy")
        error_info: Kurze Fehlerbeschreibung
        details: Detaillierte Fehlerinformationen (stdout/stderr)
    """
```

#### Verhalten

- **Bei erstem Fehler**: Erstellt `setup.log` mit Header
- **Bei weiteren Fehlern**: Appendet an existierende Datei
- **Bei Erfolg**: Keine Datei, keine Ausgabe

#### Log-Format

```
# Setup Error Log
# Nur Fehler werden hier protokolliert

======================================================================
[2025-11-20 14:35:22] FEHLER: Runtime-Dependency: numpy
======================================================================
subprocess.CalledProcessError: Command '...' returned non-zero exit status 1

Details:
ERROR: Could not find a version that satisfies the requirement numpy...
...
```

---

### 3. Installation mit Progress-Bars

#### Funktion: `install_project_editable()`

Installiert Projekt im Editable-Modus mit Progress-Bar.

```python
def install_project_editable(
    venv_python: Path,
    log_file: Path
) -> bool:
    """Installiert Projekt im Editable-Modus mit Progress-Bar.
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
```

**Ablauf**:

1. Startet `pip install -e .` in Background-Thread
2. Zeigt Progress-Bar mit simulierten Phasen:
    - 20%: Prüfe Build-Backend
    - 40%: Ermittle Requirements
    - 60%: Erstelle Metadata
    - 80%: Installiere Package
    - 95%: Finalisiere Installation
3. Wartet auf Thread-Completion
4. Bei Fehler: Loggt in `setup.log`

**Warum simulierte Phasen?**

- Pip gibt keinen strukturierten Progress-Output
- Simulation basiert auf bekannten Build-Phasen
- Gibt Schülern Feedback dass etwas passiert

---

### 4. Test-Ausführung mit Progress-Bar

#### Funktion: `run_tests()`

Führt pytest mit Progress-Bar aus.

```python
def run_tests(
    venv_python: Path,
    log_file: Path,
    skip_tests: bool = False
) -> bool:
    """Führt pytest mit Progress-Bar aus.
    
    Args:
        venv_python: Pfad zur Python-Binary im venv
        log_file: Pfad zur Log-Datei (für Fehler)
        skip_tests: Flag zum Überspringen der Tests
        
    Returns:
        True bei Erfolg (alle Tests passed), False bei Fehler
    """
```

**Ablauf**:

1. Startet `pytest -v` in Background-Thread
2. Zeigt Progress-Bar während Tests laufen
3. Extrahiert Test-Zusammenfassung aus Output
4. Zeigt nur Zusammenfassung (nicht jeden einzelnen Test)
5. Bei Fehlern: Zeigt letzte 5 relevante Zeilen

**Output bei Erfolg**:

```
🧪 Führe Tests aus (Validierung der Installation)
==================================================

   ℹ️  pytest Version: pytest 9.0.1

Starte Tests...

   [████████████████████████] 100% ✓ Tests abgeschlossen

   ✅ Alle Tests erfolgreich: 12 passed in 2.45s
```

**Output bei Fehlern**:

```
   [████████████████████████] 100% ✓ Tests abgeschlossen

   ⚠️  Einige Tests sind fehlgeschlagen (Exit-Code: 1)

📊 Test-Zusammenfassung:
   FAILED tests/test_example.py::test_something - AssertionError
   12 passed, 1 failed in 2.50s
```

---

## Hilfsfunktionen

### `extract_subprocess_error_details(exc: CalledProcessError) -> str`

Extrahiert stdout und stderr aus `CalledProcessError`.

```python
def extract_subprocess_error_details(exc: subprocess.CalledProcessError) -> str:
    """Extrahiert Fehlerdetails aus CalledProcessError (stdout + stderr).
    
    Nutzt hasattr() für sichere Attribut-Checks.
    """
```

**Verwendung**:

```python
try:
    subprocess.run([...], check=True)
except subprocess.CalledProcessError as exc:
    details = extract_subprocess_error_details(exc)
    log_error_to_file(log_file, "Section", str(exc), details)
```

---

### `get_error_message(exc: CalledProcessError) -> str`

Gibt lesbare Fehlermeldung zurück (bevorzugt stderr).

```python
def get_error_message(exc: subprocess.CalledProcessError) -> str:
    """Gibt lesbare Fehlermeldung zurück (bevorzugt stderr, Fallback str(exc))."""
```

---

### `_extract_test_summary(stdout: str) -> str | None`

Extrahiert Test-Zusammenfassung aus pytest-Output (z.B. "12 passed in 2.45s").

**Private Funktion** (führendes `_`).

---

### `_extract_test_failure_summary(stdout: str) -> list[str]`

Extrahiert Fehler-Zusammenfassung aus pytest-Output (nur FAILED/ERROR Zeilen).

**Private Funktion** (führendes `_`).

---

## Setup-Ablauf

### Vollständiger Workflow

```
1. setup.py gestartet
   ↓
2. bootstrap_env.py::main()
   ↓
3. check_python_version()          ← Prüft Python >= 3.11
   ↓
4. create_venv()                   ← Erstellt .venv/
   ↓
5. update_pip()                    ← pip, setuptools, wheel
   ↓
6. ensure_pip_index_url()          ← PyPI Index konfigurieren
   ↓
7. install_runtime_requirements()  ← requirements.txt + Progress-Bar
   ↓
8. install_dev_requirements()      ← dev-requirements + Progress-Bar
   ↓
9. install_project_editable()      ← pip install -e . + Progress-Bar
   ↓
10. verify_installation()          ← Import-Test
   ↓
11. run_tests()                    ← pytest + Progress-Bar
   ↓
12. print_next_steps()             ← Anleitung für Schüler
```

### Fehlerbehandlung

- **Jeder Schritt hat Try-Except**
- **Bei Fehler**: `log_error_to_file()` schreibt Details
- **Return False**: Setup bricht ab
- **setup.log** enthält vollständige Fehlerinformationen

---

## Kommandozeilen-Optionen

### `--skip-tests`

Überspringt Test-Ausführung (für schnellere Installation).

```bash
python setup.py --skip-tests
# oder
python tools/bootstrap_env.py --skip-tests
```

**Verwendung**:

- CI/CD wo Tests separat laufen
- Entwickler die Tests manuell ausführen wollen
- Schnelle Iteration während Entwicklung

---

## Troubleshooting

### Problem: setup.log wird nicht erstellt

**Ursache**: Kein Fehler während Setup  
**Lösung**: Das ist gewollt! setup.log wird nur bei Fehlern erstellt.

### Problem: setup.log wird bei jedem Setup überschrieben

**Ursache**: Nicht mehr zutreffend (Error-Only Logging seit 2025-11-20)  
**Lösung**: setup.log wird nur noch bei Fehlern beschrieben, nicht überschrieben.

### Problem: Progress-Bar "hängt" bei 80%

**Ursache**: Pip-Installation dauert länger als erwartet  
**Lösung**:

- Prüfe Netzwerk-Verbindung
- Prüfe ob pip-Index erreichbar ist
- Warte ab (kann bei großen Packages dauern)
- Falls wirklich hängt: Strg+C und setup.log prüfen

### Problem: Tests schlagen fehl nach erfolgreichem Setup

**Ursache**: Mögliche Probleme in Projekt-Code  
**Lösung**:

1. Prüfe vollständige Test-Ausgabe: `pytest -v`
2. Prüfe ob alle Dependencies installiert: `pip list`
3. Prüfe Python-Version: `python --version`
4. Prüfe setup.log auf Warnungen

---

## Tests

### test_progress_bar.py

Testet `ProgressBar`-Klasse:

- Initialisierung
- Update mit verschiedenen Prozenten
- Finish-Methode
- Edge-Cases (0%, 100%, >100%)

```bash
pytest tests/test_progress_bar.py -v
```

### test_error_log.py (geplant)

Testet Error-Logging:

- Log-Datei-Erstellung bei erstem Fehler
- Append bei weiteren Fehlern
- Korrekte Formatierung
- Timestamp-Format

---

## Best Practices

### Für Entwickler

- ✅ **Vor Änderungen**: Tests durchlesen
- ✅ **Nach Änderungen**: Tests aktualisieren
- ✅ **Neue Features**: Progress-Bar-Pattern beibehalten
- ✅ **Error-Handling**: Immer `log_error_to_file()` nutzen
- ✅ **Threading**: Background-Threads für lange Operationen

### Für Code-Reviews

- ✅ Prüfe ob Error-Logging korrekt ist
- ✅ Prüfe ob Progress-Bars sinnvolle Phasen zeigen
- ✅ Prüfe ob Thread-Safety gewährleistet ist
- ✅ Prüfe ob Tests aktualisiert wurden

---

## Siehe auch

- **Changelog**: [CHANGELOG.md](CHANGELOG.md) – Historie aller Änderungen
- **Schüler-Anleitung**: [docs/description/setup-guide.md](../description/setup-guide.md)
- **Testing Tools**: [TESTING_TOOLS.md](TESTING_TOOLS.md)

---

**Hinweis**: Diese Dokumentation richtet sich an Entwickler, nicht an Schüler. Für Schüler siehe
`docs/description/setup-guide.md`.

