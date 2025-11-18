Ablaufplan – Refactoring von ufosim.py in modulare Paketstruktur
Ziel: Sauberes, testbares, Clean-Architecture-konformes core.simulation-Paket

⸻

0. Zielbild / Endzustand

Endzustand der Struktur (nur src/core/simulation):

src/core/simulation/
├── __init__.py
├── config.py
├── exceptions.py
├── logging_setup.py
│
├── utils/
│ ├── __init__.py
│ ├── threads.py
│ └── maths.py
│
├── state/
│ ├── __init__.py
│ ├── state.py
│ └── manager.py
│
├── physics/
│ ├── __init__.py
│ ├── engine.py
│ └── integrators.py
│
├── command/
│ ├── __init__.py
│ ├── types.py
│ ├── queue.py
│ └── executor.py
│
├── observer/
│ ├── __init__.py
│ ├── observer.py
│ └── metrics.py
│
├── controller/
│ ├── __init__.py
│ ├── sim.py
│ └── lifecycle.py
│
└── view/
├── __init__.py
├── viewport.py
├── viewmodel.py
├── pview.py
├── hud.py
└── resources/

Öffentliche API (von außen sichtbar):
• core.simulation.SimulationConfig
• core.simulation.DEFAULT_CONFIG
• core.simulation.UfoState
• core.simulation.UfoSim
• core.simulation.ManeuverAnalysis
• core.simulation.Phase

Alles andere ist intern.

⸻

1. Architektur- und Importregeln (Verbindliche Rahmenbedingungen)
    1. Schritt: Import-Hierarchie definieren
       Beschreibung: Vor jeglicher Umsetzung werden klare Import-Richtungen festgelegt, um Zyklen zu vermeiden.

Vorbereitung:
• Bestehende ufosim.py analysieren: Welche Klassen/Funktionen hängen logisch zusammen?
• Gewünschte Modulverantwortlichkeiten (state, physics, controller, view, command, observer, utils) klar auflisten.

Sicherstellung:
• Schriftlich festhalten, welche Pakete wen importieren dürfen.

Durchführung:
• Erlaubte Richtungen:
• view → controller (+ optional observer-Typen/Phase)
• controller → physics, state, command, observer, config
• observer → state.state, config
• physics → state.state, config
• command → state, config
• utils → keine Simulationselemente (nur Standardlib/numpy/etc.)
• Verbotene Richtungen:
• physics → state.manager, controller, view
• observer → controller, view
• view → physics, state.manager
• command → controller, view
• command → observer (nur TYPE_CHECKING falls absolut nötig – im Plan: vermeiden)

Prüfung:
• Kurzes Diagramm oder Textmatrix erstellen.
• In Code-Review später gezielt prüfen: kein Modul verletzt diese Regeln.

⸻

2. Phase 1 – Basis: Konfiguration, State, Logging

2.1 config.py + DEFAULT_CONFIG

1. Schritt: Konfigurationsmodul extrahieren
   Beschreibung: Alle config-bezogenen Elemente aus ufosim.py in config.py auslagern.

Vorbereitung:
• SimulationConfig und DEFAULT_CONFIG in ufosim.py identifizieren.

Sicherstellung:
• Keine Abhängigkeit von Simulation/State/Physics in der Config (nur Standardlib).

Durchführung:
• Neues File src/core/simulation/config.py erstellen.
• SimulationConfig-Dataclass mit allen Parametern dorthin verschieben (inkl. Properties wie vmax_ms, Landeschwellen
etc.).
• DEFAULT_CONFIG = SimulationConfig() definieren.
• In ufosim.py alle direkten Verwendungen durch Imports aus config ersetzen.

Prüfung:
• python -m core.simulation.ufosim (oder dein aktuelles Entry-Skript) ausführen → Verhalten unverändert.
• mypy/IDE: keine neuen Importzyklen.

2.2 state/state.py (UfoState) + state/__init__.py

1. Schritt: State-Datenmodell auslagern
   Beschreibung: UfoState inkl. Vektor-Properties in eigenes Modul verschieben.

Vorbereitung:
• Alle Attribute, Properties (position_vector, velocity_vector, acceleration_vector) in ufosim.py lokalisieren.

Sicherstellung:
• UfoState importiert nur:
• dataclasses
• typing
• numpy
• Kein Zugriff auf StateManager, PhysicsEngine oder UfoSim.

Durchführung:
• Ordner src/core/simulation/state/ anlegen.
• state.py erstellen und UfoState dorthin verschieben.
• state/__init__.py: from .state import UfoState exportieren.
• In der alten ufosim.py und späteren Files: from core.simulation.state import UfoState verwenden.

Prüfung:
• Temporär in ufosim.py: from .state.state import UfoState (lokal relativ) nutzen und Script laufen lassen.
• Sicherstellen, dass numpy-Operationen wie bisher funktionieren.

2.3 logging_setup.py + exceptions.py

1. Schritt: Logging und Exceptions sauber kapseln
   Beschreibung: Gemeinsames Logging-Setup und Platz für projektspezifische Fehlerarten schaffen.

Vorbereitung:
• Aktuelle logging.basicConfig(...)-Konfiguration in ufosim.py identifizieren.

Sicherstellung:
• Logging-Konfiguration muss vor erster Logger-Nutzung gesetzt werden.

Durchführung:
• logging_setup.py anlegen:
• configure_logging() oder direkt beim Import basicConfig.
• get_logger(name: str) -> logging.Logger Hilfsfunktion.
• exceptions.py anlegen:
• class SimulationError(Exception): ...
• class ConfigError(SimulationError): ...
• Optional Platz für weitere (z. B. StateValidationError).

Prüfung:
• logger = get_logger(__name__) in einem Testmodul verwenden → Log-Ausgabe prüfen.
• Keine Seiteneffekte auf andere Projekte (ggf. Log-Level/Format minimal halten).

⸻

3. Phase 2 – Utilities & Physik

3.1 utils/threads.py (@synchronized)

1. Schritt: Synchronisations-Utilities auslagern
   Beschreibung: synchronized-Decorator zentralisieren und wiederverwendbar machen.

Vorbereitung:
• Aktuellen synchronized-Decorator in ufosim.py lokalisieren.

Sicherstellung:
• Decorator soll nur self._lock voraussetzen, nicht spezifische Klassen-Typen.

Durchführung:
• utils/threads.py anlegen:
• F = TypeVar("F", bound=Callable[..., Any])
• def synchronized(method: F) -> F: ...
• In state.manager, command.executor usw. später importieren.

Prüfung:
• Minimalen Test schreiben: Dummy-Klasse mit _lock = RLock() und synchronisierter Methode parallel aufrufen → keine
Race-Conditions/Fehler.

3.2 utils/maths.py (optionale, aber sinnvolle Auslagerung)

1. Schritt: Kleine numerische Helfer isolieren
   Beschreibung: Wiederholte numerische Hilfsfunktionen aus ufosim.py herausziehen.

Vorbereitung:
• Prüfen, ob du bereits Funktionen wie „Grad ↔ Rad“, Clamping, etc. mehrfach nutzt.

Sicherstellung:
• utils/maths.py darf nicht UfoState, UfoSim oder SimulationConfig importieren.

Durchführung:
• Einfache Funktionen definieren wie:
• deg_to_rad(deg: float) -> float
• wrap_angle_deg(angle: float) -> float
• clamp(value: float, min_value: float, max_value: float) -> float
• In physics.engine und observer.observer falls nötig verwenden.

Prüfung:
• Unit-Tests pro Funktion mit typischen und Randwerten.

3.3 physics/engine.py (PhysicsEngine)

1. Schritt: Physik-Engine entkoppeln
   Beschreibung: Physikalische Integrationslogik vollständig aus ufosim.py herauslösen.

Vorbereitung:
• Methoden _apply_landing_assistance, _update_velocity, _update_direction, _update_inclination, _update_position, _
handle_landing, integrate_step.

Sicherstellung:
• PhysicsEngine importiert nur:
• SimulationConfig, DEFAULT_CONFIG
• UfoState
• numpy, logging, ggf. math
• Kein Import von StateManager, UfoSim oder view.

Durchführung:
• physics/engine.py anlegen.
• Klasse PhysicsEngine dorthin verschieben.
• Signatur beibehalten: integrate_step(self, state: UfoState) -> tuple[bool, bool].
• Alle „Magic Numbers“ durch Config-Werte aus SimulationConfig ersetzen (bereits weitgehend so).

Prüfung:
• Kleine Unit-Tests für:
• Steigflug / Sinkflug (z, vz, i, d verändern sich korrekt).
• Sichere Landung vs. Crash (Kriterien greifen erwartungsgemäß).
• ufosim.py temporär anpassen: self._physics_engine = PhysicsEngine(self.config) + Aufruf über StateManager (oder
direkt, bis StateManager ausgelagert ist).

⸻

4. Phase 3 – StateManager & Observer

4.1 state/manager.py (StateManager)

1. Schritt: Thread-sicheren State-Zugriff kapseln
   Beschreibung: StateManager als eigenständige, generische State-Verwaltung isolieren.

Vorbereitung:
• Aktuelle StateManager-Implementierung in ufosim.py identifizieren.

Sicherstellung:
• StateManager hängt nur ab von:
• UfoState
• threading
• typing, dataclasses.replace
• synchronized (aus utils.threads)
• Keine Abhängigkeit von PhysicsEngine, CommandExecutor, UfoSim, view.

Durchführung:
• state/manager.py anlegen.
• StateManager dorthin verschieben.
• Observer-API (register_observer, unregister_observer) und wait_for_condition beibehalten.
• In controller.sim später: self._state_manager = StateManager().

Prüfung:
• Unit-Tests:
• update_state ruft Observer mit Snapshot auf.
• wait_for_condition kehrt bei erfüllter Bedingung oder Timeout korrekt zurück.
• reset setzt State auf neuen UfoState().

4.2 observer/observer.py (Phase, compute_phase, ManeuverAnalysis, StateObserver)

1. Schritt: Phasenmodell und Manöver-Analyse entkoppeln
   Beschreibung: Alle „Leselogik“ zur Phase/Manöverbestimmung in ein reines Analyse-Modul verlagern.

Vorbereitung:
• Phase-Literal, compute_phase, ManeuverAnalysis, StateObserver in ufosim.py lokalisieren.

Sicherstellung:
• observer.observer importiert nur:
• SimulationConfig, DEFAULT_CONFIG
• UfoState
• numpy, collections.deque, dataclasses.replace, logging
• Kein Import von UfoSim, StateManager, CommandQueue.

Durchführung:
• observer/observer.py anlegen.
• Obige Elemente dorthin verschieben.
• Logik beibehalten:
• Phasenregeln mit Prioritäten.
• Analyse von vz, Heading-Delta, Stagnation.
• In state.manager: Observer-Registrierung so lassen (aber der Observer bleibt generisch).

Prüfung:
• Unit-Tests:
• compute_phase für typische Szenarien (idle, takeoff, flying, landing, landed, crashed).
• StateObserver.analyze mit synthetischer History (z. B. stetiges Steigen → is_ascending).

⸻

5. Phase 4 – Command-System

5.1 command/types.py (CommandType, Command)

1. Schritt: Command-Typen definieren
   Beschreibung: Enums und Dataclass für Commands in eigenes Modul verlagern.

Vorbereitung:
• CommandType-Enum und Command-Dataclass in ufosim.py lokalisieren.

Sicherstellung:
• Command referenziert UfoState nur via TYPE_CHECKING + String-Annotation.

Durchführung:
• command/types.py anlegen.
• Enum und Dataclass dorthin verschieben.
• Importstruktur:
• from typing import Optional, Any, Callable, TYPE_CHECKING
• if TYPE_CHECKING: from ..state.state import UfoState

Prüfung:
• Typchecker (mypy) über Paket laufen lassen → keine Laufzeitzyklen.

5.2 command/queue.py (CommandQueue)

1. Schritt: Deklarative Command-Queue kapseln
   Beschreibung: CommandQueue als reine Struktur, keine direkte Simulation/Engine-Logik.

Vorbereitung:
• CommandQueue-Klasse in ufosim.py lokalisieren.

Sicherstellung:
• CommandQueue kennt:
• Command, CommandType
• threading.RLock, threading.Event
• Optional UfoState nur für Typ-Hints (TYPE_CHECKING)
• Keine Imports von StateManager, PhysicsEngine, UfoSim.

Durchführung:
• command/queue.py anlegen.
• set_state, wait_until, execute, log, wait_for_completion, mark_completed übernehmen.

Prüfung:
• Kleiner Test:
• Queue mit set_state/log/wait_until erstellen.
• In einem Dummy-Executor manuell ablaufen lassen und Zustand prüfen.

5.3 command/executor.py (CommandExecutor)

1. Schritt: Executor entkoppeln, Phasenlogik außen lassen
   Beschreibung: CommandExecutor führt CommandQueue gegen StateManager aus, kennt aber keine Phasen-/Maneuver-Analyse.

Vorbereitung:
• CommandExecutor-Implementierung in ufosim.py lokalisieren.

Sicherstellung:
• CommandExecutor importiert:
• StateManager
• CommandQueue, CommandType, Command
• synchronized aus utils.threads
• logging
• Keine Imports von observer, PhysicsEngine, UfoSim, view.

Durchführung:
• command/executor.py anlegen.
•    _execute_set_state nutzt StateManager.update_state mit Lambda/Inner-Funktion.
• process_commands verarbeitet nur:
• SET_STATE
• LOG_MESSAGE
• EXECUTE_FUNC
• WAIT_CONDITION (auf Basis des current_state, der vom Controller geliefert wird)
• KEINE Verwendung von compute_phase o. Ä. im Executor.

Prüfung:
• Test: Dummy-State, Dummy-StateManager, Queue mit mehreren Kommandos (inkl. WAIT_CONDITION) → sicherstellen, dass die
Indizes und Completion-Logik stimmen.

⸻

6. Phase 5 – Controller (UfoSim)

6.1 controller/sim.py (UfoSim)

1. Schritt: UfoSim als Orchestrator neu aufbauen
   Beschreibung: UfoSim importiert nur die anderen Komponenten und koordiniert sie.

Vorbereitung:
• Vorherige UfoSim-Klasse in ufosim.py als Referenz behalten.

Sicherstellung:
• controller.sim importiert:
• SimulationConfig, DEFAULT_CONFIG
• UfoState
• StateManager
• PhysicsEngine
• CommandQueue, CommandExecutor
• StateObserver, ManeuverAnalysis, Phase, compute_phase
• Optionale UfoPView, SimulationViewModel (nur GUI-Pfad, lazy import)
• Kein Rückimport in andere Module.

Durchführung:
• Neues File controller/sim.py anlegen.
• UfoSim.__init__:
• self.config = config
• self._state_manager = StateManager()
• self._physics_engine = PhysicsEngine(config)
• self._command_executor = CommandExecutor(self._state_manager)
• self.observer = StateObserver(config)
• Observer im StateManager registrieren.
• start(...):
• Speedup prüfen/clampen.
• Ziele setzen (self.__destinations).
• Sim-Thread starten (__run_sim).
• Optional Autopilot-Thread.
• Optional GUI initialisieren (mit lazy import).
•    __run_sim:
• update_state mit integrate_step.
• CommandExecutor.process_commands mit Snapshot.
• Logging über format_flight_data.
• Public APIs:
• get_state_snapshot()
• get_phase()
• get_maneuver_analysis()
• get_maneuver_description()
• wait_for_condition(...)
• create_command_queue()
• execute_command_queue(queue)
• format_flight_data()
• reset() / terminate()

Prüfung:
• Altes Verhalten (Single-File) gegen neues refactored Verhalten mit identischer Simulation vergleichen (z. B. kurze
Testflüge).

⸻

7. Phase 6 – View-Layer

7.1 view/viewport.py, view/viewmodel.py, view/hud.py, view/pview.py

1. Schritt: GUI vollständig vom Kern trennen
   Beschreibung: PyQt5-Ansicht arbeitet nur über ViewModel und UfoSim-API.

Vorbereitung:
• Aktuelle UfoPView, UfoViewport, SimulationViewModel, HUD-Helfer in ufosim.py lokalisieren.

Sicherstellung:
• view importiert:
• UfoSim (nur pview)
• SimulationViewModel, UfoViewport, HUD-Helfer
• Qt-Klassen
• Kein Import von PhysicsEngine, StateManager, CommandQueue.

Durchführung:
• viewport.py: UfoViewport mit configure_for_points, to_screen.
• viewmodel.py: SimulationViewModel mit from_simulation(sim: UfoSim).
• hud.py: create_circle_item, create_text_item.
• pview.py: UfoPView (View-Klasse), nutzt nur SimulationViewModel.from_simulation und UfoViewport.
• In controller.sim: GUI-Imports nur innerhalb des GUI-Pfads (if show_view: → from ..view.pview import UfoPView).

Prüfung:
• GUI starten, grundlegende Funktionalität (Darstellung, Crash-Screen, Auto-Shutdown) testen.
• Headless-Mode (ohne Qt-Import) testen: keine Importfehler.

⸻

8. Phase 7 – Autopilot-Integration (außerhalb Kernpaket)
    1. Schritt: Autopilot klar trennen
       Beschreibung: Autopilot-Logik bleibt außerhalb von core.simulation (z. B. in task/autopilot/), nutzt dort nur die
       öffentliche API.

Vorbereitung:
• Aktuelle Autopilot-Beispiele/Beispiellösungen analysieren.

Sicherstellung:
• Autopilot kennt nur:
• UfoSim, CommandQueue, eventuell ManeuverAnalysis, Phase
• Keine direkten Imports von PhysicsEngine, StateManager.

Durchführung:
• task/autopilot/autopilot.py (oder ähnlicher Pfad) als Schulungsmodul.
• Autopilot erzeugt CommandQueues (sim.create_command_queue()) und übergibt sie an sim.execute_command_queue(queue).

Prüfung:
• Kursaufgaben prüfen: geforderte Schnittstelle (UfoSim.start(autopilot_callback=...)) bleibt kompatibel.

⸻

9. Phase 8 – Tests, Linting, Public API

9.1 __init__.py in core.simulation

1. Schritt: Öffentliche API definieren
   Beschreibung: Nur ausgewählte Symbole werden von oben exportiert.

Vorbereitung:
• Welche Teile sollen von außen genutzt werden? (Sim, State, Config, Phase/Maneuver).

Sicherstellung:
• Interne Details (engine, manager, executor, observer-Implementierung) nicht exportieren.

Durchführung:
• core/simulation/__init__.py:

from .config import SimulationConfig, DEFAULT_CONFIG
from .state.state import UfoState
from .controller.sim import UfoSim
from .observer.observer import ManeuverAnalysis, Phase

__all__ = [
"SimulationConfig",
"DEFAULT_CONFIG",
"UfoState",
"UfoSim",
"ManeuverAnalysis",
"Phase",
]

Prüfung:
• Externe Nutzung in einem Testprojekt:
• from core.simulation import UfoSim, SimulationConfig, UfoState.

9.2 Tests & Linting

1. Schritt: Testabdeckung und statische Analyse ergänzen
   Beschreibung: Jede Kernkomponente bekommt Unit-Tests und wird statisch geprüft.

Vorbereitung:
• pytest, mypy, flake8 sind bereits installiert (siehe setup-Script).

Sicherstellung:
• Teststruktur z. B. tests/test_state.py, tests/test_physics.py, etc.

Durchführung:
• Tests pro Modul:
• test_config.py: Schwellenwerte, abgeleitete Werte.
• test_state.py: Vektoreigenschaften.
• test_physics.py: integrative Schritt-Tests (einfache Szenarien).
• test_observer.py: Phasen/Flags.
• test_command.py: Queue/Executor-Szenarien.
• test_controller.py: einfacher Simulationslauf mit wenigen Schritten.
• mypy und flake8 über src/core/simulation laufen lassen.

Prüfung:
• pytest ohne Fehler.
• mypy src/core/simulation ohne schwerwiegende Typfehler.
• flake8 ohne relevante Verstöße (oder bewusst akzeptierte Ausnahmen).

⸻