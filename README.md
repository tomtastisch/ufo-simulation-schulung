# 🛸 UFO-Simulation Schulung

Eine interaktive **UFO/Drohnen-Simulation** mit Clean Architecture zum Lernen von **Autopilot-Programmierung** in
Python.

**Für Schüler**: Lerne Programmierung anhand einer realistischen 3D-Physik-Simulation mit PyQt5-Visualisierung.

---

## ⚡ Quick Start

```bash
# 1. Setup (einziger Befehl!)
python setup_v2.py

# 2. Demo anschauen
python -m core.simulation.ufo_main

# 3. Autopilot programmieren (simulation/autopilot.py)
#    - takeoff()  → Startphase
#    - cruise()   → Reiseflug  
#    - landing()  → Landephase

# 4. Eigenen Code aktivieren
#    Setze USE_DEMO = False in autopilot.py

# 5. Testen!
python -m core.simulation.ufo_main
```

**Das war's!** 🚀

---

## 🎯 Deine Mission

Programmiere einen **Autopiloten**, der das UFO:

- ✈️ Automatisch starten lässt
- 🎯 Zum Ziel fliegen lässt
- 🛬 Sicher landen lässt

Du implementierst nur **3 Funktionen** – den Rest erledigt die Simulation für dich!

---

## 📚 Dokumentation

### Für Schüler

- **[Setup-Anleitung](docs/description/setup-anleitung.md)** – Projekt einrichten
- **[Schulungsablauf](docs/description/schulungsablauf.md)** – Übersicht der Schulung
- **Aufgaben** – Schritt-für-Schritt Anleitungen (folgen)

### Für Entwickler

- **[Changelog](docs/dev/changelog.md)** – Änderungshistorie
- **[Setup-System](docs/dev/setup-system.md)** – Setup-Dokumentation
- **[Testing-Tools](docs/dev/temp/testing-tools.md)** – Testing und Debugging

### Architektur & Planung

- **[Architektur-Spezifikationen](docs/specs/architecture/)** – System-Design
- **[Implementierungsstatus](docs/planning/implementation-status.md)** – Ticket-Tracking
- **[Coding-Guidelines](docs/guidelines/general-gd.md)** – Code-Standards

---

## 🚀 Installation

### Voraussetzungen

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- pip (kommt mit Python)

### Setup ausführen

```bash
git clone https://github.com/tomtastisch/ufo-simulation-schulung.git
cd ufo-simulation-schulung
python setup_v2.py
```

Das Setup:
- ✅ Erstellt Virtual Environment
- ✅ Installiert alle Abhängigkeiten (PyQt5, NumPy)
- ✅ Führt automatisch Tests aus
- ✅ Zeigt Fortschritt mit Progress-Bar

**Bei Problemen**: Siehe [Setup-Anleitung](docs/description/setup-anleitung.md)

---

## ⚠️ Häufige Probleme

**Setup schlägt fehl**
```bash
# Prüfe setup.log für Details
cat setup.log
```

**Python-Version zu alt**
```bash
python --version  # Muss 3.11+ sein
```

**Virtual Environment aktivieren**

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

**Weitere Hilfe**: [Setup-Anleitung](docs/description/setup-anleitung.md)

---

## 🎓 Projekt-Features

- **Realistische Physik**: 3D-Vektorrechnung mit NumPy
- **PyQt5-GUI**: Live-Visualisierung der Simulation
- **Clean Architecture**: State Manager, Physics Engine, Command Pattern
- **Schulungsfreundlich**: Demo-Implementierung als Referenz
- **Type-Safe**: Vollständige Type Hints (Python 3.11+)
- **Getestet**: Automatische Tests validieren Installation

---

## 📖 Lizenz & Copyright

Copyright (C) 2013-2025 R. Gold, tomtastisch (i-ki 1)

**Version**: 5.2.0-tw-refactored

---

**Viel Erfolg beim Programmieren! 🚀**

