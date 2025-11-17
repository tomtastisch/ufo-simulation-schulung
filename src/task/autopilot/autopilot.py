"""
🎓 AUTOPILOT-VORLAGE FÜR SCHÜLER

Deine Aufgaben:
1. Implementiere takeoff(), cruise(), landing()
2. Setze USE_DEMO = False wenn fertig
3. Starte die Simulation und teste deinen Autopiloten

NICHT ändern:
- Die Struktur dieser Klasse
- Irgendwas anderes als die 3 Funktionen
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.simulation.autopilot_base import AutopilotBase

if TYPE_CHECKING:
    from core.simulation.ufosim import UfoSim

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
            - sim.state.i: Neigung in Grad (90=vertikal hoch, 45=steil, 0=horizontal)
            - sim.wait_for_condition(lambda, timeout): Wartet bis Bedingung erfüllt
            - sim.state.z: Aktuelle Höhe (lesen)

        Tipps:
            1. Setze delta_v auf einen positiven Wert (z.B. 10.0)
            2. Setze i auf ca. 45° (steil aufwärts)
            3. Warte mit wait_for_condition bis z >= target_alt
            4. Teste deine Implementierung mit USE_DEMO = False

        Beispiel-Struktur:
            sim.state.delta_v = 10.0
            sim.state.i = 45
            sim.wait_for_condition(lambda s: s.z >= target_alt, timeout=30.0)

        ⚠️ Nicht kopieren - das bringt dir nichts zum Lernen!
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
            - sim.state.x, sim.state.y: Aktuelle Position (lesen)
            - math.atan2(dx, dy): Berechne Winkel
            - math.sqrt(x**2 + y**2): Berechne Distanz

        Tipps:
            1. Berechne dx = target_x - sim.state.x
            2. Berechne dy = target_y - sim.state.y
            3. Nutze math.degrees(math.atan2(dx, dy)) für Richtung
            4. Setze sim.state.d auf diese Richtung
            5. Setze sim.state.i = 0 für horizontalen Flug
            6. Warte bis Distanz zum Ziel < 5m

        Beispiel-Struktur:
            dx = target_x - sim.state.x
            dy = target_y - sim.state.y
            direction = math.degrees(math.atan2(dx, dy))
            if direction < 0: direction += 360
            sim.state.d = direction
            sim.state.i = 0
            # ... warte bis nahe am Ziel ...

        ⚠️ Nicht kopieren - das bringt dir nichts zum Lernen!
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

        Tipps:
            1. Reduziere Geschwindigkeit mit negativem delta_v
            2. Setze i auf ca. -20° (sanfter Sinkflug)
            3. Warte bis z <= 0.1
            4. Zu hohe Geschwindigkeit/Neigung → CRASH! ⚠️

        Beispiel-Struktur:
            sim.state.delta_v = -sim.state.v  # Bremse auf 0
            sim.state.i = -20  # Sinkflug
            sim.wait_for_condition(lambda s: s.z <= 0.1, timeout=30.0)

        ⚠️ Nicht kopieren - das bringt dir nichts zum Lernen!
        """
        pass  # ← HIER DEIN CODE!