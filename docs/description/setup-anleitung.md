# Setup-Anleitung – UFO-Simulation Schulung

Diese Anleitung hilft dir, die UFO-Simulation auf deinem Computer einzurichten.

---

## Schnellstart

### 1. Python-Version prüfen

Du benötigst Python 3.11 oder neuer. Prüfe deine Version:

```bash
python --version
# oder
python3 --version
```

Wenn deine Version älter als 3.11 ist, lade die neueste Version von [python.org](https://www.python.org/downloads/)
herunter.

---

### 2. Setup ausführen

Öffne ein Terminal im Projekt-Ordner und führe aus:

```bash
python setup.py
```

Das Setup führt automatisch folgende Schritte durch:

1. ✅ Prüft Python-Version
2. 📦 Erstellt Virtual Environment (`.venv`)
3. ⬆️ Aktualisiert pip
4. 📥 Installiert alle benötigten Pakete
5. 📦 Installiert das Projekt
6. 🧪 Führt Tests aus
7. 🎉 Zeigt nächste Schritte an

---

## Was passiert während des Setups?

### Progress-Bars

Statt langer technischer Ausgaben siehst du übersichtliche Progress-Bars:

```
📥 Installiere Runtime-Dependencies (aus requirements.txt)...

   [████████████████████████░░░░░░░░] 60% Installiere numpy...
   [████████████████████████████████] 100% ✓ Installation abgeschlossen
```

Das macht es einfacher zu sehen, was gerade passiert!

### Automatische Tests

Nach der Installation werden automatisch Tests ausgeführt:

```
🧪 Führe Tests aus (Validierung der Installation)
==================================================

   ℹ️  pytest Version: pytest 9.0.1

Starte Tests...

   [████████████████████████████████] 100% ✓ Tests abgeschlossen

   ✅ Alle Tests erfolgreich: 12 passed in 2.45s
```

Wenn alle Tests bestehen (grünes ✅), ist dein Setup korrekt!

---

## Nächste Schritte nach erfolgreichem Setup

### Virtual Environment aktivieren

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Du siehst dann `(.venv)` vor deiner Kommandozeile.

### Simulation starten

```bash
python src/core/simulation/ufo_main.py
```

Ein Fenster mit der UFO-Simulation öffnet sich!

### Schulungsaufgaben durcharbeiten

Die Schulungsaufgaben findest du im Ordner `docs/description/`. Beginne mit:

1. [Winkelberechnung](task/angle-calculation.md) (Task 1)
2. [Autopilot](task/autopilot.md) (Task 2)

---

## Probleme beheben

### Setup schlägt fehl

Wenn das Setup fehlschlägt, wurde eine Datei `setup.log` erstellt.

**Was tun?**

1. Öffne die Datei `setup.log` (im Projekt-Ordner)
2. Lies die Fehlermeldung
3. Frage deinen Lehrer um Hilfe und zeige ihm die Datei

**Häufige Probleme:**

#### "Python-Version zu alt"

```
❌ Python 3.11 oder neuer wird benötigt. Gefunden: 3.10.5
```

**Lösung:** Installiere Python 3.11 oder neuer von [python.org](https://www.python.org/downloads/)

#### "pip install fehlgeschlagen"

```
ERROR: Could not find a version that satisfies the requirement numpy...
```

**Lösung:**

1. Prüfe deine Internetverbindung
2. Versuche es erneut: `python setup.py`
3. Frage deinen Lehrer

---

### Tests schlagen fehl

Wenn Tests nach dem Setup fehlschlagen:

```
⚠️  Einige Tests sind fehlgeschlagen (Exit-Code: 1)

📊 Test-Zusammenfassung:
   FAILED tests/test_example.py::test_something
   12 passed, 1 failed in 2.50s
```

**Was tun?**

1. Das Setup ist trotzdem funktionsfähig (du kannst weitermachen)
2. Informiere deinen Lehrer über die fehlgeschlagenen Tests
3. Er kann prüfen, ob das ein Problem ist

---

### Virtual Environment aktivieren funktioniert nicht

**Windows:**

Wenn du diese Fehlermeldung siehst:

```
Die Ausführung von Skripts ist auf diesem System deaktiviert.
```

**Lösung (nur einmalig nötig):**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Danach kannst du `.venv\Scripts\activate` ausführen.

**macOS/Linux:**

Wenn `source .venv/bin/activate` nicht funktioniert:

```bash
. .venv/bin/activate
```

(Mit einem Punkt statt `source`)

---

### Simulation startet nicht

Wenn `python src/core/simulation/ufo_main.py` nicht funktioniert:

1. **Ist das Virtual Environment aktiviert?**
    - Siehst du `(.venv)` vor deiner Kommandozeile?
    - Wenn nicht: Aktiviere es (siehe oben)

2. **Bist du im richtigen Ordner?**
   ```bash
   pwd  # macOS/Linux
   cd   # Windows
   ```
   Du solltest im Projekt-Hauptordner sein (dort wo `setup.py` liegt)

3. **Frage deinen Lehrer** und zeige ihm:
    - Was du eingegeben hast
    - Die Fehlermeldung

---

## Tests manuell ausführen

Falls du Tests manuell ausführen möchtest:

```bash
# Virtual Environment muss aktiviert sein!
pytest -v
```

Das zeigt alle Tests einzeln an.

---

## Hilfreiche Befehle

### Projekt neu installieren

Falls etwas kaputt gegangen ist:

```bash
# Virtual Environment löschen
rm -rf .venv  # macOS/Linux
rmdir /s .venv  # Windows

# Setup neu ausführen
python setup.py
```

### Installierte Pakete anzeigen

```bash
# Virtual Environment muss aktiviert sein!
pip list
```

### Python-Version im Virtual Environment prüfen

```bash
# Virtual Environment muss aktiviert sein!
python --version
```

---

## Für Fortgeschrittene

### Tests überspringen

Falls du das Setup schneller durchführen möchtest (ohne Tests):

```bash
python setup.py --skip-tests
```

**Hinweis:** Nur nutzen wenn du weißt was du tust!

### Vollständige Installation-Logs

Alle Details der Installation werden in `setup.log` gespeichert (nur bei Fehlern).

Bei erfolgreichem Setup gibt es keine `setup.log` Datei.

---

## Zusammenfassung

1. **Python 3.11+** installieren
2. **`python setup.py`** ausführen
3. **Virtual Environment aktivieren** (`.venv\Scripts\activate` oder `source .venv/bin/activate`)
4. **Simulation starten** (`python src/core/simulation/ufo_main.py`)
5. **Schulungsaufgaben bearbeiten**

Bei Problemen: **Lehrer fragen** und `setup.log` zeigen (falls vorhanden)!

---

**Viel Erfolg bei der Schulung! 🚀**

