"""Hardware-free tests for the MQTT visitor-session trigger."""

import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch


class VisitorMonitorTests(unittest.TestCase):
    def setUp(self):
        self.gpio = Mock()
        rpi = ModuleType("RPi")
        rpi.GPIO = self.gpio
        paho = ModuleType("paho")
        paho_mqtt = ModuleType("paho.mqtt")
        self.mqtt = Mock()
        self.mqtt.MQTT_ERR_SUCCESS = 0
        self.mqtt.MQTTv311 = 4
        paho.mqtt = paho_mqtt
        paho_mqtt.client = self.mqtt
        dependencies = {
            "RPi": rpi,
            "RPi.GPIO": self.gpio,
            "paho": paho,
            "paho.mqtt": paho_mqtt,
            "paho.mqtt.client": self.mqtt,
        }
        path = Path(__file__).resolve().parents[1] / "waiting_for_visitors_MQTT.py"
        spec = importlib.util.spec_from_file_location("visitor_under_test", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load waiting_for_visitors_MQTT.py")
        self.monitor = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", dependencies):
            spec.loader.exec_module(self.monitor)

        self.client = self.mqtt.Client.return_value
        self.client.connect.return_value = 0
        self.client.loop_start.return_value = 0
        self.client.is_connected.return_value = True
        self.publication = self.client.publish.return_value
        self.publication.rc = 0
        self.publication.is_published.return_value = True
        self.now = 0.0
        self.sleeps = []
        self.published_at = []

        def publish(*args, **kwargs):
            self.published_at.append(self.now)
            return self.publication

        self.client.publish.side_effect = publish
        clock = SimpleNamespace(monotonic=lambda: self.now, sleep=self.sleep)
        time_patch = patch.object(self.monitor, "time", clock)
        time_patch.start()
        self.addCleanup(time_patch.stop)
        output_patch = redirect_stdout(io.StringIO())
        output_patch.__enter__()
        self.addCleanup(output_patch.__exit__, None, None, None)

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def readings(self, values):
        samples = iter(values)

        def read(_):
            try:
                self.now, value = next(samples)
                return value
            except StopIteration:
                raise KeyboardInterrupt

        self.gpio.input.side_effect = read

    def run_session(self, values):
        self.readings(values)
        with self.assertRaises(KeyboardInterrupt):
            self.monitor.watch_for_visitors(self.client)

    def messages(self):
        return [
            item[1]["payload"] for item in self.client.publish.call_args_list
        ]

    def test_import_has_no_hardware_or_mqtt_side_effects(self):
        self.gpio.setup.assert_not_called()
        self.mqtt.Client.assert_not_called()

    def test_initial_idle_does_not_publish_departure(self):
        self.run_session([(0, 0), (120, 0), (3600, 0)])
        self.assertEqual(self.messages(), [])

    def test_exact_two_minute_threshold_and_new_session(self):
        self.run_session(
            [(0, 1), (119.99, 0), (120, 0), (121, 0), (122, 1)]
        )
        self.assertEqual(
            self.messages(),
            ["HP_new_visitor", "HP_theyre_gone", "HP_new_visitor"],
        )
        self.assertEqual(self.published_at, [0, 120, 122])
        self.assertEqual(self.sleeps, [0.2] * 5)
        for item in self.client.publish.call_args_list:
            self.assertEqual(item[0], ("hauntedporch/control",))
            self.assertEqual(item[1]["qos"], 1)
            self.assertIs(item[1]["retain"], False)
        self.gpio.input.assert_has_calls([call(6)] * 5)

    def test_each_high_resets_timer_without_duplicate_arrival(self):
        self.run_session(
            [(0, 1), (100, 1), (120, 0), (219.99, 0), (220, 0), (500, 0)]
        )
        self.assertEqual(self.messages(), ["HP_new_visitor", "HP_theyre_gone"])
        self.assertEqual(self.published_at, [0, 220])

    def test_continuously_high_never_publishes_departure(self):
        self.run_session([(0, 1), (120, 1), (240, 1), (3600, 1)])
        self.assertEqual(self.messages(), ["HP_new_visitor"])

    def test_non_retriggering_pulses_keep_session_active(self):
        self.run_session(
            [(0, 1), (5, 0), (60, 1), (65, 0), (170, 1), (289, 0), (290, 0)]
        )
        self.assertEqual(self.messages(), ["HP_new_visitor", "HP_theyre_gone"])

    def test_timeout_is_configurable(self):
        with patch.object(self.monitor, "INACTIVITY_TIMEOUT_SECONDS", 30):
            self.run_session([(5, 1), (34.99, 0), (35, 0), (36, 0)])
        self.assertEqual(self.messages(), ["HP_new_visitor", "HP_theyre_gone"])
        self.assertEqual(self.published_at, [5, 35])

    def test_publish_waits_for_acknowledgement(self):
        self.monitor.publish_event(self.client, "HP_new_visitor")
        self.publication.wait_for_publish.assert_called_once_with(timeout=10)
        self.publication.is_published.assert_called_once_with()

    def test_publish_error_is_not_ignored(self):
        self.publication.rc = 4
        with self.assertRaisesRegex(RuntimeError, "failed with code 4"):
            self.monitor.publish_event(self.client, "HP_new_visitor")
        self.publication.wait_for_publish.assert_not_called()

    def test_publish_timeout_is_not_reported_as_success(self):
        self.publication.is_published.return_value = False
        with self.assertRaisesRegex(TimeoutError, "was not acknowledged"):
            self.monitor.publish_event(self.client, "HP_theyre_gone")

    def test_connect_waits_for_broker_acknowledgement(self):
        self.client.is_connected.side_effect = [False, False, True]
        self.monitor.connect_mqtt(self.client)
        self.client.connect.assert_called_once_with(
            "10.10.0.175", 1883, keepalive=60
        )
        self.client.loop_start.assert_called_once_with()
        self.assertEqual(self.sleeps, [0.2, 0.2])

    def test_connect_acknowledgement_timeout(self):
        self.client.is_connected.return_value = False
        with self.assertRaisesRegex(TimeoutError, "was not acknowledged"):
            self.monitor.connect_mqtt(self.client)
        self.assertGreaterEqual(self.now, 10)

    def test_connect_and_network_loop_errors_are_surfaced(self):
        self.client.connect.return_value = 3
        with self.assertRaisesRegex(RuntimeError, "connect failed with code 3"):
            self.monitor.connect_mqtt(self.client)
        self.client.loop_start.assert_not_called()
        self.client.connect.return_value = 0
        self.client.loop_start.return_value = 3
        with self.assertRaisesRegex(RuntimeError, "network loop failed with code 3"):
            self.monitor.connect_mqtt(self.client)

    def test_main_warms_up_then_connects_and_cleans_up_on_interrupt(self):
        def connect(*args, **kwargs):
            self.assertEqual(self.sleeps, [60])
            return 0

        self.client.connect.side_effect = connect
        self.gpio.input.side_effect = KeyboardInterrupt
        self.monitor.main()
        self.assertEqual(self.sleeps, [60])
        self.mqtt.Client.assert_called_once_with(protocol=4)
        self.gpio.setmode.assert_called_once_with(self.gpio.BCM)
        self.gpio.setup.assert_called_once_with(6, self.gpio.IN)
        self.gpio.cleanup.assert_called_once_with(6)
        self.client.disconnect.assert_called_once_with()
        self.client.loop_stop.assert_called_once_with()
        self.client.publish.assert_not_called()

    def test_gpio_error_cleans_up_and_is_propagated(self):
        self.gpio.input.side_effect = OSError("PIR read failed")
        with self.assertRaisesRegex(OSError, "PIR read failed"):
            self.monitor.main()
        self.gpio.cleanup.assert_called_once_with(6)
        self.client.disconnect.assert_called_once_with()
        self.client.loop_stop.assert_called_once_with()
        self.client.publish.assert_not_called()

    def test_connection_error_cleans_up_and_does_not_start_reading(self):
        self.client.connect.side_effect = ConnectionRefusedError("broker offline")
        with self.assertRaisesRegex(ConnectionRefusedError, "broker offline"):
            self.monitor.main()
        self.gpio.input.assert_not_called()
        self.gpio.cleanup.assert_called_once_with(6)
        self.client.disconnect.assert_called_once_with()
        self.client.loop_stop.assert_called_once_with()

    def test_publish_failure_stops_main_and_cleans_up(self):
        self.gpio.input.return_value = 1
        self.publication.rc = 4
        with self.assertRaisesRegex(RuntimeError, "failed with code 4"):
            self.monitor.main()
        self.gpio.cleanup.assert_called_once_with(6)
        self.client.disconnect.assert_called_once_with()
        self.client.loop_stop.assert_called_once_with()
        self.client.publish.assert_called_once()

    def test_invalid_startup_delay_fails_before_touching_hardware(self):
        for value in (-1, float("nan"), float("inf")):
            with self.subTest(value=value):
                with patch.object(self.monitor, "STARTUP_DELAY_SECONDS", value):
                    with self.assertRaisesRegex(ValueError, "finite and nonnegative"):
                        self.monitor.main()
        self.gpio.setup.assert_not_called()
        self.mqtt.Client.assert_not_called()

    def test_invalid_timeout_fails_before_touching_hardware(self):
        for value in (0, -1, float("nan"), float("inf")):
            with self.subTest(value=value):
                with patch.object(self.monitor, "INACTIVITY_TIMEOUT_SECONDS", value):
                    with self.assertRaisesRegex(ValueError, "finite and positive"):
                        self.monitor.main()
        self.gpio.setup.assert_not_called()
        self.mqtt.Client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
