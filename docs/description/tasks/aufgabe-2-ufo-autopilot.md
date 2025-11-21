# Aufgabe 2 – UFO-Autopilot

Praktikumsaufgabe zur autonomen Steuerung einer Lieferdrohne: Implementiere einen Autopiloten für Start, Flug und
Landung.

---

## Überblick

In dieser Aufgabe erstellst du die autonome Steuerung (Autopilot) für eine Lieferdrohne (UFO). Das UFO wird simuliert
und du programmierst die Steuerlogik.

### Ziel

Das UFO soll autonom von `(0.0, 0.0, 0.0)` zu einem beliebigen Zielpunkt `(x, y, 0.0)` fliegen und dabei eine bestimmte
Flughöhe `z` einhalten.

**Wichtig**: Das UFO startet und landet immer auf Höhe `0.0`.

### Flugphasen

Der Flug gliedert sich in drei Phasen:

1. **Takeoff** (Start): Von `(0.0, 0.0, 0.0)` auf `(0.0, 0.0, z)`
2. **Cruise** (Reiseflug): Von `(0.0, 0.0, z)` zu `(x, y, z)`
3. **Landing** (Landung): Von `(x, y, z)` zu `(x, y, 0.0)`

### Visualisierung

```
    (x, y, z) ← Cruise → (0.0, 0.0, z)
        ↓                      ↑
    Landing                Takeoff
        ↓                      ↑
    (x, y, 0.0)          (0.0, 0.0, 0.0)
```

**Beispiel**: `x=20.0, y=20.0, z=10.0`

---

## Voraussetzungen

### Benötigte Dokumente

- **UFO-Handbuch**: Lies dies zum Verständnis der Simulation
- **Aufgabe 1**: Winkelberechnung (wird hier wiederverwendet)

### Vorgegebene Dateien

Folgende Dateien werden bereitgestellt:

- `ufo_autopilot.py` (Vorlage mit Funktionsgerüst)
- `ufo_main.py` (Hauptprogramm-Vorlage)
- `pa2_utest.py` (Unit-Test-Skript)

**Download**: Alle Dateien von Moodle herunterladen

---

## Aufgabenstellung

### Teil 1: Vorgegebene Funktionen (nicht ändern!)

In `ufo_autopilot.py` sind bereits vier Funktionen vorgegeben, die **nicht geändert** werden müssen:

#### 1. `fly_to(sim, x: float, y: float, z: float) -> None`

**Parameter**:

- `sim`: Referenz auf die Simulation
- `x, y`: Zielpunkt im kartesischen Koordinatensystem
- `z`: Flughöhe

**Funktion**: Fliegt das UFO von der aktuellen Position zum Ziel durch Aufruf von:

1. `takeoff(sim, z)`
2. `cruise(sim, x, y)`
3. `landing(sim)`

#### 2. `takeoff(sim, z: float) -> None`

**Parameter**:

- `sim`: Referenz auf die Simulation
- `z`: Ziel-Flughöhe

**Funktion**: Lässt das UFO auf die Flughöhe `z` steigen

#### 3. `cruise(sim, x: float, y: float) -> None`

**Parameter**:

- `sim`: Referenz auf die Simulation
- `x, y`: Zielpunkt

**Funktion**: Fliegt zum Zielpunkt auf gleicher Höhe

#### 4. `landing(sim) -> None`

**Parameter**:

- `sim`: Referenz auf die Simulation

**Funktion**: Lässt das UFO auf Höhe `0.0` landen

---

## Teil 2: Zu implementierende Funktionen

Implementiere die folgenden Funktionen in `ufo_autopilot.py`:

### a) `distance(x1: float, y1: float, x2: float, y2: float) -> float`

**Parameter**: Zwei Punkte `(x1, y1)` und `(x2, y2)` im kartesischen Koordinatensystem

**Rückgabewert**: Abstand zwischen den beiden Punkten (Fließkommazahl)

**Zweck**: Wird benötigt, um rechtzeitig vor dem Ziel abzubremsen

**Hinweis**: Nutze den Satz des Pythagoras

---

### b) `angle_q1(x1: float, y1: float, x2: float, y2: float) -> float`

**Parameter**: Zwei Punkte `(x1, y1)` und `(x2, y2)` mit **x2 ≥ x1** und **y2 ≥ y1**

**Rückgabewert**: Winkel φ in Grad, `0° ≤ φ ≤ 90°`

**Implementierung**:

#### Wiederverwendung aus Aufgabe 1

Diese Funktion ist **genau** das, was du in Aufgabe 1 programmiert hast - nur als Funktion!

**Vorgehen**:

1. Öffne deine `angle.py` aus Aufgabe 1
2. Finde die auskommentierte Funktions-Vorlage oben
3. Entferne die Kommentarzeichen (`#`)
4. Kopiere deinen Code aus Aufgabe 1 in die Funktion:
    - **Schritt 2**: Seitenlängen-Berechnung → bleibt gleich
    - **Schritt 3**: (falls du Methode gewählt hast) → bleibt gleich
    - **Schritt 4**: Taylor-Reihe → bleibt gleich
    - **Schritt 5**: Umrechnung → `return` statt `print()`
5. **Entferne**:
    - Alle `input()`-Anweisungen (Parameter ersetzen diese)
    - Alle `print()`-Anweisungen (nutze `return`)

**Beispiel der Umwandlung**:

**Vorher (Aufgabe 1 - Skript)**:

```python
# Eingabe
x1 = float(input("x1: "))
y1 = float(input("y1: "))
x2 = float(input("x2: "))
y2 = float(input("y2: "))

# Berechnung
delta_x = x2 - x1
delta_y = y2 - y1
# ... Taylor-Reihe ...
ergebnis_grad = ergebnis_radiant * 180 / pi

# Ausgabe
print(ergebnis_grad)
```

**Nachher (Aufgabe 2 - Funktion)**:

```python
def angle_q1(x1: float, y1: float, x2: float, y2: float) -> float:
    """Berechne Winkel zwischen zwei Punkten (0° bis 90°)."""
    # Berechnung (bleibt gleich!)
    delta_x = x2 - x1
    delta_y = y2 - y1
    # ... Taylor-Reihe (dein Code aus Aufgabe 1) ...
    ergebnis_grad = ergebnis_radiant * 180 / pi

    # Rückgabe statt print
    return round(ergebnis_grad, 6)
```

**Wichtig**:

- Dies ist **keine neue Implementierung** - du nutzt deinen Code aus Aufgabe 1!
- Du lernst dabei: Wie wandelt man ein Skript in eine wiederverwendbare Funktion um?

---

### c) `angle(x1: float, y1: float, x2: float, y2: float) -> float`

**Parameter**: Zwei **beliebige** Punkte `(x1, y1)` und `(x2, y2)`

**Rückgabewert**: Winkel φ in Grad, `0° ≤ φ < 360°`

**Zweck**: Bestimmt den Drehwinkel des UFOs für beliebige Zielrichtungen

**Implementierung**: Fallunterscheidung nach Quadranten

#### Quadranten-Logik

Je nachdem in welchem Quadranten (von `(x1, y1)` aus gesehen) der Punkt `(x2, y2)` liegt, gibt es vier Fälle:

**Quadrant 1** (x2 ≥ x1 und y2 ≥ y1):

```
φ = angle_q1(x1, y1, x2, y2)
```

**Quadrant 2** (x2 < x1 und y2 ≥ y1):

```
α = angle_q1(-x1, y1, -x2, y2)
φ = 180° - α
```

**Quadrant 3** (x2 < x1 und y2 < y1):

```
α = angle_q1(-x1, -y1, -x2, -y2)
φ = 180° + α
```

**Quadrant 4** (x2 ≥ x1 und y2 < y1):

```
α = angle_q1(x1, -y1, x2, -y2)
φ = 360° - α
```

**Visualisierung (Beispiel Quadrant 2)**:

```
y
│
│  (x2, y2)
│     /
│    / ← h2
│   /
│  /φ  α
│ /____← h1
│ (x1, y1)
└──────────── x

φ = 180° - α
```

**Hinweis**: Rufe in jedem Fall die Funktion `angle_q1()` auf!

---

### d) `flight_distance(x1: float, y1: float, x2: float, y2: float, z: float) -> float`

**Parameter**:

- `(x1, y1)`, `(x2, y2)`: Start- und Zielpunkt
- `z`: Flughöhe

**Rückgabewert**: Gesamte zu fliegende Strecke (Summe der drei Teilstrecken)

**Berechnung**:

```
Gesamtstrecke = Takeoff-Strecke + Cruise-Strecke + Landing-Strecke
              = z + distance(x1, y1, x2, y2) + z
              = 2*z + distance(x1, y1, x2, y2)
```

**Zweck**: Vergleich der berechneten mit der tatsächlich geflogenen Strecke

**Hinweis**: Verwende die Funktion `distance()`

---

### e) `format_flight_data(sim) -> str`

**Parameter**: `sim` - Referenz auf die Simulation

**Rückgabewert**: Formatierte Zeichenkette mit Flugdaten

**Datenzugriff über Simulation**:

- `sim.get_ftime()`: Flugzeit
- `sim.get_x()`: x-Koordinate
- `sim.get_y()`: y-Koordinate
- `sim.get_z()`: z-Koordinate

**Formatierung**:

- Alle Zahlen: **eine Nachkommastelle**
- Flugzeit: **4 Zeichen breit**
- x-Koordinate: **5 Zeichen breit**
- y-Koordinate: **5 Zeichen breit**
- z-Koordinate: **4 Zeichen breit**

**Beispiel-Rückgabewert**:

```
" 8.5 s: 10.2 -3.1 10.0 "
```

**Format-String**:

```python
f"{zeit:4.1f} s: {x:5.1f} {y:5.1f} {z:4.1f} "
```

**Hinweis**: Auf Typannotation von `sim` kann verzichtet werden

---

### f) `fac(m: int = 1, n: int = 1) -> int`

**Parameter**:

- `n, m`: Ganzzahlen mit `n, m > 0`
- **Default-Werte**: `m=1`, `n=1`

**Rückgabewert**: Produkt `n · (n+1) · (n+2) · ... · m`

**Besonderheit**: **Rekursive** Implementierung (keine Schleife!)

**Rekursionsformel**:

```
fac(m, n) = n · fac(m, n+1) · m
```

**Abbruchbedingung**:

- Wenn `m < n`: Rückgabe `1`
- Wenn `m = n`: Rückgabe `n`

**Beispiele**:

- `fac(5, 3)` = 3 · 4 · 5 = 60
- `fac(4, 3)` = 3 · 4 = 12
- `fac(3, 3)` = 3
- `fac(2, 3)` = 1 (weil 2 < 3)
- `fac(4)` = 1 · 2 · 3 · 4 = 24 (nutzt Default-Parameter)

**Einschränkungen**:

- ❌ Keine Schleifen erlaubt
- ❌ `math.factorial()` nicht erlaubt
- ✅ Muss rekursiv sein

**Hinweis**: Diese Funktion wird erst in einer späteren Aufgabe verwendet

---

## Teil 3: Hauptprogramm ergänzen

In `ufo_main.py` sind an den gekennzeichneten Stellen folgende Ergänzungen vorzunehmen:

### i. Konsolen-Eingabe

**Aufgabe**: Lies Ziel `x`, `y` und Flughöhe `z` von der Konsole ein

**Hinweise**:

- Nutze `input()` und `float()`
- Flughöhe sollte `z > 0` sein (muss aber nicht überprüft werden)

### ii. Ausgabe berechnete Distanz

**Aufgabe**: Gib die zu fliegende Distanz aus (2 Nachkommastellen)

**Berechnung**:

```python
flight_distance(0.0, 0.0, x, y, z)
```

**Format**: `XX.XX` (2 Nachkommastellen)

### iii. Ausgabe tatsächliche Distanz

**Aufgabe**: Gib die tatsächlich geflogene Distanz aus (2 Nachkommastellen)

**Zugriff**:

```python
sim.get_dist()
```

**Format**: `XX.XX` (2 Nachkommastellen)

---

## Testfälle

Teste dein fertiges Programm mit folgenden Eingaben:

### Test 1

- x = 20.0, y = 20.0, z = 10.0

### Test 2

- x = -100.0, y = 20.0, z = 10.0

### Test 3

- x = -1.0, y = -1.0, z = 100.0

### Test 4

- x = 0.0, y = 40.0, z = 8.95

### Bekanntes Problem

Bei Test 2 (`x=-100.0, y=20.0`) wirst du feststellen: **Das UFO landet neben dem Zielpunkt!**

**Fragen zum Nachdenken**:

1. Warum ist das so?
2. Wie kann man das ändern?

**Hinweis**: Das ist nicht gut - wenn das UFO auf einer Straße landen soll, könnte es überfahren werden!

---

## Vorgehensweise

### Empfohlene Schritte

**Vorbereitung**:

1. **Aufgabe 1 abschließen**: Stelle sicher, dass deine `angle.py` funktioniert

2. **angle_q1() Funktion erstellen**:
    - Öffne `angle.py` aus Aufgabe 1
    - Entferne Kommentarzeichen bei der Funktions-Vorlage
    - Kopiere deinen Code hinein (ohne input/print)
    - Teste die Funktion

3. **Import aktivieren**:
    - Öffne `autopilot.py`
    - Finde den auskommentierten Import (Zeile 45)
    - Entferne das `#` vor: `from task.angle.angle import angle_q1`

**Hauptaufgabe**:

1. **Download**: Dateien von Moodle herunterladen
    - `ufo_main.py`
    - `ufo_autopilot.py`
    - `pa2_utest.py`

2. **Funktionsgerüst**: Kopiere Funktionskopfzeilen in `ufo_autopilot.py`

3. **Dummy-Implementierung**: Ergänze Dummy-Rümpfe
   ```python
   def dummy_funktion():
       return 0.0  # für float-Rückgabe
       # return 0    # für int-Rückgabe
       # return ""   # für str-Rückgabe
   ```

4. **Test**: Führe `pa2_utest.py` aus
    - Am Anfang schlagen die meisten Tests fehl (normal!)

5. **Schrittweise Implementierung**:
    - Programmiere eine Funktion nach der anderen
    - Führe nach jeder Funktion `pa2_utest.py` aus
    - Ziel: Alle Tests grün!
    - **Nutze** deine `angle_q1()` Funktion wo sinnvoll!

6. **Hauptprogramm**: Ergänze `ufo_main.py`

7. **Finaler Test**: Teste mit selbst gewählten Eingaben

---

## Vorgaben und Einschränkungen

### Dateinamen

- ✅ `ufo_autopilot.py` (exakt so!)
- ✅ `ufo_main.py` (exakt so!)

### Datei-Inhalte

**ufo_autopilot.py** darf **nur** enthalten:

- Import-Anweisungen
- Die 10 Funktionen:
    - `distance`
    - `angle_q1`
    - `angle`
    - `flight_distance`
    - `format_flight_data`
    - `fac`
    - `fly_to`
    - `takeoff`
    - `cruise`
    - `landing`
- ❌ Kein anderer Code!

**ufo_main.py** darf **nur** enthalten:

- Import-Anweisungen
- Das Hauptprogramm
- ❌ Keine Funktionsdefinitionen!

### Funktions-Signaturen

Die Funktionen müssen **exakt** die spezifizierten Parameter und Rückgabewerte haben:

- ✅ Keine zusätzlichen Parameter
- ✅ Keine anderen Rückgabetypen
- ✅ Typannotationen für alle Parameter (außer `sim`)
- ✅ Typannotationen für alle Rückgabewerte

### Variablennamen

Wie in Aufgabe 1:

- ✅ Nur Kleinbuchstaben
- ✅ Bestandteile mit Unterstrich
- ❌ Keine Umlaute/ß

### Typ-Prüfung

**mypy-Prüfung** muss fehlerfrei durchlaufen:

```bash
mypy ufo_autopilot.py
mypy ufo_main.py
```

### Unit-Tests

`pa2_utest.py` muss **fehlerfrei** durchlaufen:

```bash
python pa2_utest.py
```

**Hinweis**: Das Testskript muss sich im **selben Verzeichnis** befinden wie die beiden .py-Dateien!

---

## Abgabe

### Dateien

Verpacke folgende Dateien in eine **ZIP-Datei**:

- `ufo_autopilot.py`
- `ufo_main.py`

**Wichtig**:

- ✅ Nur **ZIP-Format** erlaubt
- ❌ Keine anderen Formate (7z, rar, etc.)
- ✅ Dateinamen exakt wie angegeben

### Upload

Lade die ZIP-Datei rechtzeitig in **Moodle** hoch.

### Vorführung

Lösungen müssen nur bei offenen Fragen im Praktikum vorgeführt werden.

---

## Checkliste vor Abgabe

### Funktionalität

- ✅ Alle Funktionen haben exakt die spezifizierten Parameter
- ✅ Alle Funktionen haben exakt die spezifizierten Rückgabewerte
- ✅ Keine zusätzlichen Parameter/Rückgabewerte

### Code-Qualität

- ✅ `ufo_autopilot.py` enthält nur die 10 Funktionen + Imports
- ✅ `ufo_main.py` enthält nur Hauptprogramm + Imports
- ✅ Typannotationen vorhanden (außer `sim`)
- ✅ Variablennamen-Regeln eingehalten
- ✅ Keine Syntaxfehler

### Tests

- ✅ `mypy` läuft fehlerfrei
- ✅ `pa2_utest.py` läuft fehlerfrei
- ✅ Alle Testfälle bestanden

### Eigenständigkeit

- ✅ Aufgabe selbstständig gelöst

---

## Lernziele

Nach dieser Aufgabe kannst du:

- ✅ Funktionen mit Parametern und Rückgabewerten schreiben
- ✅ Typannotationen verwenden
- ✅ Code aus einem Skript in Funktionen umwandeln
- ✅ Rekursive Funktionen implementieren
- ✅ Quadranten-Logik für Winkelberechnungen
- ✅ String-Formatierung mit festen Breiten
- ✅ Module importieren und verwenden
- ✅ Mit einer Simulation/API arbeiten

---

## Tipps

### Debugging

1. **Unit-Tests nutzen**: `pa2_utest.py` zeigt dir genau welche Funktion fehlschlägt
2. **Schrittweise testen**: Implementiere eine Funktion nach der anderen
3. **Print-Statements**: Gib Zwischenergebnisse aus
4. **Testfälle manuell prüfen**: Rechne Beispiele per Hand nach

### Häufige Fehler

1. **Falsche Quadranten-Logik**: Achte auf Vorzeichen bei `angle()`
2. **Vergessene Typannotationen**: mypy wird meckern
3. **Falsche Formatierung**: Bei `format_flight_data()` exakt auf Breiten achten
4. **Rekursion ohne Abbruch**: Bei `fac()` Abbruchbedingung nicht vergessen
5. **Zusätzlicher Code**: Nur Funktionen + Imports in den Dateien!

---

## Referenzen

- **Aufgabe 1**: [aufgabe-1-winkelberechnung.md](aufgabe-1-winkelberechnung.md)
- **Implementierung**: `src/task/autopilot/` (Vorlagen)
- **UFO-Handbuch**: Siehe Moodle
- **Setup-Anleitung**: [../setup-anleitung.md](../setup-anleitung.md)

---

**Viel Erfolg beim Programmieren des Autopiloten! 🚁**

