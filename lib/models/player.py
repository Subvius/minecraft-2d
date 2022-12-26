import pygame


class Player:
    def __init__(self, rect, image, inventory, selected_inventory_slot, hp, max_hp):
        self.rect: pygame.Rect = rect
        self.width: int = 50
        self.image = image
        self.inventory: list = inventory
        self.selected_inventory_slot: int = selected_inventory_slot
        self.hp: float = hp
        self.jump_start = None
        self.max_hp: int = max_hp
        self.images = {
            "idle": [],
            'run': [],
            'throw': [],
        }
        self.frame = 0
        self.condition = "run"
        self.moving_direction = "right"
        self.is_dead = False
        self.exp = 0

    def cut_sheet(self, sheet, columns, rows, animation_type):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.width * i + 29 * i, (self.width - 2) * j)
                image = sheet.subsurface(pygame.Rect(
                    frame_location, (self.width, 70)))
                self.images[animation_type].append(image)

    def update_image(self):
        self.frame = (self.frame + 1) % len(self.images[self.condition])
        self.image = self.images[self.condition][self.frame]

    def change_condition(self, condition):
        self.condition = condition

    def draw(self, screen, x, y):
        screen.blit(self.image, (x, y))

    def remove_from_inventory(self, slot: int, quantity: int, row: int = 0):
        self.inventory[row][slot]["quantity"] -= quantity
        if self.inventory[row][slot]["quantity"] <= 0:
            self.inventory[row][slot] = None

    def set_selected_slot(self, slot: int):
        self.selected_inventory_slot = slot

    def can_pick_up(self, game_map: list):
        block = game_map[self.rect.y // 32 + 1][self.rect.x // 32]
        rect = pygame.Rect(self.rect.x, self.rect.y, 32, 64)
        if block.count(":") and rect.colliderect(self.rect):
            return True, block
        return False, None

    def heal(self, hp: int = 1):
        self.hp += hp
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def damage(self, damage: int = 0):
        self.hp -= damage

        if self.hp <= 0:
            self.is_dead = True
