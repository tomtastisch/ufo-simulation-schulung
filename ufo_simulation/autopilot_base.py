"""
ABSTRAKTE BASE-KLASSE FÜR AUTOPILOTEN (Nur für Lehrer/Infrastruktur!)

Diese Klasse:
- Verwaltet die Demo-Implementierung (versteckt)
- Orchestriert den Flugablauf
- Handhabt USE_DEMO Logik
- Definiert abstrakte Methoden für Schüler

Schüler erben von dieser Klasse und implementieren nur:
- takeoff()
- cruise()
- landing()

WICHTIG: Schüler ändern NICHTS in dieser Datei!
"""

from __future__ import annotations

import math
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ufo_simulation.ufosim import UfoSim


class AutopilotBase(ABC):
    """
    Abstrakte Basis-Klasse für Autopiloten.

    Diese Klasse:
    - Verwaltet die Demo-Implementierung
    - Orchestriert den Flugablauf
    - Kümmert sich um USE_DEMO Logik

    Schüler erben von dieser Klasse und implementieren nur:
    - takeoff()
    - cruise()
    - landing()
    """

    # Flag für Demo-Modus (wird von der Unterklasse gesetzt)
    USE_DEMO: bool = True

    def __call__(self, sim: "UfoSim") -> None:
        """
        Einstiegspunkt - wird von UfoSim aufgerufen.

        Diese Methode ist FINAL und nicht zu verändern!
        """
        destinations = sim.get_destinations()
        if not destinations:
            print("[Autopilot] Keine Ziele definiert")
            return

        target_x, target_y = destinations[0]
        target_alt = 10.0

        print(f"[Autopilot] Mission: Fliege zu ({target_x}, {target_y})")
        print(f"[Autopilot] Mode: {'DEMO' if self.USE_DEMO else 'DEINE IMPLEMENTIERUNG'}\n")

        if self.USE_DEMO:
            self._demo_flight(sim, target_x, target_y, target_alt)
        else:
            # Schüler-Implementierung
            self.takeoff(sim, target_alt)
            self.cruise(sim, target_x, target_y)
            self.landing(sim)

        print("[Autopilot] Mission beendet\n")

    # ========================================================================
    # DEMO-IMPLEMENTIERUNG (verborgen vor Schülern)
    # ========================================================================

    @staticmethod
    def _demo_flight(
        sim: "UfoSim", target_x: float, target_y: float, target_alt: float
    ) -> None:
        """
        Interne Demo - Schüler können das studieren aber nicht ändern.
        """
        print("[DEMO] ▶ Phase 1: Takeoff")
        sim.state.delta_v = 10.0
        sim.state.i = 45
        start = time.time()
        while sim.state.z < target_alt and time.time() - start < 30.0:
            time.sleep(0.1)
        print(f"[DEMO]   → Erreichte Höhe: {sim.state.z:.1f}m\n")

        print("[DEMO] ▶ Phase 2: Cruise")
        sim.state.i = 0
        dx = target_x - sim.state.x
        dy = target_y - sim.state.y
        direction = math.degrees(math.atan2(dx, dy))
        if direction < 0:
            direction += 360
        sim.state.d = direction
        sim.state.delta_v = 5.0

        start = time.time()
        while time.time() - start < 60.0:
            dist = math.sqrt(
                (sim.state.x - target_x) ** 2 + (sim.state.y - target_y) ** 2
            )
            if dist < 5.0:
                break
            time.sleep(0.1)
        print(f"[DEMO]   → Zielgebiet erreicht\n")

        print("[DEMO] ▶ Phase 3: Landing")
        sim.state.delta_v = -sim.state.v
        sim.state.i = -20
        start = time.time()
        while sim.state.z > 0.1 and time.time() - start < 30.0:
            time.sleep(0.1)
        print(f"[DEMO]   → Gelandet\n")

    # ========================================================================
    # ABSTRAKTE METHODEN - Schüler implementiert diese!
    # ========================================================================

    @abstractmethod
    def takeoff(self, sim: "UfoSim", target_alt: float) -> None:
        """Abstrakte Methode - Schüler implementiert."""
        pass

    @abstractmethod
    def cruise(self, sim: "UfoSim", target_x: float, target_y: float) -> None:
        """Abstrakte Methode - Schüler implementiert."""
        pass

    @abstractmethod
    def landing(self, sim: "UfoSim") -> None:
        """Abstrakte Methode - Schüler implementiert."""
        pass