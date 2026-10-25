# Pneumo Jumper

## Motion-triggered sequence with sound

`waiting_for_people.py` uses the existing PIR filter and actuator sequence.
On a valid motion trigger, it starts looping
`sounds/spooky-halloween-effects-with-thunder-121665.mp3`, fires the jumper,
then runs the relay-2 sequence. The sound stops only after the entire sequence
finishes, **including the relay-2 reset wait**.

The motion trigger is unchanged: the script measures a PIR HIGH pulse and
accepts it after it returns LOW if its duration is at least 0.30 seconds.
Sound starts with that accepted trigger, not on every unfiltered PIR HIGH.
Short rejected pulses do not play sound.

### Setup

Use the Pi environment where the existing GPIO/relay tests work. Pygame's
mixer supplies asynchronous MP3 playback without initializing a display.
On Raspberry Pi OS, it can be installed as a system package:

```bash
sudo apt update
sudo apt install python3-pygame
python3 waiting_for_people.py
```

If using a virtual environment with `--system-site-packages`, the system
Pygame package is visible there too. Alternatively, install `pygame` with
that environment's `python -m pip install pygame`, not system-wide `pip`.

`SOUND_PATH` is resolved relative to the script, so starting the script from
a different working directory does not change which file is loaded. The
actual file name uses `effects-with-thunder` with hyphens.

### Playback and cleanup

- The mixer is initialized and the MP3 loaded once at startup.
- Playback is nonblocking and loops if the file ends before the sequence does.
- The current sequence timing remains unchanged: relay 2's start is anchored
  to the PIR pulse's start, followed by its 45-second extended period and
  30-second reset wait.
- Every accepted sequence stops playback in `finally`, including on failure
  or Ctrl+C. Shutdown also stops/quits the mixer and attempts both relay
  resets and GPIO cleanup, even if another cleanup step fails.
- Missing audio files or unavailable audio devices surface as errors; the
  script does not silently continue without sound.

Set the Pi's desired audio output and volume before testing. Keep the prop's
movement area clear. Do not run another script controlling these relays
simultaneously.

Hardware-free tests:

```bash
python3 -m unittest discover -s tests -p test_waiting_for_people_audio.py
```