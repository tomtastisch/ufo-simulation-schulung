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
python -m simulation.ufo_main

# 3️⃣  Implementieren in simulation/autopilot.py:
#     - takeoff()  - Startphase
#     - cruise()   - Reiseflug  
#     - landing()  - Landephase

# 4️⃣  Setze USE_DEMO = False in autopilot.py

# 5️⃣  Testen! Starte Demo erneut
python -m simulation.ufo_main
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

**Falls Fehler:** Siehe [Troubleshooting](#troubleshooting) unten.

---

## 🎮 Demo starten

Nach erfolgreichem Setup:

```bash
# Aktiviere das Virtual Environment (falls nicht aktiv)
source .venv/bin/activate  # Linux/macOS
# oder
.venv\Scripts\activate     # Windows

# Starte Demo (UFO fliegt automatisch)
python -m simulation.ufo_main
```

Das UFO fliegt automatisch zum Ziel und landet. `USE_DEMO = True` in `autopilot.py`.

---

## 📚 Aufgabenstellung für Schüler

### Deine Mission: Autopilot programmieren

Das UFO soll **automatisch fliegen** können. Du musst 3 Funktionen implementieren:

- `takeoff()` - Das UFO startet und gewinnt Höhe.
- `cruise()` - Das UFO fliegt mit konstanter Geschwindigkeit und Höhe.
- `landing()` - Das UFO landet sicher.

**Tipps:**
- Nutze die bereitgestellten Hilfsfunktionen in `simulation/utils.py`.
- Sieh dir die Demo-Implementierung in `simulation/autopilot_demo.py` an.

Viel Erfolg! 🚀

---

## 🚧 Refactor: T3 — `UfoState` extraction (2025-11-19)

Im Rahmen des Refactorings wurde der Simulationszustand (`UfoState`) in ein eigenes Paket ausgelagert
und gleichzeitig die Visualisierungslogik entkoppelt:

- `UfoState` wurde nach `src/core/simulation/state/state.py` verschoben und als immutable (`frozen=True`) dataclass definiert.
- Für Rückwärtskompatibilität wurde ein `StateProxy` eingeführt: alte Skripte, die `sim.state.delta_v = ...` verwenden,
  funktionieren weiterhin — intern werden Änderungen immutable über `StateManager.update_state()` angewendet.
- Die PyQt-basierten GUI-Komponenten wurden in `src/core/simulation/view.py` ausgelagert und werden nur geladen,
  wenn `sim.start(show_view=True)` aufgerufen wird (lazy import). Das erleichtert Headless-Tests.

Kurz: API bleibt kompatibel, State ist jetzt immutable (sicherer), GUI ist lazy-loaded.

### Schnelltests (lokal)

```bash
# 1) Virtualenv aktivieren
source .venv/bin/activate

# 2) Unit-Tests laufen lassen
pytest -q

# 3) Headless demo (Autopilot)
python - <<'PY'
from task.autopilot import Autopilot
from core.simulation.ufosim import UfoSim
sim = UfoSim()
ap = Autopilot()
sim.start(speedup=1, destinations=[(10.0,0.0)], show_view=False, enable_logging=True, log_every_step=False, autopilot_callback=ap)
PY

# 4) Voller Demo mit GUI (erfordert PyQt5 and X11/Window system)
python -m core.simulation.ufo_main
```

---

## Troubleshooting

Hier einige häufige Probleme und Lösungen:

- **Problem:** Python 3.11 nicht installiert
    - **Lösung:** [Python 3.11+ herunterladen und installieren](https://www.python.org/downloads/)

- **Problem:** Fehler bei der Ausführung von `setup.py`
    - **Lösung:** Stelle sicher, dass du die neuesten Versionen von `pip` und `setuptools` hast:
      ```bash
      python -m pip install --upgrade pip setuptools
      ```

- **Problem:** PyQt5 oder NumPy installieren fehlgeschlagen
    - **Lösung:** Überprüfe deine Internetverbindung und versuche es erneut.

- **Problem:** Demo startet nicht
    - **Lösung:** Stelle sicher, dass das Virtual Environment aktiviert ist.

Für weitere Hilfe, konsultiere die [Dokumentation](https://github.com/tomtastisch/ufo-simulation-schulung) oder
kontaktiere den Support.
