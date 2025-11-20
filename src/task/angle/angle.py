"""
🎓 PRAKTIKUMSAUFGABE 1 – WINKELBERECHNUNG

AUFGABENBESCHREIBUNG:
→ docs/description/tasks/aufgabe-1-winkelberechnung.md

Deine Aufgabe:
Berechne den Winkel φ (Phi) zwischen zwei Punkten (x1,y1) und (x2,y2)
NUR mit Grundrechenarten und math.sqrt - OHNE trigonometrische Funktionen!

Kern-Vorgaben:
- Variablennamen: klein_mit_unterstrich (keine Umlaute/ß)
- Eingabe: x1, y1, x2, y2 mit Validierung (x2 ≥ x1 und y2 ≥ y1)
- Berechnung: Taylor-Reihe für arctan ODER arccos
- Abbruch: |letzter Summand| < 0.000001
- Schleifen: Maximal 2 (Input-Validierung + Taylor-Berechnung)
- Keine Funktionsdefinitionen erlaubt!

Lies die vollständige Aufgabenbeschreibung bevor du beginnst!
"""

# ============================================================================
# 🔧 FUNKTIONS-VORLAGE FÜR AUFGABE 2
# ============================================================================
# ⚠️ FÜR AUFGABE 1: Lass diesen Block auskommentiert!
#
# ✅ FÜR AUFGABE 2: Entferne die Kommentarzeichen (#) und implementiere
#                   die Funktion mit deinem Code von unten!
#
# Diese Funktion wird in Aufgabe 2 (UFO-Autopilot) benötigt.
# Du kopierst deinen Code aus den Schritten 2-5 in diese Funktion.
# ============================================================================

# def angle_q1(x1: float, y1: float, x2: float, y2: float) -> float:
#     """
#     Berechne Winkel zwischen zwei Punkten (nur 1. Quadrant: 0° bis 90°).
#
#     Parameter:
#         x1, y1: Startpunkt
#         x2, y2: Zielpunkt (mit x2 >= x1 und y2 >= y1)
#
#     Rückgabe:
#         Winkel in Grad (0° bis 90°)
#     """
#     # ← HIER KOMMT DEIN CODE AUS SCHRITT 2-5 (ohne input/print)
#     pass

# ============================================================================
# AUFGABENBEREICH FÜR AUFGABE 1 - IMPLEMENTIERE HIER DEIN SKRIPT
# ============================================================================

# 📌 SCHRITT 1: EINGABE UND VALIDIERUNG
# ============================================================================
# Ziel:
#   Lese x1, y1, x2, y2 von der Konsole ein und validiere die Eingabe
#
# Anforderungen:
#   - x2 muss ≥ x1 sein
#   - y2 muss ≥ y1 sein
#   - Bei ungültiger Eingabe: Wiederhole die Eingabe
#
# Erlaubte Schleife: Eine Input-Validierungs-Schleife
#
# Hinweise:
#   - input() und float() sind deine Freunde
#   - Eine while-Schleife kann sich wiederholen bis eine Bedingung erfüllt ist
#   - Bei Fehler: Informiere den Benutzer was falsch war
#
# ⚠️ Schau in die Aufgabenbeschreibung wenn du nicht weiter kommst!
# ============================================================================

pass  # ← HIER DEIN CODE FÜR EINGABE UND VALIDIERUNG!

# 📌 SCHRITT 2: BERECHNUNG DER SEITENLÄNGEN
# ============================================================================
# Ziel:
#   Berechne die Katheten und Hypotenuse des rechtwinkligen Dreiecks
#
# Gegeben:
#   - Punkt 1: (x1, y1)
#   - Punkt 2: (x2, y2)
#
# Gesucht:
#   - Ankathete (delta_x)
#   - Gegenkathete (delta_y)
#   - Hypotenuse (mit Satz des Pythagoras)
#
# Erlaubt: Grundrechenarten + math.sqrt()
#
# Hinweise:
#   - Delta bedeutet "Differenz"
#   - Pythagoras: c² = a² + b²
#   - math.sqrt() berechnet die Wurzel
# ============================================================================

pass  # ← HIER DEIN CODE FÜR SEITENLÄNGEN-BERECHNUNG!

# 📌 SCHRITT 3: WAHL DER METHODE (arctan ODER arccos)
# ============================================================================
# Du hast zwei Möglichkeiten den Winkel zu berechnen:
#
# METHODE A: arctan (Arkustangens)
#   Formel: φ = arctan(delta_y / delta_x)
#   Vorteil: Einfacher für Winkel nahe 0° oder 90°
#   Taylor-Reihe: arctan(z) = z - z³/3 + z⁵/5 - z⁷/7 + ...
#   Konvergiert für: -1 < z < 1
#
# METHODE B: arccos (Arkuskosinus)
#   Formel: φ = arccos(delta_x / c)
#   Vorteil: Direkter geometrisch
#   Taylor-Reihe: arccos(z) = π/2 - arcsin(z)
#                 arcsin(z) = z + (1/2)(z³/3) + (1·3)/(2·4)(z⁵/5) + ...
#   Konvergiert für: -1 ≤ z ≤ 1
#
# 💡 EMPFEHLUNG: Wähle arctan - ist einfacher zu implementieren!
#
# Sonderfall beachten:
#   - Wenn delta_x = 0: Winkel = 90° (senkrecht)
#   - Wenn delta_y = 0: Winkel = 0° (waagerecht)
# ============================================================================

pass  # ← HIER DEIN CODE FÜR DIE GEWÄHLTE METHODE (ARCTAN ODER ARCCOS)

# 📌 SCHRITT 4: TAYLOR-REIHE IMPLEMENTIEREN
# ============================================================================
# Ziel:
#   Berechne arctan(z) oder arccos(z) mit Taylor-Reihe
#
# Anforderungen:
#   - Summiere Terme bis |letzter Summand| < 0.000001
#   - Nutze EINE Schleife für die Berechnung
#   - Keine Funktionsdefinitionen!
#
# TAYLOR-REIHE FÜR arctan(z):
# ---------------------------
# arctan(z) = z - z³/3 + z⁵/5 - z⁷/7 + z⁹/9 - ...
#
# Allgemeine Form des n-ten Summanden:
#   summand_n = (-1)ⁿ · z^(2n+1) / (2n+1)
#
# WICHTIGE FRAGEN ZUM NACHDENKEN:
#   1. Was ist z? (Verhältnis welcher Seiten?)
#   2. Wie berechnest du den ersten Summand?
#   3. Wie kommst du vom Summand n zum Summand n+1?
#      → Tipp: summand_(n+1) = summand_n · Faktor
#      → Welcher Faktor?
#   4. Wann stoppt die Schleife?
#   5. Was machst du mit den Summanden?
#
# Hinweise:
#   - abs() liefert den Betrag
#   - Initialisiere Variablen VOR der Schleife
#   - Das Ergebnis ist in RADIANT (Bogenmaß)!
#   - Für Umrechnung: Grad = Radiant · 180 / π
#
# ⚠️ ACHTUNG Sonderfall:
#   Was passiert wenn delta_x = 0? (Division durch 0!)
#   Behandle diesen Fall separat!
# ============================================================================

pass  # ← HIER DEIN CODE FÜR TAYLOR-REIHE!

# 📌 SCHRITT 5: UMRECHNUNG UND AUSGABE
# ============================================================================
# Ziel:
#   Rechne Radiant in Grad um und gib das Ergebnis aus
#
# Formel:
#   grad = radiant · 180 / π
#
# Hinweise:
#   - π ≈ 3.141592653589793 (hardcode diesen Wert!)
#   - Alternativ: Berechne π selbst mit einer Reihe (fortgeschritten)
#   - Runde das Ergebnis auf 6 Nachkommastellen
#   - Gib das Ergebnis mit print() aus
#
# ⚠️ math.pi ist NICHT erlaubt in Teil 2 der Aufgabe!
# ============================================================================

pass  # ← HIER DEIN CODE FÜR UMRECHNUNG UND AUSGABE!

# ============================================================================
# 📊 TESTFÄLLE ZUM ÜBERPRÜFEN
# ============================================================================
#
# Teste dein Programm mit diesen Eingaben:
#
# Test 1: Waagerecht (0°)
#   x1=0, y1=0, x2=10, y2=0
#   Erwartetes Ergebnis: 0°
#
# Test 2: Kleine Steigung (~18.43°)
#   x1=0, y1=0, x2=3, y2=1
#   Erwartetes Ergebnis: ≈ 18.434949°
#
# Test 3: 45°-Winkel
#   x1=0, y1=0, x2=5, y2=5
#   Erwartetes Ergebnis: 45°
#
# Test 4: Steile Steigung (~71.57°)
#   x1=0, y1=0, x2=1, y2=3
#   Erwartetes Ergebnis: ≈ 71.565051°
#
# Test 5: Senkrecht (90°)
#   x1=0, y1=0, x2=0, y2=10
#   Erwartetes Ergebnis: 90°
#
# ⚠️ Alle Tests müssen auf 6 Nachkommastellen genau sein!
#
# ============================================================================


# ============================================================================
# 💡 HILFREICHE HINWEISE
# ============================================================================
#
# 1. DEBUGGING:
#    - Gib Zwischenergebnisse aus: print(f"delta_x={delta_x}")
#    - Prüfe jeden Summand: print(f"n={n}, summand={summand}")
#    - Nutze diese Ausgaben zum Verstehen was dein Code macht!
#
# 2. HÄUFIGE FEHLER:
#    - Division durch 0: Sonderfall delta_x=0 nicht behandelt
#    - Falsche Reihenfolge im Bruch bei der Faktor-Berechnung
#    - Vergessen das Vorzeichen zu wechseln (alternierend!)
#    - Ergebnis nicht von Radiant in Grad umgerechnet
#
# 3. WENN DU NICHT WEITERKOMMST:
#    - Lies die Aufgabenbeschreibung nochmal durch
#    - Schau dir die mathematischen Formeln genau an
#    - Frage deinen Nachbarn oder den Lehrer
#    - Probiere verschiedene Testfälle aus
#
# ============================================================================

# ⚠️ WICHTIG: Lösche diese Kommentare NICHT - sie helfen beim Lernen!

# ============================================================================
# 🔄 FÜR AUFGABE 2: VON SKRIPT ZU FUNKTION UMWANDELN
# ============================================================================
#
# Wenn du mit Aufgabe 1 fertig bist und zur Aufgabe 2 übergehst:
#
# SCHRITT 1: Gehe nach oben zur "FUNKTIONS-VORLAGE FÜR AUFGABE 2"
# SCHRITT 2: Entferne dort die Kommentarzeichen (#)
# SCHRITT 3: Kopiere deinen Code aus Schritt 2-5 in die Funktion
# SCHRITT 4: Entferne input()-Anweisungen (Parameter ersetzen diese)
# SCHRITT 5: Ersetze print() mit return
#
# BEISPIEL DER UMWANDLUNG:
# ------------------------
# VORHER (Aufgabe 1 - Skript):
#   x1 = float(input("x1: "))      ← Wird zu Parameter
#   ...
#   delta_x = x2 - x1              ← Bleibt gleich
#   ...
#   print(ergebnis_grad)           ← Wird zu return
#
# NACHHER (Aufgabe 2 - Funktion):
#   def angle_q1(x1, y1, x2, y2):  ← Parameter statt input()
#       delta_x = x2 - x1          ← Code bleibt gleich
#       ...
#       return ergebnis_grad       ← return statt print()
#
# ⚠️ NOCHMAL: Für Aufgabe 1 brauchst du das NICHT!
#             Implementiere jetzt erst dein funktionierendes Skript.
#             Diese Umwandlung machst du erst in Aufgabe 2.
#
# ============================================================================
