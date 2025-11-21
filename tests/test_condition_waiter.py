#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit-Tests für ConditionWaiter Utility-Klasse."""

import threading
import time
import pytest

from src.core.simulation.utils.condition_waiter import ConditionWaiter


class TestConditionWaiter:
    """Tests für die zentrale ConditionWaiter-Utility."""

    def test_immediate_true_condition(self):
        """Prädikat bereits erfüllt → sofortiger Return mit True."""
        condition = threading.Condition()
        state = {"value": 42}

        result = ConditionWaiter.wait_for_condition(
            condition_var=condition,
            predicate=lambda s: s["value"] == 42,
            state_getter=lambda: state,
            timeout=0.1
        )

        assert result is True

    def test_immediate_false_with_timeout(self):
        """Prädikat nicht erfüllt → Timeout → Return False."""
        condition = threading.Condition()
        state = {"value": 0}

        start = time.time()
        result = ConditionWaiter.wait_for_condition(
            condition_var=condition,
            predicate=lambda s: s["value"] == 999,
            state_getter=lambda: state,
            timeout=0.1
        )
        elapsed = time.time() - start

        assert result is False
        assert elapsed >= 0.1  # Mindestens Timeout-Dauer
        assert elapsed < 0.2  # Aber nicht viel länger

    def test_condition_fulfilled_after_notify(self):
        """State wird asynchron geändert → Notification → Prädikat erfüllt."""
        condition = threading.Condition()
        state = {"value": 0}

        def update_state():
            """Ändert State nach 100ms und notified."""
            time.sleep(0.1)
            with condition:
                state["value"] = 100
                condition.notify_all()

        # Start async update
        thread = threading.Thread(target=update_state, daemon=True)
        thread.start()

        # Wait for condition
        result = ConditionWaiter.wait_for_condition(
            condition_var=condition,
            predicate=lambda s: s["value"] == 100,
            state_getter=lambda: state,
            timeout=1.0
        )

        assert result is True
        assert state["value"] == 100

    def test_timeout_before_condition_fulfilled(self):
        """Timeout läuft ab bevor Prädikat erfüllt wird."""
        condition = threading.Condition()
        state = {"value": 0}

        def slow_update():
            """Ändert State nach 500ms (zu langsam)."""
            time.sleep(0.5)
            with condition:
                state["value"] = 100
                condition.notify_all()

        thread = threading.Thread(target=slow_update, daemon=True)
        thread.start()

        # Timeout nach 100ms (State wird erst nach 500ms geändert)
        result = ConditionWaiter.wait_for_condition(
            condition_var=condition,
            predicate=lambda s: s["value"] == 100,
            state_getter=lambda: state,
            timeout=0.1
        )

        assert result is False
        # State sollte noch nicht geändert sein
        assert state["value"] == 0

    def test_no_timeout_waits_indefinitely(self):
        """Ohne Timeout wird unbegrenzt gewartet (bis Condition erfüllt)."""
        condition = threading.Condition()
        state = {"ready": False}

        def update_after_delay():
            time.sleep(0.2)
            with condition:
                state["ready"] = True
                condition.notify_all()

        thread = threading.Thread(target=update_after_delay, daemon=True)
        thread.start()

        # Kein Timeout → wartet unbegrenzt
        result = ConditionWaiter.wait_for_condition(
            condition_var=condition,
            predicate=lambda s: s["ready"],
            state_getter=lambda: state,
            timeout=None  # Explizit None
        )

        assert result is True
        assert state["ready"] is True

    def test_multiple_notifications_spurious_wakeups(self):
        """Mehrere notify_all() Calls → while-loop schützt vor spurious wakeups."""
        condition = threading.Condition()
        state = {"counter": 0}

        def send_multiple_notifications():
            """Sendet mehrere Notifications, aber ändert Wert nur einmal."""
            for i in range(5):
                time.sleep(0.02)
                with condition:
                    if i == 3:  # Nur beim 4. Mal Wert ändern
                        state["counter"] = 10
                    condition.notify_all()

        thread = threading.Thread(target=send_multiple_notifications, daemon=True)
        thread.start()

        # Warte auf counter == 10
        result = ConditionWaiter.wait_for_condition(
            condition_var=condition,
            predicate=lambda s: s["counter"] == 10,
            state_getter=lambda: state,
            timeout=1.0
        )

        assert result is True
        assert state["counter"] == 10

    def test_complex_state_object(self):
        """Funktioniert mit komplexen State-Objekten (nicht nur Dict)."""
        from dataclasses import dataclass

        @dataclass
        class ComplexState:
            x: float
            y: float
            z: float

        condition = threading.Condition()
        state = ComplexState(0.0, 0.0, 0.0)

        def update_z():
            nonlocal state
            time.sleep(0.1)
            with condition:
                state = ComplexState(state.x, state.y, 100.0)
                condition.notify_all()

        thread = threading.Thread(target=update_z, daemon=True)
        thread.start()

        result = ConditionWaiter.wait_for_condition(
            condition_var=condition,
            predicate=lambda s: s.z >= 100.0,
            state_getter=lambda: state,
            timeout=1.0
        )

        assert result is True
        assert state.z == 100.0

    def test_thread_safety_concurrent_waits(self):
        """Mehrere Threads warten gleichzeitig auf dieselbe Condition."""
        condition = threading.Condition()
        state = {"value": 0}
        results = []

        def waiter(target_value):
            result = ConditionWaiter.wait_for_condition(
                condition_var=condition,
                predicate=lambda s: s["value"] >= target_value,
                state_getter=lambda: state,
                timeout=2.0
            )
            results.append((target_value, result))

        # 3 Threads warten auf verschiedene Werte
        threads = [
            threading.Thread(target=waiter, args=(10,), daemon=True),
            threading.Thread(target=waiter, args=(20,), daemon=True),
            threading.Thread(target=waiter, args=(30,), daemon=True),
        ]

        for t in threads:
            t.start()

        # State inkrementieren und notifyen
        for value in [10, 20, 30]:
            time.sleep(0.1)
            with condition:
                state["value"] = value
                condition.notify_all()

        # Warte auf alle Threads
        for t in threads:
            t.join(timeout=3.0)

        # Alle sollten erfolgreich gewesen sein
        assert len(results) == 3
        assert all(result for _, result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

