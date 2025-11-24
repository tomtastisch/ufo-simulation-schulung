<!-- File: docs/dev/refactoring/tools-module-refactoring.md -->

# Refactoring des `tools/`-Moduls

Dieses Dokument beschreibt das abgeschlossene Refactoring des `tools/`-Moduls. Ziel war eine klare Trennung der
Verantwortlichkeiten, PEP-8-konforme Struktur, reduzierte Redundanz in Docstrings und eine moderne, einheitliche
Rich-basierte Terminal-UI.

---

## 1. Zielbild

Das `tools/`-Modul stellt Hilfswerkzeuge für Setup, Analyse und UI bereit, ohne Fachlogik der Simulation zu enthalten.

### 1.1 Anforderungen

- Saubere Unterteilung in eigenständige Submodule:
    - `tools.setup` für Setup-Orchestrierung und Konfiguration
    - `tools.analysis` für Import- und Datei-Analyse
    - `tools.ui` für Konsolen-UI, Progress-Bars und Textressourcen
- PEP-8-konforme Modulnamen und Ordnerstruktur
- Konsistente Modul-Dokumentation gemäß `docs/guidelines/general-gd.md`
- Zentralisiertes Logging und Fehlerprotokollierung (`setup.log`)
- Fortschrittsanzeige mit Rich-Progress-Bars für längere Operationen
- Minimale, aber aussagekräftige Docstrings in den einzelnen Dateien

### 1.2 Zielstruktur

```text
tools/
├── __init__.py              # Überblick über alle Submodule
├── setup/                   # Setup-Prozess
│   ├── __init__.py          # Setup-Dokumentation
│   ├── bootstrap.py         # Bootstrap-Orchestrierung (venv, pip, Tests)
│   ├── config.py            # BootstrapConfig, Plattform-Infos
│   └── steps.py             # Wiederverwendbare Setup-Schritte
├── analysis/                # Code-Analyse
│   ├── __init__.py          # Analyse-Dokumentation
│   ├── files.py             # Dateianalyse (AST, Pfade)
│   └── imports.py           # Import-Analyse, import-linter-Integration
└── ui/                      # UI-Komponenten
    ├── __init__.py          # UI-Dokumentation
    ├── console.py           # SetupConsole, StepProgress, ErrorLog
    └── resources/
        ├── __init__.py      # Ressourcen-Dokumentation
        ├── catalog.py       # TextCatalog (TOML-basierte Texte)
        └── text_blocks.toml # Text- und Flow-Blöcke für Setup-UI