import os

import pygame.mixer


class Sound:
    def __init__(self):
        self.sounds = dict()

    def add_sound(self, filename: str):
        self.sounds.update({filename.split(".")[0]: pygame.mixer.Sound(f"lib/assets/sounds/{filename}")})

    def add_music(self, filename: str):
        self.sounds.update({filename.split(".")[0]: f"lib/assets/music/{filename}"})

    def play_sound(self, name: str):
        if name in list(self.sounds.keys()):
            self.sounds.get(name).play()

    def play_music(self, name: str, repeat: int = -1):
        if name in list(self.sounds.keys()):
            pygame.mixer.music.load(self.sounds.get(name))
            pygame.mixer.music.play(repeat)

    def stop_music(self, name: str, milliseconds: int = 100):
        if name in list(self.sounds.keys()):
            self.sounds.get(name).fadeout(milliseconds)

    def load_all(self):
        for file in os.listdir("lib/assets/sounds/"):
            if not file == ".DS_Store":
                self.add_sound(file)

        for file in os.listdir("lib/assets/music/"):
            if not file == ".DS_Store":
                self.add_music(file)
