# Setup & Configuration – Richtlinie

## Zweck von `setup.py`

`setup.py` dient ausschließlich als Minimal-Schnittstelle zu `setuptools`, damit Werkzeuge wie `pip install -e .` oder
CI-Pipelines das Projekt paketieren können. Die eigentliche Umgebungskonfiguration (Virtual Environment,
Paketinstallation, Verifikation) liegt bewusst in `tools/bootstrap_env.py`, damit der CLI-Workflow und die
Packaging-Schnittstelle sauber getrennt bleiben.

## Aufgaben & Pflichten

- stellt sicher, dass Packaging-Tools ein gültiges `setup()`-Entry-Point vorfinden.
- darf keine Infrastruktur- oder Installationslogik enthalten (kein venv-Anlegen, keine Paket-Downloads).
- verweist in der Modul-Docstring klar auf das Bootstrap-Skript.
- bleibt stabil, damit bestehende Automatisierungen („editable installs“) nicht brechen.

## Ablauf (Packaging-Sicht)

**Kurzbeschreibung:** `setup.py` startet nur `setuptools.setup()` mit der Konfiguration aus `pyproject.toml`.

**Schritte:**

- Interpreter ruft `setup.py` auf (z. B. durch `pip install -e .`).
- Datei importiert `setuptools.setup`.
- `setup()` liest sämtliche Metadaten aus `pyproject.toml` ein.
- Build-Backend (`setuptools.build_meta`) verarbeitet die dort hinterlegten Optionen (`tool.setuptools*`).

## Requirements-Verwaltung & dynamisches Laden

- Die vollständige Runtime-Abhängigkeitsliste liegt ausschließlich in `requirements.txt`.
- `pyproject.toml` deklariert `[tool.setuptools.dynamic] dependencies = { file = ["requirements.txt"] }`.
- Beim Aufruf von `setup()` lädt `setuptools` diese Datei dynamisch und erzeugt daraus die `project.dependencies`.
- Vorteil: `requirements.txt` ist „Single Source of Truth“ für Runtime-Pakete (Setup-Skript, CI, Docker, Entwickler:
  innen).
- `setup.py` darf daher **nicht** versuchen, eigenständig Dependencies zu parsen – das geschieht zentral durch den
  Build-Backend-Mechanismus.

## Verhältnis zu `tools/bootstrap_env.py`

- `setup.py` → Packaging-Stubs, keine Seiteneffekte.
- `tools/bootstrap_env.py` → ausführbares CLI, das Virtual Environments erstellt, `requirements.txt` installiert,
  Dev-Extras aus `[project.optional-dependencies].dev` einliest und den Erfolg prüft.
- Beide Komponenten greifen auf dieselben Artefakte (`pyproject.toml`, `requirements.txt`) zu, jedoch in klar getrennten
  Rollen (Packaging vs. Provisioning).

## Wrapper-Skript

- Schüler:innen starten ausschließlich `python setup.py`; das Skript entscheidet intern, ob der Bootstrap (
  `tools/bootstrap_env.py`) oder der setuptools-Shim aktiv ist.
- Kein separates Wrapper-Verzeichnis notwendig; `setup.py` liegt im Projektwurzelverzeichnis und kapselt beide Pfade.
- Dokumentation verweist nur auf `python setup.py` als Einstiegsbefehl.

## Mindestanforderungen für Änderungen an `setup.py`

1. Änderungen nur vornehmen, wenn Packaging-Anforderungen sich ändern (z. B. neuer Build-Backend, zusätzliche
   Metadaten).
2. Nach jeder Änderung sicherstellen, dass `pip install -e .` weiterhin ohne Zusatzschritte funktioniert.
3. Keine Logik ergänzen, die `pip` im Build-Sandkasten scheitern lassen könnte (z. B. Netzwerkzugriffe, `sys.exit`
   -Aufrufe außerhalb von `setup()`).
