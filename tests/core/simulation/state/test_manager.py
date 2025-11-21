#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit-Tests für StateManager (state/manager.py)."""

import threading
import time
from dataclasses import replace

import pytest

from core.simulation.state import StateManager, UfoState


class TestStateManagerInitialization:
    """Tests für StateManager-Initialisierung."""

    def test_default_initialization(self):
        """StateManager initialisiert mit Default-UfoState."""
        manager = StateManager()
        snapshot = manager.get_snapshot()
        
        assert snapshot.x == 0.0
        assert snapshot.y == 0.0
        assert snapshot.z == 0.0
        assert snapshot.v == 0.0

    def test_custom_initial_state(self):
        """StateManager akzeptiert custom initial State."""
        initial_state = UfoState(x=10.0, y=20.0, z=30.0, v=50.0)
        manager = StateManager(initial_state=initial_state)
        snapshot = manager.get_snapshot()
        
        assert snapshot.x == 10.0
        assert snapshot.y == 20.0
        assert snapshot.z == 30.0
        assert snapshot.v == 50.0


class TestStateManagerSnapshot:
    """Tests für get_snapshot()-Methode."""

    def test_get_snapshot_returns_copy(self):
        """get_snapshot() liefert defensive Kopie."""
        manager = StateManager()
        snapshot1 = manager.get_snapshot()
        snapshot2 = manager.get_snapshot()
        
        # Beide Snapshots sind Kopien, nicht dasselbe Objekt
        assert snapshot1 is not snapshot2
        
        # Aber sie haben dieselben Werte
        assert snapshot1.x == snapshot2.x
        assert snapshot1.z == snapshot2.z

    def test_snapshot_is_immutable(self):
        """Snapshot ist immutable (frozen dataclass)."""
        manager = StateManager()
        snapshot = manager.get_snapshot()
        
        # Frozen dataclass wirft AttributeError bei direkter Änderung
        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            snapshot.x = 100.0  # type: ignore[misc,assignment]

    def test_snapshot_does_not_affect_manager_state(self):
        """Snapshot-Modifikation beeinflusst Manager-State nicht."""
        manager = StateManager()
        snapshot1 = manager.get_snapshot()
        
        # Neuen State aus Snapshot erstellen (replace)
        modified = replace(snapshot1, x=999.0)
        
        # Manager-State ist unverändert
        snapshot2 = manager.get_snapshot()
        assert snapshot2.x == 0.0
        assert modified.x == 999.0


class TestStateManagerUpdate:
    """Tests für update_state()-Methode."""

    def test_update_state_applies_function(self):
        """update_state() wendet Funktion auf State an."""
        manager = StateManager()
        
        def move_up(state: UfoState) -> UfoState:
            return replace(state, z=state.z + 10.0)
        
        manager.update_state(move_up)
        snapshot = manager.get_snapshot()
        
        assert snapshot.z == 10.0

    def test_update_state_is_atomic(self):
        """update_state() ist atomar - State ändert sich komplett oder gar nicht."""
        manager = StateManager()
        
        def complex_update(state: UfoState) -> UfoState:
            return replace(state, x=100.0, y=200.0, z=300.0)
        
        manager.update_state(complex_update)
        snapshot = manager.get_snapshot()
        
        assert snapshot.x == 100.0
        assert snapshot.y == 200.0
        assert snapshot.z == 300.0

    def test_multiple_updates(self):
        """Mehrere Updates werden sequenziell angewendet."""
        manager = StateManager()
        
        manager.update_state(lambda s: replace(s, z=10.0))
        manager.update_state(lambda s: replace(s, z=s.z + 5.0))
        manager.update_state(lambda s: replace(s, z=s.z * 2.0))
        
        snapshot = manager.get_snapshot()
        assert snapshot.z == 30.0  # (10 + 5) * 2


class TestObserverPattern:
    """Tests für Observer-Registrierung und -Benachrichtigung."""

    def test_register_observer(self):
        """Observer kann registriert werden."""
        manager = StateManager()
        notifications = []
        
        def observer(state: UfoState) -> None:
            notifications.append(state.z)
        
        manager.register_observer(observer)
        manager.update_state(lambda s: replace(s, z=42.0))
        
        assert len(notifications) == 1
        assert notifications[0] == 42.0

    def test_multiple_observers(self):
        """Mehrere Observer werden alle benachrichtigt."""
        manager = StateManager()
        notifications1 = []
        notifications2 = []
        
        def observer1(state: UfoState) -> None:
            notifications1.append(state.z)
        
        def observer2(state: UfoState) -> None:
            notifications2.append(state.x)
        
        manager.register_observer(observer1)
        manager.register_observer(observer2)
        
        manager.update_state(lambda s: replace(s, x=10.0, z=20.0))
        
        assert len(notifications1) == 1
        assert notifications1[0] == 20.0
        assert len(notifications2) == 1
        assert notifications2[0] == 10.0

    def test_observer_receives_snapshot(self):
        """Observer erhält Snapshot, nicht Original-State."""
        manager = StateManager()
        received_states = []
        
        def observer(state: UfoState) -> None:
            received_states.append(state)
        
        manager.register_observer(observer)
        manager.update_state(lambda s: replace(s, z=100.0))
        
        assert len(received_states) == 1
        # Snapshot kann nicht den Manager-State beeinflussen
        assert received_states[0].z == 100.0

    def test_duplicate_observer_registration_ignored(self):
        """Mehrfache Registrierung desselben Observers wird ignoriert."""
        manager = StateManager()
        notification_count = [0]
        
        def observer(_: UfoState) -> None:
            notification_count[0] += 1
        
        manager.register_observer(observer)
        manager.register_observer(observer)  # Duplikat
        manager.register_observer(observer)  # Duplikat
        
        manager.update_state(lambda s: replace(s, z=1.0))
        
        # Observer sollte nur einmal registriert sein
        assert notification_count[0] == 1

    def test_unregister_observer(self):
        """Observer kann deregistriert werden."""
        manager = StateManager()
        notifications = []
        
        def observer(state: UfoState) -> None:
            notifications.append(state.z)
        
        manager.register_observer(observer)
        manager.update_state(lambda s: replace(s, z=10.0))
        
        manager.unregister_observer(observer)
        manager.update_state(lambda s: replace(s, z=20.0))
        
        # Nur erste Benachrichtigung sollte angekommen sein
        assert len(notifications) == 1
        assert notifications[0] == 10.0

    def test_observer_exception_does_not_break_others(self):
        """Exception in einem Observer bricht andere Observer nicht ab."""
        manager = StateManager()
        notifications1 = []
        notifications2 = []
        
        def failing_observer(_: UfoState) -> None:
            raise RuntimeError("Simulated observer error")
        
        def working_observer1(state: UfoState) -> None:
            notifications1.append(state.z)
        
        def working_observer2(state: UfoState) -> None:
            notifications2.append(state.z)
        
        manager.register_observer(working_observer1)
        manager.register_observer(failing_observer)
        manager.register_observer(working_observer2)
        
        manager.update_state(lambda s: replace(s, z=42.0))
        
        # Beide funktionierenden Observer sollten benachrichtigt worden sein
        assert len(notifications1) == 1
        assert len(notifications2) == 1


class TestWaitForCondition:
    """Tests für wait_for_condition()-Methode."""

    def test_wait_for_condition_fulfilled_immediately(self):
        """wait_for_condition() kehrt sofort zurück wenn bereits erfüllt."""
        manager = StateManager()
        manager.update_state(lambda s: replace(s, z=100.0))
        
        result = manager.wait_for_condition(lambda s: s.z >= 50.0, timeout=1.0)
        
        assert result is True

    def test_wait_for_condition_fulfilled_after_update(self):
        """wait_for_condition() wartet auf Update."""
        manager = StateManager()
        result_container = []
        
        def waiter():
            result = manager.wait_for_condition(lambda s: s.z >= 50.0, timeout=5.0)
            result_container.append(result)
        
        # Thread starten der wartet
        wait_thread = threading.Thread(target=waiter)
        wait_thread.start()
        
        # Kurz warten, dann Bedingung erfüllen
        time.sleep(0.1)
        manager.update_state(lambda s: replace(s, z=100.0))
        
        # Thread sollte terminieren
        wait_thread.join(timeout=2.0)
        
        assert len(result_container) == 1
        assert result_container[0] is True

    def test_wait_for_condition_timeout(self):
        """wait_for_condition() gibt False bei Timeout zurück."""
        manager = StateManager()
        
        start_time = time.time()
        result = manager.wait_for_condition(lambda s: s.z >= 1000.0, timeout=0.5)
        elapsed = time.time() - start_time
        
        assert result is False
        assert 0.4 <= elapsed <= 0.7  # Timeout sollte eingehalten werden

    def test_wait_for_condition_without_timeout(self):
        """wait_for_condition() wartet unbegrenzt ohne Timeout."""
        manager = StateManager()
        result_container = []
        
        def waiter():
            result = manager.wait_for_condition(lambda s: s.z >= 50.0)
            result_container.append(result)
        
        # Thread starten der wartet
        wait_thread = threading.Thread(target=waiter, daemon=True)
        wait_thread.start()
        
        # Kurz warten, dann Bedingung erfüllen
        time.sleep(0.1)
        manager.update_state(lambda s: replace(s, z=100.0))
        
        # Thread sollte terminieren
        wait_thread.join(timeout=2.0)
        
        assert len(result_container) == 1
        assert result_container[0] is True


class TestReset:
    """Tests für reset()-Methode."""

    def test_reset_clears_state(self):
        """reset() setzt State auf Default zurück."""
        manager = StateManager()
        
        # State modifizieren
        manager.update_state(lambda s: replace(s, x=100.0, y=200.0, z=300.0))
        
        # Reset
        manager.reset()
        
        # State sollte wieder Default sein
        snapshot = manager.get_snapshot()
        assert snapshot.x == 0.0
        assert snapshot.y == 0.0
        assert snapshot.z == 0.0

    def test_reset_notifies_waiters(self):
        """reset() weckt wartende Threads auf."""
        manager = StateManager()
        manager.update_state(lambda s: replace(s, z=50.0))
        
        result_container = []
        
        def waiter():
            # Wartet auf z == 0 (nur durch reset erreichbar)
            result = manager.wait_for_condition(lambda s: s.z == 0.0, timeout=5.0)
            result_container.append(result)
        
        wait_thread = threading.Thread(target=waiter)
        wait_thread.start()
        
        time.sleep(0.1)
        manager.reset()
        
        wait_thread.join(timeout=2.0)
        
        assert len(result_container) == 1
        assert result_container[0] is True

    def test_reset_notifies_observers(self):
        """reset() benachrichtigt alle Observer."""
        manager = StateManager()
        notifications = []
        
        def observer(state: UfoState) -> None:
            notifications.append(state.z)
        
        manager.register_observer(observer)
        
        # Erste Änderung
        manager.update_state(lambda s: replace(s, z=100.0))
        
        # Reset sollte Observer benachrichtigen
        manager.reset()
        
        # Observer sollte zweimal benachrichtigt worden sein (update + reset)
        assert len(notifications) == 2
        assert notifications[0] == 100.0
        assert notifications[1] == 0.0  # Nach reset ist z wieder 0



class TestThreadSafety:
    """Tests für Thread-Safety."""

    def test_concurrent_updates(self):
        """Mehrere Threads können gleichzeitig updaten."""
        manager = StateManager()
        num_threads = 10
        updates_per_thread = 100
        
        def updater():
            for _ in range(updates_per_thread):
                manager.update_state(lambda s: replace(s, z=s.z + 1.0))
        
        threads = [threading.Thread(target=updater) for _ in range(num_threads)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join(timeout=5.0)
        
        # Alle Updates sollten atomar ausgeführt worden sein
        snapshot = manager.get_snapshot()
        expected = num_threads * updates_per_thread
        assert snapshot.z == expected

    def test_concurrent_reads_and_writes(self):
        """Lesezugriffe während Updates sind thread-sicher."""
        manager = StateManager()
        read_count = [0]
        stop_flag = threading.Event()
        
        def reader():
            while not stop_flag.is_set():
                snapshot = manager.get_snapshot()
                # Snapshot sollte immer konsistent sein (z >= 0)
                assert snapshot.z >= 0.0
                read_count[0] += 1
                time.sleep(0.001)
        
        def writer():
            for i in range(50):
                manager.update_state(lambda s: replace(s, z=float(i)))
                time.sleep(0.01)
        
        reader_thread = threading.Thread(target=reader)
        writer_thread = threading.Thread(target=writer)
        
        reader_thread.start()
        writer_thread.start()
        
        writer_thread.join(timeout=5.0)
        stop_flag.set()
        reader_thread.join(timeout=2.0)
        
        # Reader sollte viele Snapshots gelesen haben
        assert read_count[0] > 10


class TestLegacyStateProperty:
    """Tests für Legacy-Property state."""

    def test_state_property_returns_internal_state(self):
        """state-Property gibt internen State zurück."""
        manager = StateManager()
        manager.update_state(lambda s: replace(s, z=42.0))
        
        # Legacy-Zugriff
        state = manager.state
        
        assert state.z == 42.0

    def test_state_property_is_not_thread_safe(self):
        """state-Property ist nicht thread-sicher (dokumentiert)."""
        # Dies ist ein dokumentiertes Verhalten - kein Test nötig
        # Property existiert nur für Legacy-Kompatibilität
        manager = StateManager()
        assert hasattr(manager, 'state')


class TestStateManagerIntegration:
    """Integrationstests für StateManager."""

    def test_full_workflow_with_observers_and_waiting(self):
        """Vollständiger Workflow: Observer + wait_for_condition."""
        manager = StateManager()
        notifications = []
        
        def observer(state: UfoState) -> None:
            notifications.append(state.z)
        
        manager.register_observer(observer)
        
        # Simuliere Flug bis Ziel-Höhe
        result_container = []
        
        def waiter():
            result = manager.wait_for_condition(lambda s: s.z >= 100.0, timeout=5.0)
            result_container.append(result)
        
        wait_thread = threading.Thread(target=waiter)
        wait_thread.start()
        
        # Simuliere graduelle Höhenänderung
        for i in range(11):
            manager.update_state(lambda s: replace(s, z=s.z + 10.0))
            time.sleep(0.05)
        
        wait_thread.join(timeout=2.0)
        
        # Observer sollte alle Updates erhalten haben
        assert len(notifications) == 11
        assert notifications[-1] == 110.0
        
        # Waiter sollte erfolgreich gewesen sein
        assert len(result_container) == 1
        assert result_container[0] is True


@pytest.mark.threading
class TestDeadlockPrevention:
    """Tests zur Deadlock-Vermeidung."""

    def test_no_deadlock_with_observer_calling_get_snapshot(self):
        """Observer kann get_snapshot() aufrufen ohne Deadlock."""
        manager = StateManager()
        snapshots_in_observer = []
        
        def observer(_: UfoState) -> None:
            # Observer ruft get_snapshot() auf
            # (wird außerhalb Lock benachrichtigt, daher kein Deadlock)
            snapshot = manager.get_snapshot()
            snapshots_in_observer.append(snapshot.z)
        
        manager.register_observer(observer)
        manager.update_state(lambda s: replace(s, z=42.0))
        
        assert len(snapshots_in_observer) == 1
        assert snapshots_in_observer[0] == 42.0
