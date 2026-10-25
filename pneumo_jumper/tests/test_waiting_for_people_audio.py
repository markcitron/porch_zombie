"""Hardware-free tests for sound lifetime and existing motion timings."""

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch


class MotionAudioTests(unittest.TestCase):
    def setUp(self):
        self.gpio = Mock()
        self.gpio.LOW = 0
        self.gpio.HIGH = 1
        rpi = ModuleType("RPi")
        rpi.GPIO = self.gpio
        self.pygame = Mock()
        self.pygame.mixer.get_init.return_value = (44100, -16, 2)
        folder = Path(__file__).resolve().parents[1]
        loaded = {}
        with patch.dict(
            sys.modules,
            {"RPi": rpi, "RPi.GPIO": self.gpio, "pygame": self.pygame},
        ):
            for name in ("relays", "waiting_for_people"):
                spec = importlib.util.spec_from_file_location(
                    name, folder / f"{name}.py"
                )
                if spec is None or spec.loader is None:
                    raise RuntimeError(f"Could not load {name}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                loaded[name] = module
        self.runner = loaded["waiting_for_people"]
        self.now = 100.0
        self.sleeps = []
        self.clock = SimpleNamespace(
            monotonic=lambda: self.now,
            time=lambda: self.now + 1000,
            sleep=self.sleep,
        )
        clock_patch = patch.object(self.runner, "time", self.clock)
        clock_patch.start()
        self.addCleanup(clock_patch.stop)
        redirect = redirect_stdout(io.StringIO())
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def assert_hardware_cleanup(self):
        self.assertEqual(
            self.gpio.output.call_args_list[-2:],
            [call(26, 0), call(20, 1)],
        )
        self.gpio.cleanup.assert_called_once_with()
        self.pygame.mixer.quit.assert_called_once_with()

    def test_sound_path_is_anchored_to_script_and_matches_existing_file(self):
        self.assertTrue(self.runner.SOUND_PATH.is_absolute())
        self.assertEqual(
            self.runner.SOUND_PATH,
            Path(self.runner.__file__).resolve().parent
            / "sounds" / "spooky-halloween-effects-with-thunder-121665.mp3",
        )
        self.assertTrue(self.runner.SOUND_PATH.is_file())

    def test_sound_spans_entire_sequence_including_reset_wait(self):
        timeline = []
        relay1 = Mock()
        relay2 = Mock()

        def record(name):
            return lambda *args, **kwargs: timeline.append((name, self.now))

        self.pygame.mixer.music.play.side_effect = record("play")
        self.pygame.mixer.music.stop.side_effect = record("stop")
        relay1.contract.side_effect = record("jumper_on")
        relay1.extend.side_effect = record("jumper_off")
        relay2.extend.side_effect = record("relay2_extend")
        relay2.contract.side_effect = record("relay2_contract")
        self.runner.run_motion_sequence(relay1, relay2, 100.0)
        self.assertEqual(
            timeline,
            [
                ("play", 100.0),
                ("jumper_on", 100.0),
                ("jumper_off", 101.0),
                ("relay2_extend", 130.0),
                ("relay2_contract", 175.0),
                ("stop", 205.0),
            ],
        )
        self.assertEqual(self.sleeps, [1.0, 29.0, 45.0, 30.0])
        self.pygame.mixer.music.play.assert_called_once_with(loops=-1)

    def test_long_pir_pulse_preserves_existing_relay2_deadline(self):
        self.now = 140.0
        self.runner.run_motion_sequence(Mock(), Mock(), 100.0)
        self.assertEqual(self.sleeps, [1.0, 0.0, 45.0, 30.0])
        self.pygame.mixer.music.stop.assert_called_once_with()

    def test_action_error_stops_sound_and_propagates(self):
        relay1 = Mock()
        relay1.contract.side_effect = OSError("jumper failed")
        with self.assertRaisesRegex(OSError, "jumper failed"):
            self.runner.run_motion_sequence(relay1, Mock(), self.now)
        self.pygame.mixer.music.stop.assert_called_once_with()

    def test_interrupt_during_reset_wait_stops_sound(self):
        relay2 = Mock()

        def sleep(seconds):
            if seconds == self.runner.RELAY_2_RESET_TIME:
                raise KeyboardInterrupt
            self.now += seconds

        with patch.object(self.clock, "sleep", sleep):
            with self.assertRaises(KeyboardInterrupt):
                self.runner.run_motion_sequence(Mock(), relay2, self.now)
        relay2.contract.assert_called_once_with()
        self.pygame.mixer.music.stop.assert_called_once_with()

    def test_playback_failure_does_not_start_actuators(self):
        relay1 = Mock()
        relay2 = Mock()
        self.pygame.mixer.music.play.side_effect = OSError("playback failed")
        with self.assertRaisesRegex(OSError, "playback failed"):
            self.runner.run_motion_sequence(relay1, relay2, self.now)
        relay1.contract.assert_not_called()
        relay2.extend.assert_not_called()
        self.pygame.mixer.music.stop.assert_called_once_with()

    def test_main_initializes_loads_once_and_cleans_up(self):
        self.gpio.input.side_effect = KeyboardInterrupt
        self.runner.main()
        self.pygame.mixer.init.assert_called_once_with()
        self.pygame.mixer.music.load.assert_called_once_with(
            str(self.runner.SOUND_PATH)
        )
        self.pygame.mixer.music.play.assert_not_called()
        self.pygame.mixer.music.stop.assert_called_once_with()
        self.assert_hardware_cleanup()

    def test_main_missing_file_error_cleans_up_and_propagates(self):
        self.pygame.mixer.music.load.side_effect = FileNotFoundError("audio missing")
        with self.assertRaisesRegex(FileNotFoundError, "audio missing"):
            self.runner.main()
        self.gpio.input.assert_not_called()
        self.pygame.mixer.music.play.assert_not_called()
        self.assert_hardware_cleanup()

    def test_main_unavailable_audio_device_cleans_up_and_propagates(self):
        self.pygame.mixer.init.side_effect = OSError("audio device unavailable")
        self.pygame.mixer.get_init.return_value = None
        with self.assertRaisesRegex(OSError, "audio device unavailable"):
            self.runner.main()
        self.pygame.mixer.music.stop.assert_not_called()
        self.assert_hardware_cleanup()

    def test_stop_error_does_not_prevent_hardware_cleanup_or_mixer_quit(self):
        self.gpio.input.side_effect = KeyboardInterrupt
        self.pygame.mixer.music.stop.side_effect = OSError("audio stop failed")
        with self.assertRaisesRegex(OSError, "audio stop failed"):
            self.runner.main()
        self.assert_hardware_cleanup()

    def test_short_pir_pulse_does_not_play_sound(self):
        self.gpio.input.side_effect = [1, 1, 0]

        def sleep(seconds):
            if seconds == 0.05:
                raise KeyboardInterrupt
            self.now += seconds

        with patch.object(self.clock, "sleep", sleep):
            self.runner.main()
        self.pygame.mixer.music.play.assert_not_called()
        self.assert_hardware_cleanup()

    def test_valid_pir_pulse_starts_the_combined_sequence(self):
        self.gpio.input.side_effect = [1] + [1] * 31 + [0]

        def sleep(seconds):
            if seconds == 0.05:
                raise KeyboardInterrupt
            self.now += seconds

        with patch.object(self.clock, "sleep", sleep), patch.object(
            self.runner, "run_motion_sequence"
        ) as sequence:
            self.runner.main()
        sequence.assert_called_once()
        self.assertEqual(sequence.call_args[0][2], 100.0)
        self.pygame.mixer.music.load.assert_called_once()
        self.assert_hardware_cleanup()


if __name__ == "__main__":
    unittest.main()
