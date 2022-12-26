import pygame


class Entity:
    def __init__(self, hp, max_hp, damage, jump_height, speed, is_grounded, is_friendly, position, width, height,
                 trigger_radius=0):
        self.rect: pygame.Rect = pygame.Rect(position[0], position[1], width, height)
        self.hp: int = hp
        self.max_hp: int = max_hp
        self.damage: int = damage
        self.jump_height: int = jump_height
        self.speed: int = speed
        self.is_grounded: bool = is_grounded
        self.is_friendly: bool = is_friendly
        self.is_dead: bool = False
        self.images = {
            "idle": [],
            'run': [],
            'throw': [],
        }
        self.image = None
        self.frame: int = 0
        self.condition: str = "run"
        self.destination = None
        self.trigger_radius = trigger_radius
        # self.update_image()

    def heal(self, hp):
        self.hp += hp
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.is_dead = True
            self.hp = 0

    def cut_sheet(self, sheet, columns, rows, animation_type):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i + 29 * i, (self.rect.width - 2) * j)
                image = sheet.subsurface(pygame.Rect(
                    frame_location, (self.rect.width, 70)))
                self.images[animation_type].append(image)

    def update_image(self):
        self.frame = (self.frame + 1) % len(self.images[self.condition])
        self.image = self.images[self.condition][self.frame]

    def change_condition(self, condition):
        self.condition = condition

    def set_destination(self, coord):
        self.destination = coord
