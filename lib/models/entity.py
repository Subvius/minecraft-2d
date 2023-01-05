import random

import pygame
from lib.models.sound import Sound


class Entity:
    def __init__(self, hp, max_hp, damage, jump_height, speed, is_grounded, is_friendly, position, width, height,
                 trigger_radius=0, mob_type: str = "cave_monster", attack_delay: int = 500):
        self.rect: pygame.Rect = pygame.Rect(position[0], position[1], width, height)
        self.hp: int = hp
        self.max_hp: int = max_hp
        self.attack_damage: int = damage
        self.jump_height: int = jump_height
        self.speed: int = speed
        self.is_grounded: bool = is_grounded
        self.is_friendly: bool = is_friendly
        self.is_dead: bool = False
        self.images = {
            "idle": [],
            'walk': [],
            'hurt': [],
            'death': [],
            'attack': [],
        }
        self.image = None
        self.frame: int = 0
        self.condition: str = "idle"
        self.destination = None
        self.trigger_radius = trigger_radius
        self.moving_direction = "left"
        self.vertical_momentum = 0
        self.mob_type = mob_type
        self.width = width
        self.height = height
        self.animation_duration = 200
        self.last_update = pygame.time.get_ticks()
        self.attack_delay = attack_delay
        self.last_attack = self.last_update
        self.last_sun_damage = pygame.time.get_ticks()
        self.sun_damage_delay = 600

        # self.update_image()

    def heal(self, hp):
        self.hp += hp
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def damage(self, damage, sounds: Sound) -> bool:
        self.hp -= damage
        if self.hp <= 0:
            self.is_dead = True
            if self.mob_type == 'cave_monster':
                sounds.play_sound(f"zombie_death")
            self.hp = 0
        else:
            self.condition = 'hurt'
            self.frame = 0
            if self.mob_type == 'cave_monster':
                sounds.play_sound(f"zombie_hurt{random.randint(1, 2)}")
        return self.is_dead

    def cut_sheet(self, sheet, columns, rows, animation_type, frame_width, step):
        for j in range(rows):
            for i in range(columns):
                frame_location = (frame_width * i + step * i, 0)
                image = sheet.subsurface(pygame.Rect(
                    frame_location, (frame_width, sheet.get_height() // rows)))
                self.images[animation_type].append(image)

    def update_image(self, images_quantity: int):
        self.frame = (self.frame + 1) % images_quantity
        # self.image = self.images[self.condition][self.frame]

    def change_condition(self, condition):
        self.condition = condition
        self.frame = 0

    def set_destination(self, coord):
        self.destination = coord
