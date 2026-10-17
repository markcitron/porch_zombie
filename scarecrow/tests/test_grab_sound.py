"""Check the sound trigger without requiring Raspberry Pi hardware."""

import importlib.util
import sys
import time
import unittest
from pathlib import Path
from threading import Event
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch


def load_actions():
    hardware = {}
    for name, symbols in {
        "lib8relind": ("get", "set"),
        "robot_hat": ("Servo",),
        "robot_hat.utils": ("reset_mcu",),
    }.items():
        module = ModuleType(name)
        for symbol in symbols:
            setattr(module, symbol, Mock())
        hardware[name] = module

    folder = Path(__file__).resolve().parents[1]
    loaded = {}
    with patch.dict(sys.modules, hardware):
        for name in ("relays", "scarecrow_actions", "test_actions"):
            spec = importlib.util.spec_from_file_location(
                name, folder / f"{name}.py"
            )
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Could not load {name}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[name] = module
    return (
        loaded["scarecrow_actions"],
        loaded["test_actions"],
        hardware["lib8relind"],
    )


class GrabSoundTests(unittest.TestCase):
    def setUp(self):
        self.actions, self.combined, self.relays = load_actions()
        self.now = 100.0
        self.writes = []
        self.sleeps = []
        self.relays.set.side_effect = (
            lambda board, relay, state: self.writes.append(
                (board, relay, state, self.now)
            )
        )
        self.clock = SimpleNamespace(
            monotonic=lambda: self.now,
            sleep=self.advance,
        )

    def advance(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def test_sound_states_and_exact_delays_from_grab_start(self):
        with patch.object(self.actions, "time", self.clock), patch.object(
            self.combined, "time", self.clock
        ):
            self.combined._trigger_grab_sound(100.0)
        self.assertEqual(self.sleeps, [1.0, 0.5])
        self.assertEqual(
            self.writes,
            [(0, 3, 0, 101.0), (0, 3, 1, 101.5)],
        )

    def test_worker_scheduling_delay_does_not_restart_one_second_wait(self):
        self.now = 100.25
        with patch.object(self.actions, "time", self.clock), patch.object(
            self.combined, "time", self.clock
        ):
            self.combined._trigger_grab_sound(100.0)
        self.assertEqual(self.sleeps, [0.75, 0.5])
        self.assertEqual(
            self.writes,
            [(0, 3, 0, 101.0), (0, 3, 1, 101.5)],
        )

    def test_late_worker_preserves_half_second_pulse(self):
        self.now = 102.0
        with patch.object(self.actions, "time", self.clock), patch.object(
            self.combined, "time", self.clock
        ):
            self.combined._trigger_grab_sound(100.0)
        self.assertEqual(self.sleeps, [0.0, 0.5])
        self.assertEqual(
            self.writes,
            [(0, 3, 0, 102.0), (0, 3, 1, 102.5)],
        )

    def test_grab_sound_runs_during_hand_movement(self):
        contracted = Event()
        timeline = []

        def write(board, relay, state):
            timeline.append((f"relay_{state}", time.monotonic()))
            if state == 1:
                contracted.set()

        def hands(_):
            timeline.append(("hands_start", time.monotonic()))
            self.assertTrue(contracted.wait(3), "Sound did not complete")
            timeline.append(("hands_finish", time.monotonic()))

        self.relays.set.side_effect = write
        with patch.object(self.combined, "close_arms") as arms, patch.object(
            self.combined, "close_hands", side_effect=hands
        ):
            started_at = time.monotonic()
            self.combined.grab(Mock(), Mock())
        arms.assert_called_once_with()
        self.assertEqual(
            [name for name, _ in timeline],
            ["hands_start", "relay_0", "relay_1", "hands_finish"],
        )
        self.assertGreaterEqual(timeline[1][1] - started_at, 1.0)
        self.assertGreaterEqual(timeline[2][1] - timeline[1][1], 0.5)
        self.assertGreaterEqual(timeline[2][1] - started_at, 1.5)
        self.assertEqual(
            self.relays.set.call_args_list,
            [call(0, 3, 0), call(0, 3, 1)],
        )

    def test_grab_waits_for_sound_and_surfaces_relay_failure(self):
        with patch.object(self.combined, "SOUND_START_DELAY_SECONDS", 0), (
            patch.object(self.combined, "close_arms")
        ), patch.object(self.combined, "close_hands"):
            self.relays.set.side_effect = OSError("speaker relay failed")
            with self.assertRaisesRegex(OSError, "speaker relay failed"):
                self.combined.grab(Mock(), Mock(), hand_delay=0)

    def test_grab_finishes_sound_before_propagating_movement_error(self):
        with patch.object(self.combined, "SOUND_START_DELAY_SECONDS", 0), (
            patch.object(self.actions, "SOUND_TRIGGER_PAUSE_SECONDS", 0)
        ), patch.object(
            self.combined, "close_arms", side_effect=OSError("arms failed")
        ):
            with self.assertRaisesRegex(OSError, "arms failed"):
                self.combined.grab(Mock(), Mock())
        self.assertEqual(
            self.relays.set.call_args_list,
            [call(0, 3, 0), call(0, 3, 1)],
        )

    def test_let_go_does_not_trigger_sound_or_change_movement_order(self):
        events = Mock()
        hand = Mock()
        wrist = Mock()
        with patch.object(
            self.combined, "open_arms", events.open_arms
        ), patch.object(
            self.combined, "open_hands", events.open_hands
        ), patch.object(self.combined, "time", SimpleNamespace(sleep=events.sleep)):
            self.combined.let_go(hand, wrist)
        self.assertEqual(
            events.mock_calls,
            [call.open_arms(), call.sleep(0.5), call.open_hands(hand)],
        )
        self.relays.set.assert_not_called()


if __name__ == "__main__":
    unittest.main()
