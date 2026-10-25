"""Hardware-free tests for the coordinated MQTT/distance scarecrow controller."""

import importlib.util
import io
import sys
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from queue import Queue
from threading import Event, Lock
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch


class ScarecrowListenerTests(unittest.TestCase):
    def setUp(self):
        self.hardware = Mock()
        self.mqtt = Mock()
        self.mqtt.CallbackAPIVersion = SimpleNamespace(VERSION2=2)
        self.mqtt.MQTTv311 = 4
        self.mqtt.MQTT_ERR_SUCCESS = 0
        paho = ModuleType("paho")
        paho_mqtt = ModuleType("paho.mqtt")
        paho.mqtt = paho_mqtt
        paho_mqtt.client = self.mqtt
        robot_hat = ModuleType("robot_hat")
        robot_hat.Servo = Mock()
        robot_hat.Pin = Mock()
        robot_hat.Ultrasonic = Mock()
        robot_utils = ModuleType("robot_hat.utils")
        robot_utils.reset_mcu = Mock()
        dependencies = {
            "lib8relind": self.hardware,
            "paho": paho,
            "paho.mqtt": paho_mqtt,
            "paho.mqtt.client": self.mqtt,
            "robot_hat": robot_hat,
            "robot_hat.utils": robot_utils,
        }
        folder = Path(__file__).resolve().parents[1]
        loaded = {}
        with patch.dict(sys.modules, dependencies):
            for name in (
                "relays", "scarecrow_actions", "test_actions",
                "test_distance_ultra", "scarecrow_waiting", "scarecrow_listening_mqtt",
            ):
                spec = importlib.util.spec_from_file_location(
                    name, folder / f"{name}.py"
                )
                if spec is None or spec.loader is None:
                    raise RuntimeError(f"Could not load {name}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                loaded[name] = module
        self.listener = loaded["scarecrow_listening_mqtt"]
        self.relays = loaded["relays"]
        self.actions = loaded["scarecrow_actions"]
        self.client = self.mqtt.Client.return_value
        self.client.connect.return_value = 0
        self.client.loop_forever.return_value = 0
        self.client.subscribe.return_value = (0, 1)
        self.success = SimpleNamespace(is_failure=False)
        self.failure = SimpleNamespace(is_failure=True)
        self.events = Queue()
        self.sensor = Mock()
        self.sensor.read.return_value = 40.0
        self.hand = Mock()
        self.wrist = Mock()
        self.now = 100.0
        self.clock = SimpleNamespace(
            monotonic=lambda: self.now,
            sleep=lambda seconds: self.advance(seconds),
        )
        self.calls = Mock()
        self.calls.attach_mock(self.hardware.set, "relay")
        self.run_controller = self.listener.run_controller
        replacements = patch.multiple(
            self.listener,
            time=self.clock,
            initialize_hardware=Mock(),
            HandController=Mock(return_value=self.hand),
            WristController=Mock(return_value=self.wrist),
            Ultrasonic=Mock(return_value=self.sensor),
            grab=self.calls.grab,
            let_go=self.calls.let_go,
            run_controller=Mock(),
        )
        replacements.start()
        self.addCleanup(replacements.stop)
        self.controller = self.listener.ScarecrowController(
            self.events, self.sensor, self.hand, self.wrist
        )
        self.now = self.controller.startup_ready_at
        self.output = io.StringIO()
        redirect = redirect_stdout(self.output)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)

    def advance(self, seconds):
        self.now += seconds

    def message(self, payload, topic="hauntedporch/control", retain=False):
        message = SimpleNamespace(topic=topic, payload=payload, retain=retain)
        self.listener.on_message(self.client, self.events, message)

    def arrive(self):
        self.message(b"HP_new_visitor")
        self.controller.process_events()

    def test_import_does_not_write_relays_or_connect(self):
        self.hardware.set.assert_not_called()
        self.mqtt.Client.assert_not_called()

    def test_callbacks_only_queue_commands(self):
        self.message(b"HP_new_visitor")
        self.message(b"HP_theyre_gone")
        self.hardware.set.assert_not_called()
        self.calls.grab.assert_not_called()
        self.assertEqual(self.events.get_nowait(), "HP_new_visitor")
        self.assertEqual(self.events.get_nowait(), "HP_theyre_gone")

    def test_arrival_departure_and_duplicate_events_only_change_base_once(self):
        for payload in (
            b"HP_new_visitor", b"HP_new_visitor",
            b"HP_theyre_gone", b"HP_theyre_gone",
        ):
            self.message(payload)
        self.controller.process_events()
        self.assertFalse(self.controller.active)
        self.assertEqual(
            self.hardware.set.call_args_list, [call(0, 6, 1), call(0, 6, 0)]
        )

    def test_idle_does_not_read_distance_or_exit(self):
        for _ in range(3):
            self.controller.update()
            self.advance(10)
        self.sensor.read.assert_not_called()
        self.calls.grab.assert_not_called()
        self.arrive()
        self.controller.update()
        self.calls.grab.assert_called_once_with(self.hand, self.wrist)

    def test_startup_grace_blocks_grabs_but_not_arrivals(self):
        self.now = 100
        self.arrive()
        self.controller.update()
        self.hardware.set.assert_called_once_with(0, 6, 1)
        self.sensor.read.assert_not_called()
        self.now = self.controller.startup_ready_at - 0.01
        self.controller.update()
        self.calls.grab.assert_not_called()
        self.now = self.controller.startup_ready_at
        self.controller.update()
        self.calls.grab.assert_called_once()

    def test_settling_delay_starts_after_extension(self):
        with patch.object(self.listener, "BASE_SETTLE_SECONDS", 2):
            self.arrive()
        self.controller.update()
        self.sensor.read.assert_not_called()
        self.advance(1.99)
        self.controller.update()
        self.calls.grab.assert_not_called()
        self.advance(0.01)
        self.controller.update()
        self.calls.grab.assert_called_once()

    def test_current_threshold_is_preserved_at_eighty_cm(self):
        self.assertEqual(self.listener.TRIGGER_DISTANCE_CM, 80.0)
        self.assertEqual(self.listener.BASE_SETTLE_SECONDS, 0.0)
        self.arrive()
        self.sensor.read.return_value = 80.01
        self.controller.update()
        self.calls.grab.assert_not_called()
        self.sensor.read.return_value = 80.0
        self.controller.update()
        self.calls.grab.assert_called_once()

    def test_hold_is_five_seconds_after_grab_finishes(self):
        self.calls.grab.side_effect = lambda *_: self.advance(3)
        self.arrive()
        self.controller.update()
        finished = self.now
        self.assertEqual(self.controller.hold_until, finished + 5)
        self.now = finished + 4.99
        self.controller.update()
        self.calls.let_go.assert_not_called()
        self.now = finished + 5
        self.controller.update()
        self.calls.let_go.assert_called_once_with(self.hand, self.wrist)

    def test_nearby_person_requires_valid_far_reading_to_rearm(self):
        self.arrive()
        self.controller.update()
        self.advance(5)
        self.controller.update()
        for distance in (40, -1, float("nan"), float("inf"), 80):
            self.sensor.read.return_value = distance
            self.controller.update()
        self.calls.grab.assert_called_once()
        self.sensor.read.return_value = 80.01
        self.controller.update()
        self.sensor.read.return_value = 79
        self.controller.update()
        self.assertEqual(self.calls.grab.call_count, 2)

    def test_invalid_readings_never_trigger(self):
        self.arrive()
        for distance in (-1, -2, float("nan"), float("inf")):
            self.sensor.read.return_value = distance
            self.controller.update()
        self.calls.grab.assert_not_called()
        self.assertTrue(self.controller.armed)

    def test_duplicate_arrival_does_not_rearm_or_restart_hold(self):
        self.arrive()
        self.controller.update()
        hold_until = self.controller.hold_until
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.assertEqual(self.controller.hold_until, hold_until)
        self.assertFalse(self.controller.armed)
        self.hardware.set.assert_called_once_with(0, 6, 1)

    def test_departure_during_grab_finishes_grab_then_releases_before_rotation(self):
        def grab(*_):
            self.message(b"HP_theyre_gone")
            self.assertEqual(self.hardware.set.call_args_list, [call(0, 6, 1)])
            self.advance(2)

        self.calls.grab.side_effect = grab
        self.arrive()
        self.controller.update()
        self.assertEqual(
            self.calls.mock_calls,
            [
                call.relay(0, 6, 1),
                call.grab(self.hand, self.wrist),
                call.let_go(self.hand, self.wrist),
                call.relay(0, 6, 0),
            ],
        )
        self.assertFalse(self.controller.active)
        self.assertFalse(self.controller.holding)

    def test_departure_during_hold_skips_remainder_and_releases_before_rotation(self):
        self.arrive()
        self.controller.update()
        self.advance(1)
        self.message(b"HP_theyre_gone")
        self.controller.update()
        self.assertLess(self.now, self.controller.hold_until)
        self.assertEqual(
            self.calls.mock_calls[-2:],
            [call.let_go(self.hand, self.wrist), call.relay(0, 6, 0)],
        )
        self.assertFalse(self.controller.holding)

    def test_departure_during_sensor_read_prevents_grab(self):
        def read():
            self.message(b"HP_theyre_gone")
            return 20

        self.sensor.read.side_effect = read
        self.arrive()
        self.controller.update()
        self.calls.grab.assert_not_called()
        self.assertFalse(self.controller.active)

    def test_departure_followed_by_arrival_is_not_coalesced(self):
        def grab(*_):
            self.message(b"HP_theyre_gone")
            self.message(b"HP_new_visitor")

        self.calls.grab.side_effect = grab
        self.arrive()
        self.controller.update()
        self.assertEqual(
            self.calls.mock_calls[-3:],
            [
                call.let_go(self.hand, self.wrist),
                call.relay(0, 6, 0),
                call.relay(0, 6, 1),
            ],
        )
        self.assertTrue(self.controller.active)
        self.assertTrue(self.controller.armed)
        self.assertFalse(self.controller.holding)

    def test_next_group_can_grab_without_restarting_script(self):
        self.arrive()
        self.controller.update()
        self.message(b"HP_theyre_gone")
        self.controller.update()
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.assertEqual(self.calls.grab.call_count, 2)

    def test_bad_or_retained_messages_are_logged_and_ignored(self):
        self.message(b"HP_new_visitor", retain=True)
        self.message(b"HP_theyre_gone", retain=True)
        self.message(b"HP_new_visitor", topic="another/topic")
        self.message(b"\xff")
        self.message(b"scarecrow")
        self.message(b"")
        self.message(b"HP_new_visitor ")
        self.controller.process_events()
        self.hardware.set.assert_not_called()
        self.assertIn("retained visitor event", self.output.getvalue())
        self.assertIn("unexpected topic", self.output.getvalue())
        self.assertIn("non-UTF-8", self.output.getvalue())
        self.assertIn("unrelated MQTT payload", self.output.getvalue())

    def test_every_connection_subscribes_without_resetting_state(self):
        self.arrive()
        for _ in range(2):
            self.listener.on_connect(self.client, None, None, self.success, None)
        self.assertEqual(
            self.client.subscribe.call_args_list,
            [call("hauntedporch/control", qos=1)] * 2,
        )
        self.hardware.set.assert_called_once_with(0, 6, 1)

    def test_disconnect_keeps_base_and_distance_control_active(self):
        self.arrive()
        self.listener.on_disconnect(self.client, None, None, self.failure, None)
        self.controller.update()
        self.hardware.set.assert_called_once_with(0, 6, 1)
        self.calls.grab.assert_called_once()
        self.assertIn("Keeping relay 6 unchanged", self.output.getvalue())

    def test_rejected_connection_or_subscription_surfaces_errors(self):
        with self.assertRaisesRegex(ConnectionError, "connection rejected"):
            self.listener.on_connect(self.client, None, None, self.failure, None)
        self.client.subscribe.return_value = (4, None)
        with self.assertRaisesRegex(RuntimeError, "subscription failed with code 4"):
            self.listener.on_connect(self.client, None, None, self.success, None)
        for codes in ([], [self.failure]):
            with self.assertRaisesRegex(RuntimeError, "subscription rejected"):
                self.listener.on_subscribe(self.client, None, 1, codes, None)

    def test_subscription_success_is_logged_after_acknowledgement(self):
        self.listener.on_subscribe(self.client, None, 1, [self.success], None)
        self.assertIn("Listening for visitor events", self.output.getvalue())

    def test_main_initializes_releases_and_resets_base_on_shutdown(self):
        self.listener.run_controller.side_effect = KeyboardInterrupt
        self.listener.main()
        self.listener.initialize_hardware.assert_called_once_with()
        self.listener.Ultrasonic.assert_called_once()
        self.calls.let_go.assert_has_calls(
            [call(self.hand, self.wrist), call(self.hand, self.wrist)]
        )
        self.assertEqual(
            self.calls.mock_calls,
            [
                call.relay(0, 6, 0),
                call.let_go(self.hand, self.wrist),
                call.let_go(self.hand, self.wrist),
                call.relay(0, 6, 0),
            ],
        )
        self.client.connect.assert_called_once_with("10.10.0.175", 1883, keepalive=60)
        self.assertIs(self.client.on_message, self.listener.on_message)
        self.assertEqual(self.mqtt.Client.call_args[1]["callback_api_version"], 2)
        self.assertIsInstance(self.mqtt.Client.call_args[1]["userdata"], Queue)
        self.client.disconnect.assert_called_once_with()

    def test_main_error_releases_before_contracting_and_is_propagated(self):
        self.listener.run_controller.side_effect = OSError("controller failed")
        with self.assertRaisesRegex(OSError, "controller failed"):
            self.listener.main()
        self.assertEqual(
            self.calls.mock_calls[-2:],
            [call.let_go(self.hand, self.wrist), call.relay(0, 6, 0)],
        )
        self.client.disconnect.assert_called_once_with()

    def test_initial_connection_failure_cleans_up(self):
        self.client.connect.side_effect = ConnectionRefusedError("broker offline")
        with self.assertRaisesRegex(ConnectionRefusedError, "broker offline"):
            self.listener.main()
        self.listener.run_controller.assert_not_called()
        self.hardware.set.assert_has_calls([call(0, 6, 0), call(0, 6, 0)])
        self.client.disconnect.assert_called_once_with()

    def test_release_failure_still_attempts_base_reset_and_disconnect(self):
        self.calls.let_go.side_effect = [None, OSError("release failed")]
        with self.assertRaisesRegex(OSError, "release failed"):
            self.listener.main()
        self.hardware.set.assert_has_calls([call(0, 6, 0), call(0, 6, 0)])
        self.client.disconnect.assert_called_once_with()

    def test_network_callback_failure_reaches_main_thread(self):
        self.client.loop_forever.side_effect = RuntimeError("subscription rejected")
        with self.assertRaisesRegex(RuntimeError, "subscription rejected"):
            self.run_controller(self.client, self.controller)
        self.client.disconnect.assert_called_once_with()

    def test_network_return_code_failure_is_not_silent(self):
        self.client.loop_forever.return_value = 4
        with self.assertRaisesRegex(RuntimeError, "network loop exited with code 4"):
            self.run_controller(self.client, self.controller)
        self.client.disconnect.assert_called_once_with()

    def test_network_runs_while_main_thread_performs_a_grab(self):
        connected = Event()
        disconnected = Event()
        grab_started = Event()
        departure_queued = Event()

        def network():
            connected.set()
            if not grab_started.wait(2):
                raise TimeoutError("Test grab did not start")
            self.message(b"HP_theyre_gone")
            departure_queued.set()
            if not disconnected.wait(3):
                raise TimeoutError("Test MQTT loop did not stop")
            return 0

        def disconnect():
            disconnected.set()

        def grab(*_):
            self.assertTrue(connected.wait(1))
            grab_started.set()
            self.assertTrue(departure_queued.wait(2))
            self.hardware.set.assert_called_once_with(0, 6, 1)

        def update():
            self.controller.update()
            if not self.controller.active:
                raise KeyboardInterrupt

        self.arrive()
        self.client.loop_forever.side_effect = network
        self.client.disconnect.side_effect = disconnect
        self.calls.grab.side_effect = grab
        controller = Mock()
        controller.update.side_effect = update
        with self.assertRaises(KeyboardInterrupt):
            self.run_controller(self.client, controller)
        self.assertTrue(disconnected.is_set())
        self.calls.grab.assert_called_once()
        self.assertEqual(
            self.calls.mock_calls[-2:],
            [call.let_go(self.hand, self.wrist), call.relay(0, 6, 0)],
        )

    def test_invalid_configuration_fails_before_hardware_access(self):
        for name, value in (
            ("BASE_SETTLE_SECONDS", -1), ("STARTUP_DELAY_SECONDS", float("nan")),
            ("HOLD_SECONDS", -1), ("READ_INTERVAL", 0), ("TRIGGER_DISTANCE_CM", 0),
        ):
            with self.subTest(name=name):
                with patch.object(self.listener, name, value):
                    with self.assertRaisesRegex(ValueError, name):
                        self.listener.main()
        self.hardware.set.assert_not_called()
        self.mqtt.Client.assert_not_called()

    def test_relay_reads_and_writes_share_one_lock(self):
        counters = {"active": 0, "maximum": 0}
        counter_lock = Lock()

        def io_operation(*_):
            with counter_lock:
                counters["active"] += 1
                counters["maximum"] = max(counters["maximum"], counters["active"])
            time.sleep(0.005)
            with counter_lock:
                counters["active"] -= 1
            return 1

        self.hardware.set.side_effect = io_operation
        self.hardware.get.side_effect = io_operation
        with ThreadPoolExecutor(max_workers=4) as executor:
            jobs = []
            for _ in range(4):
                jobs.append(executor.submit(self.listener.BASE_RELAY.extend))
                jobs.append(executor.submit(self.actions.read_relay_state, 6))
            for job in jobs:
                job.result(timeout=2)
        self.assertEqual(counters["maximum"], 1)
        self.assertEqual(counters["active"], 0)

    def test_sound_writes_use_same_locked_relay_helper(self):
        with patch.object(self.actions, "set_relay_state") as write, patch.object(
            self.actions, "time", SimpleNamespace(sleep=Mock())
        ):
            self.actions.trigger_sound()
        self.assertEqual(write.call_args_list, [call(3, 0), call(3, 1)])

    def test_relay_lock_is_released_after_an_io_error(self):
        self.hardware.set.side_effect = OSError("relay failed")
        with self.assertRaisesRegex(OSError, "relay failed"):
            self.listener.BASE_RELAY.extend()
        acquired = self.relays.RELAY_IO_LOCK.acquire(timeout=1)
        self.assertTrue(acquired)
        if acquired:
            self.relays.RELAY_IO_LOCK.release()


if __name__ == "__main__":
    unittest.main()
