from autopilot import Autopilot  # ← Automatisch die richtige Klasse!
from ufosim import UfoState, Phase, UfoSim

if __name__ == "__main__":
    sim = UfoSim()

    print("\n" + "=" * 70)
    print("STARTBEDINGUNGEN:")
    print(f"  Position: ({sim.state.x}, {sim.state.y}, {sim.state.z})m")
    print(f"  Geschwindigkeit: {sim.state.v} km/h")
    print(f"  Richtung: {sim.state.d}° (0=Nord, 90=Ost, 180=Süd, 270=West)")
    print(f"  Neigung: {sim.state.i}° (90=hoch, 0=horizontal, -90=runter)")
    print("=" * 70 + "\n")

    autopilot = Autopilot()

    destinations = [(100.0, 0.0)]

    sim.start(
        speedup=50,
        destinations=destinations,
        show_view=True,
        enable_logging=True,
        log_interval_s=0.5,
        autopilot_callback=autopilot
    )

    print("\n" + "=" * 70)
    print("SIMULATION BEENDET")
    print("=" * 70)
    final_phase: Phase = sim.get_phase()
    final_state: UfoState = sim.get_state_snapshot()
    print(f"Endposition: ({final_state.x:.2f}, {final_state.y:.2f}, {final_state.z:.2f})m")
    print(f"Phase: {final_phase}")
    print(f"Gesamtdistanz: {final_state.dist:.2f}m")
    print(f"Flugzeit: {final_state.ftime:.2f}s")
    print("=" * 70 + "\n")