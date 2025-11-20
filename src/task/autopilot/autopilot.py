"""
🎓 PRAKTIKUMSAUFGABE 2 – UFO-AUTOPILOT

AUFGABENBESCHREIBUNG:
→ docs/description/tasks/aufgabe-2-ufo-autopilot.md

Deine Aufgaben:
1. Implementiere die drei Flugphasen: takeoff(), cruise(), landing()
2. Setze USE_DEMO = False wenn deine Implementierung fertig ist
3. Starte die Simulation und teste deinen Autopiloten

Hinweis:
Diese Datei ist Teil der größeren Aufgabe 2. Für die vollständige
Aufgabenstellung (inkl. ufo_autopilot.py mit Hilfsfunktionen) lies
bitte die Aufgabenbeschreibung!

NICHT ändern:
- Die Struktur dieser Klasse
- Die Imports
- Alles außer den 3 Funktionen
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.simulation.autopilot_base import AutopilotBase

if TYPE_CHECKING:
    from core.simulation.ufosim import UfoSim


# ============================================================================
# 📥 IMPORT FÜR WINKELBERECHNUNG AUS AUFGABE 1
# ============================================================================
# ⚠️ WICHTIG: Entferne die Kommentarzeichen (#) erst NACHDEM du in
#            angle.py die Funktion angle_q1() implementiert hast!
#
# VORAUSSETZUNG:
#   1. Du hast Aufgabe 1 abgeschlossen (angle.py funktioniert)
#   2. Du hast in angle.py die Funktion angle_q1() implementiert
#      (siehe "FUNKTIONS-VORLAGE FÜR AUFGABE 2" in angle.py)
#   3. Du hast die Kommentarzeichen dort entfernt
#
# DANN HIER:
#   Entferne die # vor "from task.angle.angle import angle_q1"
#
# VERWENDUNG IN cruise():
#   winkel = angle_q1(sim.state.x, sim.state.y, target_x, target_y)
#
# ============================================================================

# from task.angle.angle import angle_q1

# ============================================================================

class Autopilot(AutopilotBase):
    """
    Dein Autopilot zum selbst schreiben.

    Setze das Flag unten auf False wenn du fertig bist:
    """

    USE_DEMO = True  # ← Setze auf False wenn deine Implementierung fertig ist!

    # ========================================================================
    # AUFGABENBEREICH - IMPLEMENTIERE DIESE 3 FUNKTIONEN
    # ========================================================================

    def takeoff(self, sim: "UfoSim", target_alt: float) -> None:
        """
        ✍️ AUFGABE 1: Implementiere die Startphase

        Ziel:
            Bringe das UFO von der aktuellen Höhe zur Zielflughöhe (target_alt)

        Verfügbare Steuerung:
            - sim.state.delta_v: Geschwindigkeitsänderung (positiv = schneller)
            - sim.state.i: Neigung in Grad (90=vertikal, 45=steil, 0=horizontal)
            - sim.wait_for_condition(bedingung, timeout): Wartet bis Bedingung erfüllt
            - sim.state.z: Aktuelle Höhe

        Fragen zum Nachdenken:
            1. Wie erhöhe ich die Geschwindigkeit?
            2. Welche Neigung brauche ich zum Steigen?
            3. Wann habe ich die Zielflughöhe erreicht?
            4. Wie warte ich bis die Bedingung erfüllt ist?

        ⚠️ Lies die Aufgabenbeschreibung für Details!
        """
        pass  # ← HIER DEIN CODE!

    def cruise(self, sim: "UfoSim", target_x: float, target_y: float) -> None:
        """
        ✍️ AUFGABE 2: Implementiere den Reiseflug

        Ziel:
            Fliege von der aktuellen Position zum Ziel (target_x, target_y)

        Verfügbare Steuerung:
            - sim.state.d: Richtung in Grad (0=Nord, 90=Ost, 180=Süd, 270=West)
            - sim.state.i: Neigung in Grad (0=horizontal)
            - sim.state.delta_v: Geschwindigkeitsänderung
            - sim.state.x, sim.state.y: Aktuelle Position

        💡 VERWENDUNG DEINER angle_q1() FUNKTION:
            Wenn du oben den Import entkommentiert hast, kannst du
            deine Winkelberechnung aus Aufgabe 1 hier nutzen!

            Beispiel:
                winkel = angle_q1(sim.state.x, sim.state.y, target_x, target_y)
                sim.state.d = winkel

            ⚠️ ABER: angle_q1() funktioniert nur für den 1. Quadranten!
                     Für negative Koordinaten brauchst du eine Anpassung.

        Fragen zum Nachdenken:
            1. Wie berechne ich die Differenz zum Ziel (dx, dy)?
            2. Wie berechne ich den Winkel zum Ziel?
               → Mit angle_q1() wenn du sie implementiert hast
               → Oder mit math.atan2(dx, dy) als Alternative
            3. Welche Neigung brauche ich für horizontalen Flug?
            4. Wann bin ich nah genug am Ziel?

        Hinweis zu Winkeln:
            - math.atan2(dx, dy) gibt Winkel in Radiant zurück
            - math.degrees() rechnet in Grad um
            - Negative Winkel müssen auf 0-360° umgerechnet werden

        ⚠️ Lies die Aufgabenbeschreibung für Details zur vollständigen Aufgabe!
        """
        pass  # ← HIER DEIN CODE!

    def landing(self, sim: "UfoSim") -> None:
        """
        ✍️ AUFGABE 3: Implementiere die Landephase

        Ziel:
            Bringe das UFO sicher zum Boden (z <= 0.1)

        Verfügbare Steuerung:
            - sim.state.delta_v: Geschwindigkeitsänderung (negativ = bremsen)
            - sim.state.i: Neigung (negativ = abwärts)
            - sim.state.v: Aktuelle Geschwindigkeit (lesen)
            - sim.state.z: Aktuelle Höhe (lesen)

        Fragen zum Nachdenken:
            1. Wie bremse ich das UFO ab?
            2. Welche Neigung brauche ich für sanften Sinkflug?
            3. Wann habe ich den Boden erreicht?
            4. Was passiert bei zu schneller Landung?

        ⚠️ WARNUNG:
            Zu hohe Geschwindigkeit oder zu steile Neigung → CRASH!
            Teste mit kleinen Werten und beobachte was passiert!

        ⚠️ Lies die Aufgabenbeschreibung für Details!
        """
        pass  # ← HIER DEIN CODE!