#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UFO-Simulation Controller.

Orchestriert Simulation-Lifecycle, Threading und Komponenten-Integration.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, replace as dataclass_replace
from enum import Enum, auto
from pathlib import Path
from typing import Optional, List, Tuple, overload, Callable, Any, final

import numpy as np
# noinspection PyPackageRequirements
from PyQt5 import QtWidgets, QtGui, QtCore

from .infrastructure import DEFAULT_CONFIG, SimulationConfig, get_logger
from .observer import Phase, ManeuverAnalysis, compute_phase, StateObserver
from .physics import PhysicsEngine
from .state import UfoState, StateManager
from .synchronization import conditional, synchronized

# =============================================================================
# LOGGING - Verwendet zentrale Konfiguration aus logging_setup
# =============================================================================

logger = get_logger(__name__)


# =============================================================================
# KONFIGURATION - Importiert aus simulation_config.py
# =============================================================================
# SimulationConfig und DEFAULT_CONFIG sind nun in simulation_config.py definiert
# und werden am Anfang dieser Datei importiert.


# =============================================================================
# COMMAND SYSTEM - Deklarative Steuerung ohne Warteschleifen
# =============================================================================

class CommandType(Enum):
    """Typ der Steuerkommandos."""
    SET_STATE = auto()  # Setze State-Attribut direkt
    WAIT_CONDITION = auto()  # Warte auf Bedingung
    EXECUTE_FUNC = auto()  # Führe Funktion aus
    LOG_MESSAGE = auto()  # Gebe Nachricht aus


@dataclass
class Command:
    """
    Einzelnes Steuerkommando.

    Statt Warteschleifen definierst du eine Sequenz von Commands.
    Die Simulation führt diese automatisch aus.
    """
    type: CommandType
    target: Optional[str] = None  # State-Attribut (für SET_STATE)
    value: Optional[Any] = None  # Wert (für SET_STATE)
    condition: Optional[Callable[[UfoState], bool]] = None  # Bedingung (für WAIT_CONDITION)
    func: Optional[Callable] = None  # Funktion (für EXECUTE_FUNC)
    message: Optional[str] = None  # Nachricht (für LOG_MESSAGE)
    timeout: Optional[float] = None  # Timeout für WAIT_CONDITION


class CommandQueue:
    """
    Command Queue für deklarative Autopilot-Steuerung.

    Statt:
        while sim.state.z < 10:
            time.sleep(0.05)

    Schreibe:
        queue.wait_until(lambda s: s.z >= 10)

    Die Simulation führt Commands automatisch aus, wenn Bedingungen erfüllt sind.
    """

    def __init__(self):
        """Initialisiert eine leere Command Queue."""
        self.commands: List[Command] = []
        self.current_index: int = 0
        self._lock = threading.RLock()
        self._completed = threading.Event()

    @property
    def lock(self) -> threading.RLock:
        """Interner Lock für threadsicheren Zugriff."""
        return self._lock

    def set_state(self, attribute: str, value: Any) -> 'CommandQueue':
        """
        Setze State-Attribut.

        Example:
            >>> CommandQueue().set_state('i', 90).set_state('delta_v', 10)
        """
        self.commands.append(Command(
            type=CommandType.SET_STATE,
            target=attribute,
            value=value
        ))
        return self

    def wait_until(
            self,
            condition: Callable[[UfoState], bool],
            timeout: Optional[float] = None
    ) -> 'CommandQueue':
        """
        Warte bis Bedingung erfüllt (OHNE Schleife!).

        Example:
            >>> queue = CommandQueue()
            >>> queue..wait_until(lambda s: s.z >= 10.0)
        """
        self.commands.append(Command(
            type=CommandType.WAIT_CONDITION,
            condition=condition,
            timeout=timeout
        ))
        return self

    def execute(self, func: Callable) -> 'CommandQueue':
        """
        Führe Funktion aus.

        Example:
            >>> CommandQueue().execute(lambda: print("Checkpoint!"))
        """
        self.commands.append(Command(
            type=CommandType.EXECUTE_FUNC,
            func=func
        ))
        return self

    def log(self, message: str) -> 'CommandQueue':
        """
        Gebe Log-Nachricht aus.

        Example:
            >>> CommandQueue().log("Takeoff started")
        """
        self.commands.append(Command(
            type=CommandType.LOG_MESSAGE,
            message=message
        ))
        return self

    @synchronized
    def is_completed(self) -> bool:
        """Prüft ob alle Commands ausgeführt wurden."""
        return self.current_index >= len(self.commands)

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wartet bis alle Commands ausgeführt wurden.

        Returns:
            True wenn completed, False bei Timeout
        """
        return self._completed.wait(timeout=timeout)

    def mark_completed(self) -> None:
        """Markiert Queue als vollständig ausgeführt."""
        self._completed.set()


# =============================================================================
# COMMAND EXECUTOR - Event-basierte Command-Verarbeitung
# =============================================================================

class CommandExecutor:
    """
    Executor für Command Queues - entkoppelt von Simulationsloop.

    Verarbeitet Commands event-basiert wenn sich der State ändert.
    Läuft in separatem Thread für vollständige Isolation.
    """

    def __init__(self, state_manager: StateManager):
        """
        Initialisiert CommandExecutor mit StateManager.

        Args:
            state_manager: StateManager zur State-Überwachung
        """
        self._state_manager = state_manager
        self._active_queue: Optional[CommandQueue] = None
        self._lock = threading.RLock()
        logger.debug("CommandExecutor initialized")

    @synchronized
    def set_active_queue(self, queue: CommandQueue) -> None:
        """
        Setzt aktive Command Queue.

        Args:
            queue: Auszuführende CommandQueue
        """
        self._active_queue = queue
        logger.info(f"CommandQueue activated with {len(queue.commands)} commands")

    @synchronized
    def clear_active_queue(self) -> None:
        """Entfernt aktive Queue."""
        self._active_queue = None
        logger.debug("CommandQueue cleared")

    @synchronized
    def process_commands(self, current_state: UfoState) -> None:
        """
        Verarbeitet Commands der aktiven Queue basierend auf aktuellem State.

        Args:
            current_state: Aktueller State für Bedingungsprüfung
        """
        if self._active_queue is None or self._active_queue.is_completed():
            return

        queue = self._active_queue

        with queue.lock:
            # Verarbeite aktuellen Command
            if queue.current_index < len(queue.commands):
                cmd = queue.commands[queue.current_index]

                # SET_STATE: Direkt ausführen
                if cmd.type == CommandType.SET_STATE:
                    self._execute_set_state(cmd)
                    queue.current_index += 1

                # LOG_MESSAGE: Direkt ausführen
                elif cmd.type == CommandType.LOG_MESSAGE:
                    print(cmd.message)
                    logger.debug(f"Command executed: LOG {cmd.message}")
                    queue.current_index += 1

                # EXECUTE_FUNC: Direkt ausführen
                elif cmd.type == CommandType.EXECUTE_FUNC:
                    if cmd.func: cmd.func()
                    logger.debug("Command executed: FUNC")
                    queue.current_index += 1

                # WAIT_CONDITION: Prüfe Bedingung
                elif cmd.type == CommandType.WAIT_CONDITION:
                    if cmd.condition is not None and cmd.condition(current_state):
                        logger.debug("Command executed: WAIT condition fulfilled")
                        queue.current_index += 1

            # Prüfe ob Queue fertig
            if queue.current_index >= len(queue.commands):
                queue.mark_completed()
                logger.info("CommandQueue completed")
                self._active_queue = None

    def _execute_set_state(self, cmd: Command) -> None:
        """
        Führt SET_STATE Command aus.

        Args:
            cmd: Command mit target und value
        """

        def update(state: UfoState) -> UfoState:
            return dataclass_replace(state, **{cmd.target: cmd.value})

        self._state_manager.update_state(update)
        logger.debug(f"Command executed: SET {cmd.target}={cmd.value}")


# =============================================================================
# VIEWPORT - Dynamisches Zoom-System
# =============================================================================

@dataclass
class UfoViewport:
    """
    Viewport- und Skalierungslogik für die UFO-Karte.

    Berechnet dynamisch den Zoom-Faktor basierend auf Start- und Zielpunkten,
    sodass alle relevanten Punkte im Fenster sichtbar bleiben.
    """

    width: int
    height: int
    config: SimulationConfig = DEFAULT_CONFIG
    scaling: int = None

    def __post_init__(self) -> None:
        """Initialisiert scaling falls nicht gesetzt."""
        if self.scaling is None:
            self.scaling = self.config.view_min_scaling

    def configure_for_points(self, points: List[Tuple[float, float]]) -> None:
        """
        Bestimmt die optimale Skalierung aus einer Menge von Punkten.

        Args:
            points: Liste von (x, y)-Koordinaten in Metern.
        """
        final_scaling = self.config.view_min_scaling

        if points:
            max_abs_x = max(abs(x) for x, _ in points) or self.config.min_coordinate_epsilon
            max_abs_y = max(abs(y) for _, y in points) or self.config.min_coordinate_epsilon

            half_w = self.width * self.config.view_margin_factor / 2.0
            half_h = self.height * self.config.view_margin_factor / 2.0

            scale_x = half_w / max_abs_x
            scale_y = half_h / max_abs_y

            s = min(scale_x, scale_y)
            final_scaling = max(self.config.view_min_scaling, min(int(s), self.config.view_max_scaling))

        self.scaling = final_scaling

    def to_screen(self, x: float, y: float) -> Tuple[float, float]:
        """
        Wandelt Weltkoordinaten (x, y) in Bildschirmkoordinaten (px, py) um.

        Args:
            x: X-Koordinate in Metern
            y: Y-Koordinate in Metern

        Returns:
            Tupel (px, py) in Pixelkoordinaten
        """
        cx = self.width / 2.0
        cy = self.height / 2.0
        px = cx + x * self.scaling
        py = cy - y * self.scaling
        return px, py


# =============================================================================
# STATE MANAGER - Thread-sichere Zustandsverwaltung (Legacy)
# =============================================================================

class _UfoLegacyStateManager:
    """
    Thread-sicherer Manager für UFO-Zustand (Legacy-Implementierung).

    DEPRECATED: Wird durch StateManager aus state.manager ersetzt.
    Nur für Abwärtskompatibilität mit altem Code beibehalten.

    Kapselt Zugriff auf UfoState und bietet Event-System für Änderungsbenachrichtigungen.
    Implementiert Observer-Pattern für Listener-Registrierung.
    
    Refactored für frozen UfoState: update_state() akzeptiert Funktionen, die neuen State zurückgeben.
    """

    def __init__(self, initial_state: Optional['UfoState'] = None):
        """
        Initialisiert StateManager mit optionalem Anfangszustand.

        Args:
            initial_state: Optionaler initialer Zustand (Standard: neuer UfoState())
        """
        self._state: UfoState = initial_state if initial_state is not None else UfoState()
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._observers: List[Callable[[UfoState], None]] = []
        logger.debug("StateManager initialized")

    @synchronized
    def get_snapshot(self) -> 'UfoState':
        """
        Gibt thread-sicheren Snapshot des aktuellen Zustands zurück.

        Returns:
            Kopie des aktuellen UfoState
        """
        return dataclass_replace(self._state)

    def update_state(self, update_func: Callable[['UfoState'], 'UfoState']) -> None:
        """
        Führt atomare State-Aktualisierung aus und benachrichtigt Observer.

        Args:
            update_func: Funktion die neuen State zurückgibt (immutable Pattern)
        """
        # Kritischer Abschnitt unter @conditional
        snapshot = self._update_state_atomic(update_func)

        # Benachrichtige Observer außerhalb Lock (Deadlock-Vermeidung)
        self._notify_observers(snapshot)

    @conditional
    def _update_state_atomic(self, update_func: Callable[['UfoState'], 'UfoState']) -> 'UfoState':
        """Atomarer State-Update unter Condition-Lock (verhindert nested lock)."""
        self._state = update_func(self._state)
        self._condition.notify_all()  # Kein nested lock dank @conditional
        return dataclass_replace(self._state)

    def _notify_observers(self, snapshot: 'UfoState') -> None:
        """
        Benachrichtigt alle registrierten Observer über State-Änderung.

        Args:
            snapshot: Snapshot des neuen Zustands
        """
        for observer in self._observers:
            try:
                observer(snapshot)
            except Exception as e:  # noqa: BLE001 - Breiter Catch bewusst: Observer können beliebige Exceptions werfen, dürfen aber andere Observer nicht blockieren
                logger.exception(f"Observer notification failed: {e}")

    @synchronized
    def register_observer(self, observer: Callable[['UfoState'], None]) -> None:
        """
        Registriert Observer für State-Änderungen.

        Args:
            observer: Callable das bei jeder Änderung aufgerufen wird
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observer registered, total: {len(self._observers)}")

    @synchronized
    def unregister_observer(self, observer: Callable[['UfoState'], None]) -> None:
        """
        Entfernt Observer aus Benachrichtigungsliste.

        Args:
            observer: Zu entfernender Observer
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"Observer unregistered, remaining: {len(self._observers)}")

    def wait_for_condition(
            self,
            condition: Callable[['UfoState'], bool],
            timeout: Optional[float] = None
    ) -> bool:
        """
        Wartet bis Bedingung erfüllt ist (event-basiert, kein Busy-Waiting).

        Args:
            condition: Bedingung die State prüft
            timeout: Optionales Timeout in Sekunden

        Returns:
            True wenn Bedingung erfüllt, False bei Timeout
        """
        # Delegation an zentrale ConditionWaiter-Utility
        from .utils.condition_waiter import ConditionWaiter

        return ConditionWaiter.wait_for_condition(
            condition_var=self._condition,
            predicate=condition,
            state_getter=lambda: self._state,
            timeout=timeout
        )


    def reset(self) -> None:
        """Setzt State auf Ausgangszustand zurück."""
        self._reset_atomic()

    @conditional
    def _reset_atomic(self) -> None:
        """Atomarer State-Reset unter Condition-Lock (verhindert nested lock)."""
        self._state = UfoState()
        self._condition.notify_all()  # Kein nested lock dank @conditional
        logger.debug("State reset")

    @property
    def state(self) -> 'UfoState':
        """
        Direkter Zugriff auf internen State (NICHT thread-sicher!).

        Nur für Legacy-Kompatibilität. Verwende get_snapshot() oder update_state().
        """
        return self._state


# =============================================================================
# SIMULATION CONTROLLER - Orchestrierung ohne Implementierung
# =============================================================================

class UfoSim:
    """
    Schlanker Controller für UFO-Simulation.

    Orchestriert Komponenten ohne eigene Implementierung:
    - StateManager für Thread-Safety
    - PhysicsEngine für Berechnungen
    - CommandExecutor für Autopilot
    - StateObserver für Manöver-Analyse

    Verantwortlich nur für:
    - Komponenten-Initialisierung
    - Thread-Management
    - Logging-Koordination
    - Public API
    """

    __version__ = "5.2.0-tw-refactored"
    __author__ = "tomtastisch (i-ki 1)"
    __release_date__ = "2025-01-15"

    def __init__(self, config: SimulationConfig = DEFAULT_CONFIG) -> None:
        """
        Initialisiert Simulation durch Komponenten-Komposition.

        Args:
            config: Simulations-Konfiguration (Standard: DEFAULT_CONFIG)
        """
        self.config = config

        # Komponenten
        self._state_manager = StateManager()
        self._physics_engine = PhysicsEngine(config)
        self._command_executor = CommandExecutor(self._state_manager)
        self.observer = StateObserver(config)

        # Registriere Observer als Listener für State-Änderungen
        self._state_manager.register_observer(self.observer.observe)

        # Runtime-State
        self.__speedup = int(config.one_value)
        self.__running = False
        self.__logging_enabled = False
        self.__log_interval_s = 1.0
        self.__log_every_step = False
        self.__last_log_time = 0.0
        self.__destinations: List[Tuple[float, float]] = []

        # Threading
        self._view: Optional['UfoPView'] = None
        self._sim_thread: Optional[threading.Thread] = None
        self._autopilot_thread: Optional[threading.Thread] = None

        logger.info(f"UfoSim v{self.__version__} initialized with config: dt={config.dt}s, vmax={config.vmax_kmh}km/h")

    def reset(self) -> None:
        """Setzt die Simulation auf den Ausgangszustand zurück."""
        self.__running = False
        self._state_manager.reset()
        self.observer = StateObserver(self.config)
        self._state_manager.register_observer(self.observer.observe)
        logger.info("Simulation reset")

    @property
    def speedup(self) -> int:
        """Aktueller Beschleunigungsfaktor."""
        return self.__speedup

    @property
    def is_running(self) -> bool:
        """Gibt an, ob die Simulation noch aktiv läuft."""
        return self.__running

    @property
    def state(self) -> StateProxy:
        """
        Legacy-kompatibler Proxy: erlaubt `sim.state.x = ...` bei frozen UfoState.

        Lesezugriffe geben Werte aus einem Snapshot zurück, Schreibzugriffe werden
        an den StateManager delegiert und erzeugen einen neuen UfoState via
        dataclass_replace.
        """
        return StateProxy(self._state_manager)

    def get_phase(self) -> Phase:
        """
        Gibt die aktuelle Flugphase threadsicher zurück.

        Returns:
            Aktuelle Phase als Literal-String
        """
        snap = self.get_state_snapshot()
        return compute_phase(snap, self.config)

    def get_maneuver_analysis(self) -> ManeuverAnalysis:
        """
        Gibt eine vollständige Manöver-Analyse zurück.

        Returns:
            ManeuverAnalysis mit Phase und Bewegungs-Flags
        """
        return self.observer.analyze()

    def get_maneuver_description(self) -> str:
        """
        Gibt eine lesbare Beschreibung des aktuellen Manövers zurück.

        Returns:
            String-Beschreibung des Manövers
        """
        return self.observer.get_maneuver_description()

    def get_destinations(self) -> List[Tuple[float, float]]:
        """
        Gibt die Liste der Zielkoordinaten zurück.

        Returns:
            Liste von (x, y) Tupeln in Metern
        """
        return self.__destinations

    def wait_for_condition(
            self,
            condition: Callable[[UfoState], bool],
            timeout: Optional[float] = None
    ) -> bool:
        """
        Wartet bis eine Bedingung erfüllt ist, ohne busy-waiting.

        Args:
            condition: Callable das den State prüft und bool zurückgibt
            timeout: Optional - Maximale Wartezeit in Sekunden (None = unbegrenzt)

        Returns:
            True wenn Bedingung erfüllt, False bei Timeout
        """
        return self._state_manager.wait_for_condition(condition, timeout)

    @final
    def create_command_queue(self) -> CommandQueue:
        """
        Erstellt eine neue Command Queue für deklarative Steuerung.

        Returns:
            CommandQueue zum Definieren von Aktionen

        Example:
            >>> sim = UfoSim()
            >>> queue = sim.create_command_queue()
            >>> queue.wait_until(lambda s: s.z >= 10.0)
        """
        return CommandQueue()

    def execute_command_queue(self, queue: CommandQueue) -> None:
        """
        Führt Command Queue aus (setzt sie als aktive Queue).

        Args:
            queue: CommandQueue mit definierten Aktionen
        """
        self._command_executor.set_active_queue(queue)

    @overload
    def start(self) -> None:
        """Startet die Simulation mit Default-Parametern."""
        ...

    @overload
    def start(
            self,
            speedup: int,
            *,
            destinations: Optional[List[Tuple[float, float]]] = None,
            show_view: bool = False,
            enable_logging: bool = True,
            log_interval_s: float = 1.0,
            log_every_step: bool = False,
            autopilot_callback: Optional[callable] = None,
    ) -> None:
        """Startet die Simulation mit angegebenem Speedup-Faktor."""
        ...

    def start(
            self,
            speedup: int = None,
            *,
            destinations: Optional[List[Tuple[float, float]]] = None,
            show_view: bool = False,
            enable_logging: bool = True,
            log_interval_s: float = 1.0,
            log_every_step: bool = True,
            autopilot_callback: Optional[callable] = None,
    ) -> None:
        """
        Startet die Simulation.

        Args:
            speedup: Faktor zur Beschleunigung der Simulation (1–25). None = Default aus Config.
            destinations: Liste von Zielkoordinaten (x, y) in Metern. Standard: [(0.0, 0.0)]
            show_view: False → Headless, True → Visualisierung mit PyQt.
            enable_logging: Aktiviert kontinuierliche Telemetrie-Ausgabe auf stdout.
            log_interval_s: Intervall für Logging-Ausgaben in Sekunden (Echtzeit). Wird ignoriert wenn log_every_step=True.
            log_every_step: Wenn True, wird jeder Simulationsschritt geloggt (sehr detailliert).
            autopilot_callback: Optional - Funktion die mit (sim) aufgerufen wird im separaten Thread.
        """
        final_destinations = destinations if destinations is not None else [(0.0, 0.0)]
        final_speedup = speedup if speedup is not None else self.config.speedup_default

        if not (self.config.speedup_min <= final_speedup <= self.config.speedup_max):
            logger.warning(
                f"speedup {final_speedup} outside valid range [{self.config.speedup_min}, {self.config.speedup_max}], using default")
            final_speedup = self.config.speedup_default

        self.__speedup = final_speedup
        self.__running = True
        self.__logging_enabled = enable_logging
        self.__log_interval_s = log_interval_s
        self.__log_every_step = log_every_step
        self.__last_log_time = 0.0
        self.__destinations = final_destinations

        logger.info(
            f"Starting simulation: speedup={self.__speedup}, destinations={len(final_destinations)}, show_view={show_view}, log_every_step={log_every_step}")

        # Wenn keine View, ist Thread nicht-daemon damit er nicht abgebrochen wird
        sim_thread = threading.Thread(target=self.__run_sim, daemon=show_view)
        sim_thread.start()
        self._sim_thread = sim_thread

        if autopilot_callback is not None:
            self._autopilot_thread = threading.Thread(
                target=autopilot_callback,
                args=(self,),
                daemon=True
            )
            self._autopilot_thread.start()
            logger.info("Autopilot thread started")

        if show_view:
            app = QtWidgets.QApplication.instance()
            owns_app = app is None

            if owns_app:
                app = QtWidgets.QApplication([])

            self._view = UfoPView(self, destinations=final_destinations)

            if owns_app:
                app.exec_()
        else:
            # Headless mode: Warte bis Simulation fertig ist
            sim_thread.join()

    def __run_sim(self) -> None:
        """
        Führt die Simulationsberechnungen in einer Endlosschleife aus.

        Delegiert alle Berechnungen an PhysicsEngine und StateManager.
        """
        while self.__running:
            # Physik-Step ausführen über StateManager
            def physics_update(state: UfoState) -> UfoState:
                updated_state, should_continue, _ = self._physics_engine.integrate_step(state)
                if not should_continue:
                    self.__running = False
                return updated_state

            self._state_manager.update_state(physics_update)

            # Command Queue verarbeiten
            current_snapshot = self._state_manager.get_snapshot()
            self._command_executor.process_commands(current_snapshot)

            # Logging: entweder jeden Schritt oder zeitbasiert
            if self.__logging_enabled:
                if self.__log_every_step:
                    print(self.format_flight_data())
                else:
                    current_time = time.time()
                    if current_time - self.__last_log_time >= self.__log_interval_s:
                        print(self.format_flight_data())
                        self.__last_log_time = current_time

            time.sleep(self.config.dt / max(1, self.__speedup))

    def terminate(self) -> None:
        """Beendet die Simulation."""
        self.__running = False

    def get_state_snapshot(self) -> UfoState:
        """Gibt einen threadsicheren Schnappschuss des aktuellen Zustands zurück."""
        return self._state_manager.get_snapshot()

    def format_flight_data(self) -> str:
        """
        Formatierte Telemetrie für Logging-Ausgaben.

        Enthält Position, Geschwindigkeit, Phase und Manöver-Analyse.
        Verwendet NumPy für effiziente Beschleunigungsberechnung.

        Returns:
            Formatierter String mit allen relevanten Flugdaten
        """
        snap = self.get_state_snapshot()
        analysis = self.observer.analyze()

        # Berechne Gesamtbeschleunigung mit NumPy (L2-Norm)
        total_accel = np.linalg.norm(snap.acceleration_vector)

        # Manöver-Flags als kompakte Darstellung
        flags = []
        if analysis.is_ascending:
            flags.append("↑")
        elif analysis.is_descending:
            flags.append("↓")
        if analysis.is_turning:
            flags.append("↻")
        if analysis.is_stagnating:
            flags.append("⊗")
        flags_str = "".join(flags) if flags else "-"

        return (
            f"{snap.ftime:6.1f}s: "
            f"pos=({snap.x:6.1f}, {snap.y:6.1f}, {snap.z:5.1f})m | "
            f"v={snap.v:3.0f}km/h, d={snap.d:3.0f}°, i={snap.i:4.0f}° | "
            f"phase={analysis.phase:>8s} [{flags_str}] | "
            f"dist={snap.dist:6.1f}m, vz={snap.vz:5.2f}m/s, a={total_accel:5.2f}m/s²"
        )


# =============================================================================
# VIEW MODEL - Entkopplung zwischen Simulation und Visualisierung
# =============================================================================

@dataclass
class SimulationViewModel:
    """
    View-Model (DTO) für Visualisierung.

    Entkoppelt View von direktem Zugriff auf Simulation.
    Enthält nur Daten die für Rendering benötigt werden.
    """
    # State
    position: Tuple[float, float, float]  # (x, y, z) in m
    velocity_kmh: float
    direction_deg: float
    inclination_deg: float
    distance_m: float
    flight_time_s: float

    # Analyse
    phase: Phase
    is_running: bool

    @classmethod
    def from_simulation(cls, sim: UfoSim) -> 'SimulationViewModel':
        """
        Erstellt ViewModel aus Simulation.

        Args:
            sim: UfoSim Instanz

        Returns:
            SimulationViewModel mit aktuellen Daten
        """
        snap = sim.get_state_snapshot()
        phase = compute_phase(snap, sim.config)

        return cls(
            position=(snap.x, snap.y, snap.z),
            velocity_kmh=snap.v,
            direction_deg=snap.d,
            inclination_deg=snap.i,
            distance_m=snap.dist,
            flight_time_s=snap.ftime,
            phase=phase,
            is_running=sim.is_running
        )


# =============================================================================
# HUD HELPER - Reduziert Boilerplate
# =============================================================================

def create_circle_item(
        color: str,
        z_value: int,
) -> QtWidgets.QGraphicsEllipseItem:
    """
    Erstellt ein kreisförmiges Graphics-Item.

    Args:
        color: Farbe als String (z.B. "white", "blue")
        z_value: Z-Order für Rendering-Reihenfolge

    Returns:
        Konfiguriertes QGraphicsEllipseItem (Größe muss vom Caller gesetzt werden)
    """
    item = QtWidgets.QGraphicsEllipseItem(0.0, 0.0, 0.0, 0.0)
    item.setBrush(QtGui.QBrush(QtGui.QColor(color)))
    item.setPen(QtGui.QPen(QtGui.QColor(color)))
    item.setZValue(z_value)
    return item


def create_text_item(color: str, z_value: int) -> QtWidgets.QGraphicsSimpleTextItem:
    """
    Erstellt ein Text-Graphics-Item.

    Args:
        color: Textfarbe als String
        z_value: Z-Order für Rendering-Reihenfolge

    Returns:
        Konfiguriertes QGraphicsSimpleTextItem
    """
    item = QtWidgets.QGraphicsSimpleTextItem("")
    item.setBrush(QtGui.QBrush(QtGui.QColor(color)))
    item.setZValue(z_value)
    return item


# =============================================================================
# VIEW - Effiziente Visualisierung mit QGraphicsScene
# =============================================================================

class UfoPView(QtWidgets.QGraphicsView):
    """
    PyQt5-basierte Ansicht für die UFO-Simulation mit QGraphicsScene.

    Features:
        - Effiziente Darstellung mit Pixmap-Items
        - ViewModel für Datenabstraktion
        - Feste Fenstergröße, dynamische Kartenskalierung
        - Crash-Bild bei Absturz
        - Automatischer Shutdown nach Landung/Crash
    """

    def __init__(
            self,
            simulation: UfoSim,
            destinations: Optional[List[Tuple[float, float]]] = None,
    ) -> None:

        super().__init__()

        self.sim = simulation
        self.config = simulation.config
        self.destinations = destinations if destinations is not None else []

        self.viewport_model = UfoViewport(
            width=self.config.window_size,
            height=self.config.window_size,
            config=self.config,
        )

        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform
        )
        self.setFixedSize(self.config.window_size, self.config.window_size)
        self.setSceneRect(0.0, 0.0, self.config.window_size, self.config.window_size)
        self.setWindowTitle("Drohnenflug Simulationsvisualisierung - by Tom Werner")

        self.__package_dir = Path(__file__).parent

        icon_path = self.__package_dir / "thi_icon_258.png"
        if icon_path.is_file():
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))

        map_image = self._load_image("resources/background_card.png")
        ufo_image = self._load_image("resources/ufo_icon.png")
        crash_image = self._load_image("resources/sim_crash.png")

        self.__map_pixmap = QtGui.QPixmap.fromImage(map_image).scaled(
            self.config.window_size,
            self.config.window_size,
            QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self.__ufo_pixmap = QtGui.QPixmap.fromImage(ufo_image)
        self.__crash_pixmap = QtGui.QPixmap.fromImage(crash_image).scaled(
            self.config.window_size,
            self.config.window_size,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )

        points = [(0.0, 0.0)] + list(self.destinations)
        self.viewport_model.configure_for_points(points)

        self._create_scene_items()

        self._shutdown_scheduled = False
        self._closing = False
        self._crash_displayed = False

        self.show()

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self._update)
        self.update_timer.start(self.config.update_interval_ms)

        logger.info(f"View initialized: window_size={self.config.window_size}, scaling={self.viewport_model.scaling}")

    def _load_image(self, filename: str) -> QtGui.QImage:
        """Lädt ein Bild aus dem aktuellen Verzeichnis."""
        image_path = self.__package_dir / filename
        image = QtGui.QImage(str(image_path))

        if image.isNull():
            raise FileNotFoundError(f"Image not found: {filename}")

        return image

    def _create_scene_items(self) -> None:
        """Erstellt alle Scene-Items EINMALIG."""
        self._background_item = QtWidgets.QGraphicsPixmapItem(self.__map_pixmap)
        self._background_item.setZValue(-100)
        self.scene.addItem(self._background_item)

        self._start_item = create_circle_item("white", 0)
        self.scene.addItem(self._start_item)

        self._dest_items: List[Tuple[QtWidgets.QGraphicsEllipseItem, QtWidgets.QGraphicsEllipseItem]] = []
        for _ in self.destinations:
            outer = create_circle_item("white", 1)
            self.scene.addItem(outer)

            inner = create_circle_item("black", 2)
            self.scene.addItem(inner)

            self._dest_items.append((outer, inner))

        self._ufo_item = QtWidgets.QGraphicsPixmapItem(self.__ufo_pixmap)
        self._ufo_item.setZValue(10)
        self.scene.addItem(self._ufo_item)

        self._ufo_dot_item = create_circle_item("blue", 11)
        self.scene.addItem(self._ufo_dot_item)

        info_labels = ["status", "x", "y", "z", "v", "d", "i", "dist", "time"]
        self._info_items: List[QtWidgets.QGraphicsSimpleTextItem] = []
        for _ in info_labels:
            item = create_text_item("black", 20)
            self.scene.addItem(item)
            self._info_items.append(item)

        self._scale_text_item = create_text_item("black", 20)
        self.scene.addItem(self._scale_text_item)

        self._scale_line_item = QtWidgets.QGraphicsLineItem()
        self._scale_line_item.setPen(QtGui.QPen(QtGui.QColor("black")))
        self._scale_line_item.setZValue(20)
        self.scene.addItem(self._scale_line_item)

    def _update(self) -> None:
        """
        Aktualisiert alle Items - verwendet ViewModel statt direkten State-Zugriff.

        Vorteile:
        - Entkoppelt View von Simulation-Internals
        - Nur eine API-Abfrage pro Frame
        - Klare Datenstruktur
        """
        if self._closing:
            return

        # Hole ViewModel (einziger Zugriff auf Simulation!)
        view_model = SimulationViewModel.from_simulation(self.sim)

        if view_model.phase == "crashed" and not self._crash_displayed:
            self._show_crash_screen()
            return

        # Render Start/Dest Marker
        start_px, start_py = self.viewport_model.to_screen(0.0, 0.0)
        r = self.config.hud_start_radius
        self._start_item.setRect(start_px - r, start_py - r, 2 * r, 2 * r)

        outer_r = self.config.hud_dest_out_radius
        inner_r = self.config.hud_dest_in_radius
        for (dx, dy), (outer_item, inner_item) in zip(self.destinations, self._dest_items):
            px, py = self.viewport_model.to_screen(dx, dy)
            outer_item.setRect(px - outer_r, py - outer_r, 2 * outer_r, 2 * outer_r)
            inner_item.setRect(px - inner_r, py - inner_r, 2 * inner_r, 2 * inner_r)

        # Render UFO
        x, y, z = view_model.position
        ux, uy = self.viewport_model.to_screen(x, y)
        ufo_w = self.__ufo_pixmap.width()
        ufo_h = self.__ufo_pixmap.height()
        self._ufo_item.setPos(ux - ufo_w / 2.0, uy - ufo_h / 2.0)

        dot_r = self.config.hud_ufo_dot_radius
        self._ufo_dot_item.setRect(ux - dot_r, uy - dot_r, 2 * dot_r, 2 * dot_r)

        # Render HUD Text
        info_lines = [
            f"ufo:  {view_model.phase:>8s}",
            f"x:    {x:6.1f} m   ",
            f"y:    {y:6.1f} m   ",
            f"z:    {z:6.1f} m   ",
            f"v:     {view_model.velocity_kmh:3.0f}   km/h",
            f"d:     {view_model.direction_deg:3.0f}   deg ",
            f"i:     {view_model.inclination_deg:3.0f}   deg ",
            f"dist: {view_model.distance_m:6.1f} m   ",
            f"time: {view_model.flight_time_s:6.1f} s   ",
        ]

        for line, item in zip(info_lines, self._info_items):
            item.setText(line)

        margin = self.config.hud_text_margin
        y_base = self.config.window_size - margin

        for idx_rev, item in enumerate(reversed(self._info_items)):
            rect = item.boundingRect()
            x_pos = self.config.window_size - margin - rect.width()
            y_pos = y_base - idx_rev * self.config.hud_text_line_height - rect.height()
            item.setPos(x_pos, y_pos)

        # Render Scale
        scale_text = f"{int(self.config.hud_scale_length_m)} m"
        self._scale_text_item.setText(scale_text)
        rect = self._scale_text_item.boundingRect()
        text_x = margin
        text_y = self.config.window_size - margin - rect.height()
        self._scale_text_item.setPos(text_x, text_y)

        line_y = self.config.window_size - margin - rect.height() - 2.0
        line_x1 = margin
        line_length_px = self.config.hud_scale_length_m * self.viewport_model.scaling
        line_x2 = min(line_x1 + line_length_px, self.config.window_size - margin)
        self._scale_line_item.setLine(line_x1, line_y, line_x2, line_y)

        # Shutdown nach Ende
        if not view_model.is_running and not self._shutdown_scheduled and not self._crash_displayed:
            self._shutdown_scheduled = True
            self.update_timer.stop()
            QtCore.QTimer.singleShot(self.config.shutdown_delay_ms, self._shutdown_after_sim)

    def _show_crash_screen(self) -> None:
        """Zeigt das Crash-Bild an und plant automatisches Shutdown."""
        self._crash_displayed = True
        self.update_timer.stop()

        self.scene.clear()

        crash_item = QtWidgets.QGraphicsPixmapItem(self.__crash_pixmap)
        crash_item.setZValue(1000)

        x_offset = (self.config.window_size - self.__crash_pixmap.width()) / 2.0
        y_offset = (self.config.window_size - self.__crash_pixmap.height()) / 2.0
        crash_item.setPos(x_offset, y_offset)

        self.scene.addItem(crash_item)

        logger.warning("Crash screen displayed")
        QtCore.QTimer.singleShot(self.config.crash_display_duration_ms, self._shutdown_after_sim)

    def _shutdown_after_sim(self) -> None:
        """Schließt die View nach Simulationsende."""
        self.close()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Behandelt das Schließen des Fensters."""
        self._closing = True

        if hasattr(self, "update_timer") and self.update_timer.isActive():
            self.update_timer.stop()
            try:
                self.update_timer.timeout.disconnect(self._update)
            except (RuntimeError, TypeError):
                pass

        self.sim.terminate()
        event.accept()


class StateProxy:
    """Legacy-kompatibler Proxy: erlaubt `sim.state.x = ...` bei frozen UfoState.

    Lesezugriffe geben Werte aus einem Snapshot zurück, Schreibzugriffe werden
    an den StateManager delegiert und erzeugen einen neuen UfoState via
    dataclass_replace.
    """

    def __init__(self, manager: 'StateManager') -> None:
        object.__setattr__(self, "_manager", manager)

    def __getattr__(self, name: str):
        snap = self._manager.get_snapshot()
        if hasattr(snap, name):
            return getattr(snap, name)
        raise AttributeError(name)

    def __setattr__(self, name: str, value) -> None:
        def updater(state: UfoState) -> UfoState:
            try:
                return dataclass_replace(state, **{name: value})
            except (AttributeError, TypeError):  # noqa: BLE001 - Breiter Catch bewusst: AttributeError oder TypeError möglich
                return state

        self._manager.update_state(updater)

    def __repr__(self) -> str:  # pragma: no cover - convenience
        snap = self._manager.get_snapshot()
        return f"StateProxy({snap})"


__all__ = [
    # Simulation (Hauptklasse)
    "UfoSim",

    # Config
    "SimulationConfig",
    "DEFAULT_CONFIG",

    # State & Phase
    "UfoState",
    "Phase",

    # Manöver-Analyse (für Autopilot)
    "ManeuverAnalysis",
]

