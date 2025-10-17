#!/usr/bin/python3
"""
Simple sound output test for Raspberry Pi.
- Plays a 440Hz beep (sine wave) for 1 second.
- Plays a WAV file if a .wav path is given as an argument (simpleaudio).
- Plays an MP3 file if a .mp3 path is given as an argument (pygame).

Usage:
  python3 sound_test.py           # play beep
  python3 sound_test.py myfile.wav  # play WAV file
  python3 sound_test.py myfile.mp3  # play MP3 file
"""
import sys
import time
import os

try:
    import simpleaudio as sa
except ImportError:
    sa = None
try:
    import numpy as np
except ImportError:
    np = None
try:
    import pygame
except ImportError:
    pygame = None


def play_wav(wav_path):
    if sa is None:
        print("simpleaudio not installed. Install with: pip install simpleaudio")
        return
    try:
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        print(f"Playing {wav_path}...")
        play_obj.wait_done()
    except Exception as e:
        print(f"Error playing {wav_path}: {e}")

def play_mp3(mp3_path):
    if pygame is None:
        print("pygame not installed. Install with: pip install pygame")
        return
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_path)
        print(f"Playing {mp3_path}...")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        pygame.mixer.quit()
    except Exception as e:
        print(f"Error playing {mp3_path}: {e}")

def play_beep():
    if sa is None or np is None:
        print("simpleaudio and numpy required for beep. Install with: pip install simpleaudio numpy")
        return
    print("Playing 440Hz test beep for 1 second...")
    fs = 44100  # samples per second
    t = np.linspace(0, 1, int(fs), False)
    note = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
    audio = (note * 32767 / np.max(np.abs(note))).astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, fs)
    play_obj.wait_done()
    print("Done.")

if len(sys.argv) > 1:
    sound_path = sys.argv[1]
    ext = os.path.splitext(sound_path)[1].lower()
    if ext == ".wav":
        play_wav(sound_path)
    elif ext == ".mp3":
        play_mp3(sound_path)
    else:
        print(f"Unsupported file type: {ext}. Only .wav and .mp3 supported.")
else:
    play_beep()
