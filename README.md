# 🛸 UFO-Simulation Schulung

Eine interaktive **UFO/Drohnen-Simulation** mit Clean Architecture für Anfänger zum Lernen von **Autopilot-Programmierung**.

**Besonderheiten:**
- ✅ Realistische 3D-Physik-Simulation mit NumPy
- ✅ PyQt5-basierte Visualisierung
- ✅ Clean Architecture (State Manager, Physics Engine, etc.)
- ✅ Schulungsfreundlich: Demo + Schüler-Template getrennt
- ✅ Keine Code-Ablenkung für Schüler (3 leere Funktionen + 1 Flag)
- ✅ Moderne Python 3.11+ Features (type hints, dataclasses, etc.)

---

## ⚡ Quick Start (5 Schritte)

```bash
# 1️⃣  Einziger Befehl für Setup! (Alles wird automatisch konfiguriert)
python setup.py

# 2️⃣  Demo anschauen
python -m ufo_simulation.ufo_main

# 3️⃣  Implementieren in ufo_simulation/autopilot.py:
#     - takeoff()  - Startphase
#     - cruise()   - Reiseflug  
#     - landing()  - Landephase

# 4️⃣  Setze USE_DEMO = False in autopilot.py

# 5️⃣  Testen! Starte Demo erneut
python -m ufo_simulation.ufo_main
```

**Das war's!** 🚀 Nach `setup.py` funktioniert alles automatisch.

---

## 🚀 Installation (Detailliert)

### Voraussetzungen
- **Python 3.11 oder höher** (für moderne Language Features)
- pip

### Python-Version prüfen

```bash
python --version
# Output: Python 3.11.x oder höher erforderlich
```

Falls du noch Python 3.10 oder älter hast, aktualisiere bitte zu [Python 3.11+](https://www.python.org/downloads/).

### Automatisches Setup

```bash
# Repository klonen
git clone https://github.com/tomtastisch/ufo-simulation-schulung.git
cd ufo-simulation-schulung

# Setup-Script ausführen (EINZIGER Befehl!)
python setup.py

# Folge den Anweisungen am Bildschirm
```

Das Script macht automatisch:
- ✅ Prüft Python 3.11+
- ✅ Erstellt Virtual Environment
- ✅ Konfiguriert pip richtig
- ✅ Installiert PyQt5 & NumPy
- ✅ Prüft die Installation
- ✅ Zeigt nächste Schritte

**Falls Fehler:** Siehe [Troubleshooting](#🆘-troubleshooting) unten.

---

## 🎮 Demo starten

Nach erfolgreichem Setup:

```bash
# Aktiviere das Virtual Environment (falls nicht aktiv)
source .venv/bin/activate  # Linux/macOS
# oder
.venv\Scripts\activate     # Windows

# Starte Demo (UFO fliegt automatisch)
python -m ufo_simulation.ufo_main
```

Das UFO fliegt automatisch zum Ziel und landet. `USE_DEMO = True` in `autopilot.py`.

---

## 📚 Aufgabenstellung für Schüler

### Deine Mission: Autopilot programmieren

Das UFO soll **automatisch fliegen** können. Du musst 3 Funktionen implementieren:

[... REST wie vorher ...]