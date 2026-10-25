"""Hardware-free tests for delayed Zombie Closet visitor sequences."""

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from queue import Queue
from threading import Event
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch


class ZombieClosetListenerTests(unittest.TestCase):
    def setUp(self):
        self.gpio = Mock()
        self.gpio.LOW = 0
        self.gpio.HIGH = 1
        rpi = ModuleType("RPi")
        rpi.GPIO = self.gpio
        self.mqtt = Mock()
        self.mqtt.CallbackAPIVersion = SimpleNamespace(VERSION2=2)
        self.mqtt.MQTTv311 = 4
        self.mqtt.MQTT_ERR_SUCCESS = 0
        paho = ModuleType("paho")
        paho_mqtt = ModuleType("paho.mqtt")
        paho.mqtt = paho_mqtt
        paho_mqtt.client = self.mqtt
        dependencies = {
            "RPi": rpi, "RPi.GPIO": self.gpio,
            "paho": paho, "paho.mqtt": paho_mqtt,
            "paho.mqtt.client": self.mqtt,
        }
        folder = Path(__file__).resolve().parents[1]
        loaded = {}
        with patch.dict(sys.modules, dependencies):
            for name in ("relays", "zombie_closet", "zombiecloset_mqtt_listener"):
                spec = importlib.util.spec_from_file_location(
                    name, folder / f"{name}.py"
                )
                if spec is None or spec.loader is None:
                    raise RuntimeError(f"Could not load {name}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                loaded[name] = module
        self.listener = loaded["zombiecloset_mqtt_listener"]
        self.actions = loaded["zombie_closet"]
        self.client = self.mqtt.Client.return_value
        self.client.connect.return_value = 0
        self.client.subscribe.return_value = (0, 1)
        self.client.loop_forever.return_value = 0
        self.success = SimpleNamespace(is_failure=False)
        self.failure = SimpleNamespace(is_failure=True)
        self.events = Queue()
        self.controller = self.listener.VisitorController(self.events)
        self.now = 100.0
        self.sequence_times = []
        self.clock = SimpleNamespace(
            monotonic=lambda: self.now,
            sleep=lambda seconds: self.advance(seconds),
        )
        self.run_sequence = self.listener.run_visitor_sequence
        self.run_controller = self.listener.run_controller
        replacements = patch.multiple(
            self.listener,
            time=self.clock,
            run_visitor_sequence=Mock(
                side_effect=lambda: self.sequence_times.append(self.now)
            ),
            run_controller=Mock(),
        )
        replacements.start()
        self.addCleanup(replacements.stop)
        self.output = io.StringIO()
        redirect = redirect_stdout(self.output)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)

    def advance(self, seconds):
        self.now += seconds

    def message(self, payload, topic="hauntedporch/control", retain=False):
        message = SimpleNamespace(payload=payload, topic=topic, retain=retain)
        self.listener.on_message(self.client, self.events, message)

    def test_callback_only_queues_a_timestamped_event(self):
        self.message(b"HP_new_visitor")
        self.assertEqual(self.events.get_nowait(), ("HP_new_visitor", 100.0))
        self.gpio.output.assert_not_called()
        self.listener.run_visitor_sequence.assert_not_called()
        self.client.connect.assert_not_called()

    def test_waits_exactly_ten_seconds_before_starting(self):
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.now = 109.99
        self.controller.update()
        self.assertEqual(self.sequence_times, [])
        self.now = 110.0
        self.controller.update()
        self.assertEqual(self.sequence_times, [110.0])

    def test_delay_uses_receipt_time_not_processing_time(self):
        self.message(b"HP_new_visitor")
        self.now = 112.0
        self.controller.update()
        self.assertEqual(self.sequence_times, [112.0])

    def test_delay_is_configurable_including_zero(self):
        with patch.object(self.listener, "VISITOR_DELAY_SECONDS", 3):
            self.message(b"HP_new_visitor")
            self.controller.update()
            self.now = 102.99
            self.controller.update()
            self.assertEqual(self.sequence_times, [])
            self.now = 103
            self.controller.update()
        self.assertEqual(self.sequence_times, [103])
        self.message(b"HP_theyre_gone")
        with patch.object(self.listener, "VISITOR_DELAY_SECONDS", 0):
            self.message(b"HP_new_visitor")
            self.controller.update()
        self.assertEqual(self.sequence_times, [103, 103])

    def test_duplicate_arrivals_do_not_restart_delay_or_repeat_sequence(self):
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.now = 105
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.now = 110
        self.controller.update()
        self.now = 200
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.assertEqual(self.sequence_times, [110])

    def test_departure_rearms_for_next_session(self):
        self.message(b"HP_new_visitor")
        self.now = 110
        self.controller.update()
        self.message(b"HP_theyre_gone")
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.now = 120
        self.controller.update()
        self.assertEqual(self.sequence_times, [110, 120])

    def test_departure_during_delay_does_not_cancel_activation(self):
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.now = 105
        self.message(b"HP_theyre_gone")
        self.controller.update()
        self.assertFalse(self.controller.session_active)
        self.now = 110
        self.controller.update()
        self.assertEqual(self.sequence_times, [110])

    def test_multiple_sessions_queue_and_never_overlap(self):
        def sequence():
            self.sequence_times.append(self.now)
            self.message(b"HP_theyre_gone")
            self.message(b"HP_new_visitor")
            self.advance(15)

        self.listener.run_visitor_sequence.side_effect = sequence
        self.message(b"HP_new_visitor")
        self.now = 110
        self.controller.update()
        self.assertEqual(self.sequence_times, [110])
        self.controller.update()
        self.assertEqual(self.sequence_times, [110, 125])

    def test_initial_idle_or_departure_does_not_activate(self):
        self.controller.update()
        self.message(b"HP_theyre_gone")
        self.now = 1000
        self.controller.update()
        self.listener.run_visitor_sequence.assert_not_called()

    def test_invalid_unrelated_and_retained_messages_are_ignored(self):
        self.message(b"HP_new_visitor", topic="another/topic")
        self.message(b"HP_new_visitor", retain=True)
        self.message(b"HP_theyre_gone", retain=True)
        self.message(b"\xff")
        self.message(b"")
        self.message(b"HP_new_visitor ")
        self.controller.update()
        self.now = 200
        self.controller.update()
        self.assertEqual(self.sequence_times, [])
        self.assertIn("unexpected topic", self.output.getvalue())
        self.assertIn("retained visitor event", self.output.getvalue())
        self.assertIn("non-UTF-8", self.output.getvalue())
        self.assertIn("unrelated MQTT payload", self.output.getvalue())

    def test_sequence_calls_existing_sidekick_and_resets_gpio(self):
        with patch.object(self.actions, "time", self.clock):
            self.run_sequence()
        self.assertEqual(
            self.gpio.output.call_args_list, [call(20, 1), call(20, 0)]
        )
        self.assertEqual(self.now, 110)

    def test_sidekick_error_propagates_after_reset(self):
        clock = SimpleNamespace(sleep=Mock(side_effect=OSError("action failed")))
        with patch.object(self.actions, "time", clock):
            with self.assertRaisesRegex(OSError, "action failed"):
                self.run_sequence()
        self.assertEqual(
            self.gpio.output.call_args_list, [call(20, 1), call(20, 0)]
        )

    def test_sidekick_interrupt_resets_gpio(self):
        clock = SimpleNamespace(sleep=Mock(side_effect=KeyboardInterrupt))
        with patch.object(self.actions, "time", clock):
            with self.assertRaises(KeyboardInterrupt):
                self.run_sequence()
        self.gpio.output.assert_has_calls([call(20, 1), call(20, 0)])

    def test_sidekick_activation_write_failure_still_attempts_reset(self):
        self.gpio.output.side_effect = [OSError("GPIO failed"), None]
        with self.assertRaisesRegex(OSError, "GPIO failed"):
            self.run_sequence()
        self.assertEqual(
            self.gpio.output.call_args_list, [call(20, 1), call(20, 0)]
        )

    def test_reconnect_resubscribes_without_clearing_pending_session(self):
        self.message(b"HP_new_visitor")
        self.controller.update()
        self.listener.on_disconnect(self.client, None, None, self.failure, None)
        for _ in range(2):
            self.listener.on_connect(self.client, None, None, self.success, None)
        self.now = 110
        self.controller.update()
        self.assertEqual(self.sequence_times, [110])
        self.assertTrue(self.controller.session_active)
        self.assertEqual(
            self.client.subscribe.call_args_list,
            [call("hauntedporch/control", qos=1)] * 2,
        )

    def test_connection_and_subscription_errors_are_surfaced(self):
        with self.assertRaisesRegex(ConnectionError, "connection rejected"):
            self.listener.on_connect(self.client, None, None, self.failure, None)
        self.client.subscribe.return_value = (4, None)
        with self.assertRaisesRegex(RuntimeError, "subscription failed with code 4"):
            self.listener.on_connect(self.client, None, None, self.success, None)
        for codes in ([], [self.failure]):
            with self.assertRaisesRegex(RuntimeError, "subscription rejected"):
                self.listener.on_subscribe(self.client, None, 1, codes, None)

    def test_main_wires_callbacks_and_cleans_up_on_interrupt(self):
        self.listener.run_controller.side_effect = KeyboardInterrupt
        self.listener.main()
        self.client.connect.assert_called_once_with("10.10.0.175", 1883, keepalive=60)
        self.assertEqual(self.mqtt.Client.call_args[1]["callback_api_version"], 2)
        self.assertIsInstance(self.mqtt.Client.call_args[1]["userdata"], Queue)
        self.assertIs(self.client.on_message, self.listener.on_message)
        self.assertIs(self.client.on_subscribe, self.listener.on_subscribe)
        self.assertEqual(
            self.gpio.output.call_args_list, [call(26, 0), call(26, 0)]
        )
        self.gpio.cleanup.assert_called_once_with()
        self.client.disconnect.assert_called_once_with()

    def test_main_connection_failure_cleans_up_and_propagates(self):
        self.client.connect.side_effect = ConnectionRefusedError("broker offline")
        with self.assertRaisesRegex(ConnectionRefusedError, "broker offline"):
            self.listener.main()
        self.listener.run_controller.assert_not_called()
        self.gpio.cleanup.assert_called_once_with()
        self.client.disconnect.assert_called_once_with()

    def test_main_action_failure_cleans_up_and_propagates(self):
        self.listener.run_controller.side_effect = OSError("sidekick failed")
        with self.assertRaisesRegex(OSError, "sidekick failed"):
            self.listener.main()
        self.gpio.output.assert_has_calls([call(26, 0), call(26, 0)])
        self.gpio.cleanup.assert_called_once_with()
        self.client.disconnect.assert_called_once_with()

    def test_shutdown_close_failure_still_cleans_up_and_disconnects(self):
        self.gpio.output.side_effect = [None, OSError("close failed")]
        with self.assertRaisesRegex(OSError, "close failed"):
            self.listener.main()
        self.gpio.cleanup.assert_called_once_with()
        self.client.disconnect.assert_called_once_with()

    def test_network_failures_propagate_to_hardware_thread(self):
        self.client.loop_forever.side_effect = RuntimeError("callback failed")
        with self.assertRaisesRegex(RuntimeError, "callback failed"):
            self.run_controller(self.client, self.controller)
        self.client.disconnect.assert_called_once_with()

    def test_network_failure_return_code_is_not_ignored(self):
        self.client.loop_forever.return_value = 4
        with self.assertRaisesRegex(RuntimeError, "network loop exited with code 4"):
            self.run_controller(self.client, self.controller)

    def test_mqtt_can_receive_departure_during_action(self):
        started = Event()
        queued = Event()
        disconnected = Event()

        def network():
            if not started.wait(2):
                raise TimeoutError("Test action did not start")
            self.message(b"HP_theyre_gone")
            queued.set()
            if not disconnected.wait(3):
                raise TimeoutError("Test MQTT loop did not stop")
            return 0

        def sequence():
            started.set()
            self.assertTrue(queued.wait(2))
            self.assertTrue(self.controller.session_active)
            raise KeyboardInterrupt

        self.message(b"HP_new_visitor")
        self.now = 110
        self.client.loop_forever.side_effect = network
        self.client.disconnect.side_effect = disconnected.set
        self.listener.run_visitor_sequence.side_effect = sequence
        with self.assertRaises(KeyboardInterrupt):
            self.run_controller(self.client, self.controller)
        self.assertTrue(disconnected.is_set())
        self.assertEqual(self.events.get_nowait()[0], "HP_theyre_gone")

    def test_invalid_configuration_fails_before_connecting(self):
        for name, value in (
            ("VISITOR_DELAY_SECONDS", -1), ("VISITOR_DELAY_SECONDS", float("nan")),
            ("VISITOR_DELAY_SECONDS", float("inf")), ("POLL_INTERVAL_SECONDS", 0),
        ):
            with self.subTest(name=name, value=value):
                with patch.object(self.listener, name, value):
                    with self.assertRaisesRegex(ValueError, name):
                        self.listener.main()
        self.client.connect.assert_not_called()
        self.gpio.output.assert_not_called()


if __name__ == "__main__":
    unittest.main()
