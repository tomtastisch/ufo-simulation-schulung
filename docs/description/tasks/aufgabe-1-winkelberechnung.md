# Aufgabe 1 – Winkelberechnung

Praktikumsaufgabe zur Vorbereitung des UFO-Flugs: Berechne den Winkel zwischen zwei Punkten mit Taylor-Reihen.

---

## Aufgabenstellung

Erstelle ein Python-Skript, das den Winkel φ (Phi) zwischen zwei Punkten im kartesischen Koordinatensystem berechnet.

### Eingabe

Vier Fließkommazahlen über die Konsole:

- `x1, y1`: Erster Punkt (Startpunkt)
- `x2, y2`: Zweiter Punkt (Zielpunkt)

**Bedingung**: `x2 ≥ x1` und `y2 ≥ y1`

### Ausgabe

Fließkommazahl `φ` (Phi): Winkel in Grad zwischen:

- Halbgeraden `h1` (parallel zur x-Achse durch Punkt 1)
- Halbgeraden `h2` (von Punkt 1 zu Punkt 2)

**Wertebereich**: `0° ≤ φ ≤ 90°`

### Geometrische Darstellung

```
y
│
│    (x2, y2)
│       /
│      /  h2
│     /
│    /  φ
│   /______ h1
│  (x1, y1)
│
└──────────────── x
```

---

## Mathematischer Hintergrund

### Rechtwinkliges Dreieck

Gegeben ein rechtwinkliges Dreieck mit:

- Ankathete `a = x2 - x1` (delta_x)
- Gegenkathete `b = y2 - y1` (delta_y)
- Hypotenuse `c = √(a² + b²)`

### Zwei Berechnungsmöglichkeiten

**Methode 1: Arkuskosinus (arccos)**

```
φ = arccos(a/c)
```

**Methode 2: Arkustangens (arctan)**

```
φ = arctan(b/a)
```

**Aufgabe**: Wähle eine der beiden Methoden aus!

---

## Teil 1: Grundlegende Implementierung

### Anforderungen

1. **Flussdiagramm** erstellen (per Hand oder Zeichenprogramm)
2. **Python-Skript** schreiben (`angle.py`)
3. **Konsolen-Ein-/Ausgabe** verwenden
4. **Keine Prüfung** auf korrekte Fließkommazahlen erforderlich

### Erlaubte Funktionen

- ✅ Python-Grundfunktionen (Konsolen-Ein-/Ausgabe)
- ✅ Mathematische Funktionen: `math.acos` oder `math.atan`
- ✅ Wurzelfunktion: `math.sqrt`

### Testfälle

Teste mit verschiedenen Winkeln:

- `φ = 0°` (waagerecht)
- `0° < φ < 45°` (flache Steigung)
- `φ = 45°` (diagonal)
- `45° < φ < 90°` (steile Steigung)
- `φ = 90°` (senkrecht)

---

## Teil 2: Taylor-Reihen-Implementierung

### Aufgabe

Ersetze die Berechnung von `arccos` oder `arctan` durch eine **eigene Implementierung mit Taylor-Reihen**.

### Taylor-Reihen-Formeln

**Für arccos (falls gewählt):**

```
φ = arccos(t) = π/2 - t - (1/(2·3))·t³ - ((1·3)/(2·4·5))·t⁵ - ((1·3·5)/(2·4·6·7))·t⁷ - ...

mit t = a/c und 0 < φ ≤ π/2
```

**Für arctan (falls gewählt):**

Es gibt zwei Fälle:

**Fall 1:** `t ≤ 1` (also `φ ≤ π/4 = 45°`)

```
φ = arctan(t) = t - t³/3 + t⁵/5 - t⁷/7 + t⁹/9 - ...

mit t = b/a
```

**Fall 2:** `t > 1` (also `π/4 < φ < π/2`)

```
φ = arctan(1/t) = π/2 - (t - t³/3 + t⁵/5 - t⁷/7 + ...)

mit t = a/b
```

### Abbruchkriterium

Die Schleife läuft, **bis der letzte Summand** zwischen `-0.000001` und `+0.000001` liegt.

```python
while abs(summand) >= 0.000001:
# Berechnung...
```

### Inkrementelle Berechnung

**Wichtiger Hinweis**: Berechne den nächsten Summand aus dem vorherigen!

Wenn `a_k` der k-te Summand ist, dann ist `a_(k+1) = p · a_k`.

**Frage**: Wie lautet der Faktor `p`?

**Beispiel für arctan:**

```
a_k = (-1)^k · t^(2k+1) / (2k+1)
a_(k+1) = (-1)^(k+1) · t^(2k+3) / (2k+3)

→ p = -t² · (2k+1) / (2k+3)
```

---

## Einschränkungen und Vorgaben

### Variablennamen

Alle Variablen müssen folgende Regeln einhalten:

- ✅ Nur **Kleinbuchstaben**
- ✅ Bestandteile mit **Unterstrich** getrennt
- ❌ **Keine Umlaute** (ä, ö, ü)
- ❌ **Kein ß**

**Beispiele:**

- ✅ `delta_x`, `ergebnis_radiant`, `summand`
- ❌ `deltaX`, `ErgebnisRadiant`, `winkel_größe`

### Erlaubte Operationen

**Nur folgende Operationen sind erlaubt:**

- ✅ Grundrechenarten: `+`, `-`, `*`, `/`
- ✅ Wurzelfunktion: `math.sqrt()`
- ✅ Potenzierung: `**` (nur für Quadrat)
- ✅ Betrag: `abs()`

**NICHT erlaubt:**

- ❌ `math.atan`, `math.acos`, `math.tan`, `math.cos`, `math.sin`
- ❌ `math.hypot`, `math.degrees`, `math.radians`
- ❌ Jegliche andere Trigonometrie-Funktionen

### Schleifen-Beschränkung

**Erlaubt sind genau 2 Schleifen:**

1. **Eine Schleife für die Eingabevalidierung**
    - Wiederholung bei ungültiger Eingabe
    - Prüfung: `x2 ≥ x1` und `y2 ≥ y1`

2. **Eine Schleife für die Taylor-Reihe**
    - Berechnung der Summanden
    - Abbruch bei `|summand| < 0.000001`

**Nicht erlaubt:**

- ❌ Weitere Schleifen
- ❌ Verschachtelte Schleifen (außer Input-Validierung)

### Weitere Einschränkungen

- ❌ **Keine Funktionsdefinitionen** (`def` nicht erlaubt)
- ❌ **Keine externen Bibliotheken** (außer `math` für `sqrt`)
- ❌ **Kein Imports** außer `import math`

---

## Dateiname und Abgabe

### Dateiname

Die Datei **muss** `angle.py` heißen.

### Checkliste vor der Abgabe

Stelle vor der Abgabe sicher:

**Code-Qualität:**

- ✅ Variablennamen-Regeln eingehalten
- ✅ Keine Syntaxfehler
- ✅ Code ist kommentiert und verständlich

**Funktionalität:**

- ✅ Alle Testfälle funktionieren korrekt:
    - `φ = 0°`
    - `0° < φ < 45°`
    - `φ = 45°`
    - `45° < φ < 90°`
    - `φ = 90°`

**Vorgaben:**

- ✅ Dateiname ist `angle.py`
- ✅ Nur `math.sqrt` verwendet (keine anderen math-Funktionen)
- ✅ Keine Funktionen definiert
- ✅ Genau 2 Schleifen (Input + Taylor)
- ✅ Abbruchkriterium `|summand| < 0.000001`

**Eigenständigkeit:**

- ✅ Aufgabe selbstständig gelöst

### Abgabe

1. **Flussdiagramm** mitbringen (nicht hochladen)
2. **`angle.py`** in Moodle hochladen
3. **Abnahme im Praktikum** mit Vorführung
4. **Testat** nach erfolgreicher Abnahme

---

## Testbeispiele

### Beispiel 1: Waagerecht (0°)

**Eingabe:**

```
x1 = 0
y1 = 0
x2 = 10
y2 = 0
```

**Erwartete Ausgabe:**

```
0.0
```

### Beispiel 2: 45°-Winkel

**Eingabe:**

```
x1 = 0
y1 = 0
x2 = 5
y2 = 5
```

**Erwartete Ausgabe:**

```
45.0
```

### Beispiel 3: Steile Steigung (~71.57°)

**Eingabe:**

```
x1 = 0
y1 = 0
x2 = 1
y2 = 3
```

**Erwartete Ausgabe:**

```
71.565051
```

### Beispiel 4: Senkrecht (90°)

**Eingabe:**

```
x1 = 0
y1 = 0
x2 = 0
y2 = 10
```

**Erwartete Ausgabe:**

```
90.0
```

---

## Tipps und Hinweise

### Debugging

1. **Zwischenergebnisse ausgeben:**
   ```python
   print(f"delta_x = {delta_x}")
   print(f"delta_y = {delta_y}")
   print(f"z = {z}")
   ```

2. **Summanden verfolgen:**
   ```python
   print(f"Iteration {n}: summand = {summand}")
   ```

### Häufige Fehler

1. **Division durch 0**
    - Tritt auf wenn `delta_x = 0` (senkrechter Fall)
    - Sonderfall separat behandeln!

2. **Falsche Taylor-Reihe**
    - Vorzeichen beachten: alternierend (+/-)
    - Nenner korrekt berechnen

3. **Radiant statt Grad**
    - Taylor-Reihe liefert Ergebnis in Radiant
    - Umrechnung: `grad = radiant * 180 / π`

4. **π-Wert**
    - Nutze `math.pi` **NICHT** (nicht erlaubt in Teil 2)
    - Hardcode: `pi = 3.141592653589793`

### Optimierungen

1. **z² speichern:**
   ```python
   z_quadrat = z * z
   summand = summand * (-z_quadrat) * (2*n+1) / (2*n+3)
   ```

2. **Sonderfälle vorab prüfen:**
   ```python
   if delta_x == 0:
       winkel = 90.0
   elif delta_y == 0:
       winkel = 0.0
   else:
       # Taylor-Reihe
   ```

---

## Mathematische Herleitung (Optional)

### Arkustangens Taylor-Reihe

Die Ableitung von `arctan(z)` ist `1/(1+z²)`.

Die geometrische Reihe liefert:

```
1/(1+z²) = 1 - z² + z⁴ - z⁶ + ...
```

Integration ergibt:

```
arctan(z) = z - z³/3 + z⁵/5 - z⁷/7 + ...
```

**Konvergiert für:** `-1 < z < 1`

### Arkuskosinus Taylor-Reihe

```
arccos(z) = π/2 - arcsin(z)
```

Mit:

```
arcsin(z) = z + (1/2)·(z³/3) + (1·3)/(2·4)·(z⁵/5) + ...
```

---

## Weiterführende Informationen

### Von Skript zu Funktion (für Aufgabe 2)

Wenn du mit Aufgabe 1 fertig bist, wirst du in **Aufgabe 2** (UFO-Autopilot) deine Winkelberechnung als Funktion
benötigen.

#### Umwandlungs-Prozess

**Dein Skript (Aufgabe 1)**:

```python
# Schritt 1: Eingabe
x1 = float(input("x1: "))
y1 = float(input("y1: "))
x2 = float(input("x2: "))
y2 = float(input("y2: "))

# Schritt 2-4: Berechnung
delta_x = x2 - x1
delta_y = y2 - y1
# ... Taylor-Reihe ...
ergebnis_grad = ...

# Schritt 5: Ausgabe
print(ergebnis_grad)
```

**Als Funktion (Aufgabe 2)**:

```python
def angle_q1(x1: float, y1: float, x2: float, y2: float) -> float:
    """Berechne Winkel zwischen zwei Punkten (0° bis 90°)."""
    # Schritt 2-4: Berechnung (bleibt gleich!)
    delta_x = x2 - x1
    delta_y = y2 - y1
    # ... Taylor-Reihe ...
    ergebnis_grad = ...

    # Schritt 5: Rückgabe statt Ausgabe
    return ergebnis_grad
```

**Änderungen**:

1. ❌ `input()` entfernen → Parameter verwenden
2. ✅ Berechnung bleibt gleich
3. ❌ `print()` entfernen → `return` verwenden

#### Hinweis in angle.py

In deiner `angle.py` Datei findest du:

- Oben: Auskommentierte Funktions-Vorlage
- Unten: Detaillierte Umwandlungs-Anleitung

**Erst in Aufgabe 2** wirst du dies nutzen!

---

### Nächste Aufgabe

Nach erfolgreicher Abnahme dieser Aufgabe folgt:

- **Aufgabe 2**: UFO-Autopilot programmieren
- Verwendung der Winkelberechnung für Navigation
- Umwandlung deines Skripts in eine Funktion

### Lernziele

Nach dieser Aufgabe kannst du:

- ✅ Konsolen-Ein-/Ausgabe in Python
- ✅ Schleifen mit Abbruchkriterium
- ✅ Taylor-Reihen implementieren
- ✅ Trigonometrische Berechnungen ohne Bibliotheken
- ✅ Inkrementelle Algorithmen
- ✅ Sonderfälle behandeln

---

## Referenzen

- **Implementierung**: `src/task/angle/angle.py` (Vorlage mit Struktur-Vorgaben)
- **Setup-Anleitung**: [setup-anleitung.md](../setup-anleitung.md)
- **Schulungsablauf**: [schulungsablauf.md](../schulungsablauf.md)

---

**Viel Erfolg bei der Aufgabe! 🎓**

