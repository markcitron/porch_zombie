"""Hardware-free tests for the distance-triggered scarecrow runner."""

import importlib.util
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from types import ModuleType
from unittest.mock import Mock, call, patch


def load_runner():
    dependencies = {}
    for name, symbols in {
        "robot_hat": ("Pin", "Ultrasonic"),
        "scarecrow_actions": (
            "HandController",
            "WristController",
            "initialize_hardware",
            "read_relay_state",
        ),
        "test_actions": ("grab", "let_go"),
        "test_distance_ultra": (),
    }.items():
        module = ModuleType(name)
        for symbol in symbols:
            setattr(module, symbol, Mock())
        dependencies[name] = module

    sensor_test = dependencies["test_distance_ultra"]
    sensor_test.TRIGGER_PIN = "D2"
    sensor_test.ECHO_PIN = "D3"
    sensor_test.READ_INTERVAL = 0.2
    path = Path(__file__).resolve().parents[1] / "scarecrow_waiting.py"
    spec = importlib.util.spec_from_file_location("waiting_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load scarecrow_waiting.py")
    runner = importlib.util.module_from_spec(spec)
    with patch.dict("sys.modules", dependencies):
        spec.loader.exec_module(runner)
    return runner


class FakeEvent:
    def __init__(self):
        self.stopped = False
        self.waits = []
        self.on_wait = None

    def set(self):
        self.stopped = True

    def is_set(self):
        return self.stopped

    def wait(self, timeout):
        self.waits.append(timeout)
        if self.on_wait is not None:
            self.on_wait(timeout)
        return self.stopped


class WaitingTests(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.stop = FakeEvent()
        self.executor = Mock()
        self.monitor = self.executor.submit.return_value
        executor_context = Mock()
        executor_context.__enter__ = Mock(return_value=self.executor)
        executor_context.__exit__ = Mock(return_value=False)
        self.patches = patch.multiple(
            self.runner,
            Event=Mock(return_value=self.stop),
            ThreadPoolExecutor=Mock(return_value=executor_context),
        )
        self.patches.start()
        self.addCleanup(self.patches.stop)
        self.sensor = self.runner.Ultrasonic.return_value
        self.events = Mock()
        self.events.attach_mock(self.runner.grab, "grab")
        self.events.attach_mock(self.runner.let_go, "let_go")

    def distances(self, readings):
        values = iter(readings)

        def read():
            try:
                return next(values)
            except StopIteration:
                self.stop.set()
                return 100

        self.sensor.read.side_effect = read

    def test_threshold_hold_and_rearming(self):
        threshold = self.runner.TRIGGER_DISTANCE_CM
        self.distances([threshold + 0.01, threshold, threshold - 1, threshold + 1, 0])
        self.runner.main()
        self.assertEqual(self.runner.grab.call_count, 2)
        self.assertEqual(self.stop.waits[0], 15)
        self.assertEqual(self.stop.waits.count(5), 2)
        hand = self.runner.HandController.return_value
        wrist = self.runner.WristController.return_value
        self.assertEqual(
            self.events.mock_calls,
            [
                call.grab(hand, wrist),
                call.let_go(hand, wrist),
                call.grab(hand, wrist),
                call.let_go(hand, wrist),
                call.let_go(hand, wrist),
            ],
        )
        self.runner.initialize_hardware.assert_called_once_with()
        self.runner.Pin.assert_has_calls([call("D2"), call("D3")])
        self.monitor.result.assert_called_once_with()

    def test_invalid_distances_do_not_trigger_or_rearm(self):
        self.distances([-1, -2, float("nan"), float("inf"), 49, -1, 49])
        self.runner.main()
        self.runner.grab.assert_called_once()

    def test_relay_off_during_startup_releases_without_reading_distance(self):
        self.stop.on_wait = lambda _: self.stop.set()
        self.runner.main()
        self.sensor.read.assert_not_called()
        self.runner.grab.assert_not_called()
        self.runner.let_go.assert_called_once()

    def test_relay_off_during_grab_skips_hold_and_releases(self):
        self.distances([40])
        self.runner.grab.side_effect = lambda *_: self.stop.set()
        self.runner.main()
        self.runner.grab.assert_called_once()
        self.runner.let_go.assert_called_once()
        self.assertEqual(self.stop.waits, [15, 5])
        self.assertTrue(self.stop.is_set())

    def test_relay_off_during_hold_releases_without_another_grab(self):
        self.distances([40, 60, 40])

        def wait(timeout):
            if timeout == 5:
                self.stop.set()

        self.stop.on_wait = wait
        self.runner.main()
        self.runner.grab.assert_called_once()
        self.runner.let_go.assert_called_once()
        self.assertEqual(self.sensor.read.call_count, 1)

    def test_stop_during_sensor_read_prevents_grab(self):
        def read():
            self.stop.set()
            return 40

        self.sensor.read.side_effect = read
        self.runner.main()
        self.runner.grab.assert_not_called()
        self.runner.let_go.assert_called_once()

    def test_action_error_releases_and_propagates(self):
        self.distances([40])
        self.runner.grab.side_effect = OSError("action failed")
        with self.assertRaisesRegex(OSError, "action failed"):
            self.runner.main()
        self.runner.let_go.assert_called_once()
        self.assertTrue(self.stop.is_set())

    def test_sensor_error_releases_and_propagates(self):
        self.sensor.read.side_effect = OSError("sensor failed")
        with self.assertRaisesRegex(OSError, "sensor failed"):
            self.runner.main()
        self.runner.let_go.assert_called_once()

    def test_keyboard_interrupt_releases(self):
        self.sensor.read.side_effect = KeyboardInterrupt
        self.runner.main()
        self.runner.let_go.assert_called_once()

    def test_monitor_failure_is_propagated_after_release(self):
        self.stop.set()
        self.monitor.result.side_effect = OSError("relay failed")
        with self.assertRaisesRegex(OSError, "relay failed"):
            self.runner.main()
        self.runner.let_go.assert_called_once()

    def test_monitor_latches_relay_off(self):
        self.runner.read_relay_state.side_effect = [1, 0, 1]
        self.runner.monitor_base_relay(self.stop)
        self.assertTrue(self.stop.is_set())
        self.assertEqual(
            self.runner.read_relay_state.call_args_list,
            [call(6), call(6)],
        )
        self.assertEqual(self.stop.waits, [0.2])

    def test_monitor_invalid_state_stops_and_raises(self):
        self.runner.read_relay_state.return_value = -1
        with self.assertRaisesRegex(RuntimeError, "Unexpected relay 6 state"):
            self.runner.monitor_base_relay(self.stop)
        self.assertTrue(self.stop.is_set())

    def test_monitor_read_error_stops_and_raises(self):
        self.runner.read_relay_state.side_effect = OSError("relay failed")
        with self.assertRaisesRegex(OSError, "relay failed"):
            self.runner.monitor_base_relay(self.stop)
        self.assertTrue(self.stop.is_set())

    def test_real_monitor_detects_off_while_grab_is_running(self):
        stop = Event()
        grabbing = Event()
        enabled = Event()

        def relay_state(_):
            if grabbing.is_set():
                return 0
            enabled.set()
            return 1

        def distance():
            self.assertTrue(enabled.wait(2), "Monitor did not read the relay")
            return 40

        def grab(*_):
            grabbing.set()
            self.assertTrue(stop.wait(2), "Monitor missed relay-off during grab")

        self.runner.read_relay_state.side_effect = relay_state
        self.sensor.read.side_effect = distance
        self.runner.grab.side_effect = grab
        with patch.multiple(
            self.runner,
            Event=Mock(return_value=stop),
            ThreadPoolExecutor=ThreadPoolExecutor,
            STARTUP_DELAY_SECONDS=0,
            READ_INTERVAL=0.001,
        ):
            self.runner.main()

        self.runner.grab.assert_called_once()
        self.runner.let_go.assert_called_once()
        self.assertEqual(self.sensor.read.call_count, 1)

    def test_real_monitor_error_wakes_startup_and_is_propagated(self):
        self.runner.read_relay_state.side_effect = OSError("relay unavailable")
        with patch.multiple(
            self.runner,
            Event=Event,
            ThreadPoolExecutor=ThreadPoolExecutor,
        ):
            with self.assertRaisesRegex(OSError, "relay unavailable"):
                self.runner.main()

        self.runner.grab.assert_not_called()
        self.runner.let_go.assert_called_once()
        self.sensor.read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
