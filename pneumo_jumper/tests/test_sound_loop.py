"""Hardware-free tests for the standalone speaker test."""

import ast
import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, call, patch


class SoundLoopTests(unittest.TestCase):
    def setUp(self):
        self.pygame = Mock()
        self.pygame.mixer.get_init.return_value = (44100, -16, 2)
        folder = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "sound_test_runner", folder / "test_sound.py"
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load sound test")
        self.runner = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"pygame": self.pygame}):
            spec.loader.exec_module(self.runner)
        redirect = redirect_stdout(io.StringIO())
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)

    def test_matches_motion_script_sound_without_importing_gpio(self):
        source = self.runner.SOUND_PATH.parents[1] / "waiting_for_people.py"
        tree = ast.parse(source.read_text())
        assignment = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "SOUND_PATH"
                for target in node.targets
            )
        )
        expected = eval(
            compile(ast.Expression(assignment.value), str(source), "eval"),
            {"Path": Path, "__file__": str(source)},
        )
        self.assertEqual(self.runner.SOUND_PATH, expected)
        self.assertTrue(self.runner.SOUND_PATH.is_file())
        self.pygame.mixer.init.assert_not_called()

    def test_loops_at_full_volume_until_interrupt_and_cleans_up(self):
        with patch.object(
            self.runner.time, "sleep", side_effect=[None, KeyboardInterrupt]
        ) as sleep:
            self.runner.main()
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(
            self.pygame.mixer.mock_calls,
            [
                call.init(),
                call.music.load(str(self.runner.SOUND_PATH)),
                call.music.set_volume(1.0),
                call.music.play(loops=-1),
                call.get_init(),
                call.music.stop(),
                call.quit(),
            ],
        )

    def test_load_and_play_errors_propagate_and_clean_up(self):
        for method in ("load", "play"):
            with self.subTest(method=method):
                self.pygame.reset_mock(side_effect=True)
                getattr(self.pygame.mixer.music, method).side_effect = OSError(
                    "Audio failed"
                )
                with self.assertRaisesRegex(OSError, "Audio failed"):
                    self.runner.main()
                self.pygame.mixer.music.stop.assert_called_once_with()
                self.pygame.mixer.quit.assert_called_once_with()

    def test_init_failure_quits_without_stopping_uninitialized_mixer(self):
        self.pygame.mixer.init.side_effect = OSError("No audio device")
        self.pygame.mixer.get_init.return_value = None
        with self.assertRaisesRegex(OSError, "No audio device"):
            self.runner.main()
        self.pygame.mixer.music.stop.assert_not_called()
        self.pygame.mixer.quit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
