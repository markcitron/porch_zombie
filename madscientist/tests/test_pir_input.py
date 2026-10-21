"""Hardware-free tests for the raw PIR input monitor."""

import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, call, patch


class PIRInputTests(unittest.TestCase):
    def setUp(self):
        self.gpio = Mock()
        rpi = ModuleType("RPi")
        rpi.GPIO = self.gpio
        path = Path(__file__).resolve().parents[1] / "test_pir.py"
        spec = importlib.util.spec_from_file_location("pir_input_under_test", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load test_pir.py")
        self.monitor = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"RPi": rpi, "RPi.GPIO": self.gpio}):
            spec.loader.exec_module(self.monitor)
        self.output = io.StringIO()

    def test_import_does_not_configure_hardware(self):
        self.gpio.setmode.assert_not_called()
        self.gpio.setup.assert_not_called()
        self.gpio.input.assert_not_called()

    def test_loop_reports_raw_values_and_cleans_up_on_interrupt(self):
        self.gpio.input.side_effect = [0, 1, 0]
        clock = Mock()
        clock.sleep.side_effect = [None, None, KeyboardInterrupt]
        with patch.object(self.monitor, "time", clock), redirect_stdout(self.output):
            self.monitor.main()

        self.gpio.setmode.assert_called_once_with(self.gpio.BCM)
        self.gpio.setup.assert_called_once_with(6, self.gpio.IN)
        self.assertEqual(self.gpio.input.call_args_list, [call(6)] * 3)
        self.assertEqual(clock.sleep.call_args_list, [call(0.2)] * 3)
        self.gpio.cleanup.assert_called_once_with(6)
        lines = [
            line for line in self.output.getvalue().splitlines() if "PIR=" in line
        ]
        self.assertEqual(len(lines), 3)
        self.assertIn("PIR=0 (LOW - idle output)", lines[0])
        self.assertIn("PIR=1 (HIGH - motion signaled)", lines[1])
        self.assertIn("PIR=0 (LOW - idle output)", lines[2])
        for line in lines:
            self.assertRegex(line, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3} ")
        self.assertIn("Exiting PIR test.", self.output.getvalue())

    def test_read_error_is_propagated_and_pin_is_released(self):
        self.gpio.input.side_effect = OSError("GPIO read failed")
        with redirect_stdout(self.output):
            with self.assertRaisesRegex(OSError, "GPIO read failed"):
                self.monitor.main()
        self.gpio.cleanup.assert_called_once_with(6)


if __name__ == "__main__":
    unittest.main()
