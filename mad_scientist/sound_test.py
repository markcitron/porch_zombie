#!/usr/bin/python3
"""
Simple sound output test for Raspberry Pi.
- Plays a 440Hz beep (sine wave) for 1 second.
- Optionally, play a WAV file if a path is given as an argument.

Usage:
  python3 sound_test.py           # play beep
  python3 sound_test.py myfile.wav  # play WAV file
"""
import sys
import time

try:
    import simpleaudio as sa
except ImportError:
    print("simpleaudio not installed. Install with: pip install simpleaudio")
    sys.exit(1)

import numpy as np

if len(sys.argv) > 1:
    # Play a WAV file
    wav_path = sys.argv[1]
    try:
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        print(f"Playing {wav_path}...")
        play_obj.wait_done()
    except Exception as e:
        print(f"Error playing {wav_path}: {e}")
else:
    # Play a 440Hz beep for 1 second
    print("Playing 440Hz test beep for 1 second...")
    fs = 44100  # samples per second
    t = np.linspace(0, 1, int(fs), False)
    note = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
    audio = (note * 32767 / np.max(np.abs(note))).astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, fs)
    play_obj.wait_done()
    print("Done.")
