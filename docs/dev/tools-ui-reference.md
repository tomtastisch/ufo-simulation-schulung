# Quick Reference: tools.ui

Schnelle Referenz für die Verwendung der UI-Komponenten in Setup-/Tool-Skripten.

## Import

```python
from tools.ui import SetupConsole, StepProgress, ErrorLog
```

## SetupConsole - Formatierte Ausgaben

Alle Methoden sind statisch - keine Instanziierung nötig.

```python
# Prominenter Header mit Trennlinie
SetupConsole.header("SETUP GESTARTET")

# Unter-Header in Panel
SetupConsole.subheader("Installation")

# Erfolgs-Meldung (grün, ✅)
SetupConsole.success("Installation erfolgreich")

# Fehler-Meldung (rot, ❌)
SetupConsole.error("Installation fehlgeschlagen")

# Warnung (gelb, ⚠️)
SetupConsole.warning("Bitte Konfiguration prüfen")

# Information (cyan, ℹ️)
SetupConsole.info("Starte Download...")

# Fix/Reparatur-Hinweis (blau, 🔧)
SetupConsole.fix("Konfiguriere pip Index...")
```

## StepProgress - Fortschrittsbalken

Kontextmanager für sichtbare Progress-Bars (nicht transient).

```python
# Einfache Verwendung
with StepProgress("Installiere Pakete", total=10) as progress:
    for i in range(10):
        # Mache etwas...
        progress.advance(status=f"Paket {i + 1}/10")

# Mit explizitem Schritt-Wert
with StepProgress("Verarbeite Dateien", total=100) as progress:
    for i in range(0, 100, 5):
        # Mache etwas...
        progress.advance(step=5, status=f"Bei {i}%")
```

### Threading-Kompatibilität

```python
import threading
import time

done = threading.Event()


def background_task():
    time.sleep(2)
    done.set()


thread = threading.Thread(target=background_task, daemon=True)
thread.start()

with StepProgress("Warte auf Task", total=100) as progress:
    elapsed = 0
    while not done.is_set():
        elapsed = min(95, elapsed + 5)
        progress.advance(step=5)
        time.sleep(0.1)
    progress.advance(step=100 - elapsed)

thread.join()
```

## ErrorLog - Fehlerprotokollierung

Schreibt nur bei Fehlern in Datei. Erster Fehler erstellt Datei neu, weitere werden angehängt.

```python
from pathlib import Path

# Erstelle Logger (Datei wird NICHT sofort erstellt)
log = ErrorLog(Path("setup.log"))

# Schreibe Fehler (Datei wird JETZT erstellt)
log.write_error(
    section="Installation: PyQt5",
    message="Fehler beim Installieren von PyQt5>=5.15.11",
    details=exception_stderr_output
)

# Weitere Fehler werden angehängt
log.write_error(
    section="Verifikation: pytest",
    message="Paket nicht gefunden",
    details="Package 'pytest' konnte nicht importiert werden"
)
```

### ErrorLog durch Funktionen durchreichen

```python
def install_packages(packages: dict[str, str], log: ErrorLog) -> bool:
    for name, version in packages.items():
        try:
            # Installation...
            pass
        except Exception as exc:
            log.write_error(
                f"Installation: {name}",
                f"Fehler bei {name}{version}",
                str(exc)
            )
            return False
    return True


def main() -> int:
    log = ErrorLog(Path("setup.log"))

    if not install_packages({"pytest": ">=8.0.0"}, log):
        SetupConsole.error(f"Fehler - siehe {log.path}")
        return 1

    return 0
```

## Vollständiges Beispiel

```python
#!/usr/bin/env python3
from pathlib import Path
from tools.ui import SetupConsole, StepProgress, ErrorLog


def main() -> int:
    log = ErrorLog(Path("setup.log"))

    SetupConsole.header("MEIN SETUP-TOOL")
    SetupConsole.info("Starte Installation...")

    packages = ["numpy", "pandas", "matplotlib"]

    with StepProgress("Installiere Pakete", total=len(packages)) as progress:
        for pkg in packages:
            try:
                # Simuliere Installation
                import time
                time.sleep(0.5)
                progress.advance(status=f"Installiert: {pkg}")
                SetupConsole.success(f"{pkg} installiert")
            except Exception as exc:
                log.write_error(
                    f"Installation: {pkg}",
                    f"Fehler bei {pkg}",
                    str(exc)
                )
                SetupConsole.error(f"Fehler bei {pkg}")
                return 1

    SetupConsole.header("SETUP ABGESCHLOSSEN")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
```

## Best Practices

1. **SetupConsole**: Verwende für alle User-sichtbaren Meldungen statt `print()`
2. **StepProgress**: Nutze bei bekannter Anzahl von Items (Installation, Tests, etc.)
3. **ErrorLog**: Immer in `main()` erstellen und durchreichen
4. **Threading**: StepProgress ist thread-safe, nutze für lange Hintergrund-Prozesse
5. **Fehler-Details**: Übergebe vollständige stdout/stderr an ErrorLog für Debugging

## Migrationshilfe

### Alt (ohne tools.ui)

```python
print("=" * 70)
print("  SETUP")
print("=" * 70)
print("✅ Erfolg")
print("❌ Fehler")
```

### Neu (mit tools.ui)

```python
SetupConsole.header("SETUP")
SetupConsole.success("Erfolg")
SetupConsole.error("Fehler")
```

### Alt (eigener Progress-Bar)

```python
for i, item in enumerate(items):
    percent = int((i / len(items)) * 100)
    print(f"\r[{'█' * i}{'░' * (len(items)-i)}] {percent}%", end="")
```

### Neu (StepProgress)

```python
with StepProgress("Verarbeite Items", total=len(items)) as progress:
    for item in items:
        # ... verarbeite item ...
        progress.advance(status=f"Item: {item}")
```

