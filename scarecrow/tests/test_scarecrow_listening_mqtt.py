"""Hardware-free MQTT listener tests using the actual LinAct relay mapping."""

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
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
        dependencies = {
            "lib8relind": self.hardware,
            "paho": paho,
            "paho.mqtt": paho_mqtt,
            "paho.mqtt.client": self.mqtt,
        }
        folder = Path(__file__).resolve().parents[1]
        loaded = {}
        with patch.dict(sys.modules, dependencies):
            for name in ("relays", "scarecrow_listening_mqtt"):
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
        self.client = self.mqtt.Client.return_value
        self.client.connect.return_value = 0
        self.client.loop_forever.return_value = 0
        self.client.subscribe.return_value = (0, 1)
        self.success = SimpleNamespace(is_failure=False)
        self.failure = SimpleNamespace(is_failure=True)
        self.output = io.StringIO()
        redirect = redirect_stdout(self.output)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)

    def message(self, payload, topic="hauntedporch/control", retain=False):
        message = SimpleNamespace(topic=topic, payload=payload, retain=retain)
        self.listener.on_message(self.client, None, message)

    def test_import_does_not_write_relays_or_connect(self):
        self.hardware.set.assert_not_called()
        self.mqtt.Client.assert_not_called()

    def test_arrival_and_departure_use_only_relay_six(self):
        self.message(b"HP_new_visitor")
        self.message(b"HP_theyre_gone")
        self.assertEqual(
            self.hardware.set.call_args_list,
            [call(0, 6, 1), call(0, 6, 0)],
        )

    def test_duplicate_events_set_the_same_values(self):
        self.message(b"HP_new_visitor")
        self.message(b"HP_new_visitor")
        self.message(b"HP_theyre_gone")
        self.message(b"HP_theyre_gone")
        self.assertEqual(
            self.hardware.set.call_args_list,
            [call(0, 6, 1), call(0, 6, 1), call(0, 6, 0), call(0, 6, 0)],
        )

    def test_unknown_payload_does_not_change_extended_relay(self):
        self.message(b"HP_new_visitor")
        self.message(b"scarecrow")
        self.message(b"")
        self.message(b"HP_new_visitor ")
        self.hardware.set.assert_called_once_with(0, 6, 1)
        self.assertIn("Ignoring unrelated MQTT payload", self.output.getvalue())

    def test_retained_events_do_not_move_base(self):
        self.message(b"HP_new_visitor", retain=True)
        self.message(b"HP_theyre_gone", retain=True)
        self.hardware.set.assert_not_called()
        self.assertIn("Ignoring retained visitor event", self.output.getvalue())

    def test_unexpected_topic_is_ignored(self):
        self.message(b"HP_new_visitor", topic="another/topic")
        self.hardware.set.assert_not_called()
        self.assertIn("unexpected topic", self.output.getvalue())

    def test_invalid_utf8_is_logged_and_later_valid_message_works(self):
        self.message(b"\xff")
        self.hardware.set.assert_not_called()
        self.assertIn("non-UTF-8", self.output.getvalue())
        self.message(b"HP_new_visitor")
        self.hardware.set.assert_called_once_with(0, 6, 1)

    def test_every_connection_subscribes_without_resetting_relay(self):
        self.message(b"HP_new_visitor")
        for _ in range(2):
            self.listener.on_connect(self.client, None, None, self.success, None)
        self.assertEqual(
            self.client.subscribe.call_args_list,
            [call("hauntedporch/control", qos=1)] * 2,
        )
        self.hardware.set.assert_called_once_with(0, 6, 1)

    def test_connection_loss_and_reconnect_hold_relay_state(self):
        self.message(b"HP_new_visitor")
        self.listener.on_disconnect(self.client, None, None, self.failure, None)
        self.listener.on_connect(self.client, None, None, self.success, None)
        self.hardware.set.assert_called_once_with(0, 6, 1)
        self.assertIn("Keeping relay 6 unchanged", self.output.getvalue())

    def test_connection_rejection_is_an_error(self):
        with self.assertRaisesRegex(ConnectionError, "connection rejected"):
            self.listener.on_connect(self.client, None, None, self.failure, None)
        self.client.subscribe.assert_not_called()

    def test_subscribe_queue_failure_is_an_error(self):
        self.client.subscribe.return_value = (4, None)
        with self.assertRaisesRegex(RuntimeError, "subscription failed with code 4"):
            self.listener.on_connect(self.client, None, None, self.success, None)

    def test_subscription_success_is_logged_after_acknowledgement(self):
        self.listener.on_subscribe(self.client, None, 1, [self.success], None)
        self.assertIn(
            "Listening for visitor events on hauntedporch/control",
            self.output.getvalue(),
        )

    def test_subscription_rejection_is_an_error(self):
        for codes in ([], [self.failure]):
            with self.subTest(codes=codes):
                with self.assertRaisesRegex(RuntimeError, "subscription rejected"):
                    self.listener.on_subscribe(self.client, None, 1, codes, None)

    def test_main_defaults_to_zero_processes_events_and_resets_on_exit(self):
        def run_loop():
            self.assertEqual(self.hardware.set.call_args_list, [call(0, 6, 0)])
            self.client.on_connect(self.client, None, None, self.success, None)
            self.client.on_subscribe(self.client, None, 1, [self.success], None)
            self.message(b"HP_new_visitor")
            self.message(b"HP_theyre_gone")
            raise KeyboardInterrupt

        self.client.loop_forever.side_effect = run_loop
        self.listener.main()
        self.mqtt.Client.assert_called_once_with(
            callback_api_version=2, protocol=4
        )
        self.assertIs(self.client.on_message, self.listener.on_message)
        self.assertIs(self.client.on_disconnect, self.listener.on_disconnect)
        self.client.connect.assert_called_once_with(
            "10.10.0.175", 1883, keepalive=60
        )
        self.assertEqual(
            self.hardware.set.call_args_list,
            [call(0, 6, 0), call(0, 6, 1), call(0, 6, 0), call(0, 6, 0)],
        )
        self.client.disconnect.assert_called_once_with()

    def test_initial_connection_exception_resets_and_propagates(self):
        self.client.connect.side_effect = ConnectionRefusedError("broker offline")
        with self.assertRaisesRegex(ConnectionRefusedError, "broker offline"):
            self.listener.main()
        self.assertEqual(
            self.hardware.set.call_args_list, [call(0, 6, 0), call(0, 6, 0)]
        )
        self.client.loop_forever.assert_not_called()
        self.client.disconnect.assert_called_once_with()

    def test_initial_connect_error_code_resets_and_raises(self):
        self.client.connect.return_value = 4
        with self.assertRaisesRegex(ConnectionError, "connect failed with code 4"):
            self.listener.main()
        self.hardware.set.assert_has_calls([call(0, 6, 0), call(0, 6, 0)])
        self.client.disconnect.assert_called_once_with()

    def test_loop_error_resets_and_propagates(self):
        self.client.loop_forever.return_value = 4
        with self.assertRaisesRegex(RuntimeError, "network loop exited with code 4"):
            self.listener.main()
        self.hardware.set.assert_has_calls([call(0, 6, 0), call(0, 6, 0)])
        self.client.disconnect.assert_called_once_with()

    def test_relay_write_error_resets_and_propagates(self):
        self.hardware.set.side_effect = [None, OSError("relay failed"), None]
        self.client.loop_forever.side_effect = (
            lambda: self.message(b"HP_new_visitor")
        )
        with self.assertRaisesRegex(OSError, "relay failed"):
            self.listener.main()
        self.assertEqual(
            self.hardware.set.call_args_list,
            [call(0, 6, 0), call(0, 6, 1), call(0, 6, 0)],
        )
        self.client.disconnect.assert_called_once_with()

    def test_shutdown_relay_failure_still_disconnects_mqtt(self):
        self.hardware.set.side_effect = [None, OSError("shutdown relay failed")]
        with self.assertRaisesRegex(OSError, "shutdown relay failed"):
            self.listener.main()
        self.client.disconnect.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
