#!/usr/bin/python3

import time
from pathlib import Path

import pygame

SOUND_PATH = (
    Path(__file__).resolve().parent
    / "sounds"
    / "spooky-halloween-effects-with-thunder-121665.mp3"
)


def main():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(str(SOUND_PATH))
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(loops=-1)
        print(f"Looping {SOUND_PATH.name}. Press Ctrl+C to stop.")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping sound test...")
    finally:
        try:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.music.stop()
        finally:
            pygame.mixer.quit()


if __name__ == "__main__":
    main()