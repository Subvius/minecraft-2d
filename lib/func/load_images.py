import os
import pygame
from lib.models.cave_monster import CaveMonster


def load_images(blocks_data: dict):
    images = dict()
    icons = dict()
    mob_images = dict()

    for block in list(blocks_data.values()):
        images.update({block['item_id']: pygame.image.load(f"lib/assets/{block['image_root']}")})
    images.update({"main_screen_bg": pygame.image.load("lib/assets/main_screen_bg.jpg")})
    images.update({"world_select_bg": pygame.image.load("lib/assets/world_select_bg.jpg")})
    images.update({"no_textures": pygame.image.load("lib/assets/no_textures.webp")})

    for file in os.listdir("lib/assets/items"):
        if file.endswith(".png"):
            images.update({file.split(".")[0]: pygame.image.load(f"lib/assets/items/{file}")})

    for file in os.listdir("lib/assets/icons"):
        if file.endswith(".webp") or file.endswith(".png"):
            icons.update({f"{file.split('.')[0]}": pygame.image.load(f"lib/assets/icons/{file}")})

    icons.update({"sun": pygame.image.load("lib/assets/sun.png")})
    icons.update({"moon": pygame.image.load("lib/assets/moon.png")})

    for folder in os.listdir("lib/assets/animations/mobs/"):
        mob_images.update({folder: {}})
        for file in os.listdir(f"lib/assets/animations/mobs/{folder}"):
            mob_images[folder][file.split(".")[0]] = pygame.image.load(f"lib/assets/animations/mobs/{folder}/{file}")

    mob = CaveMonster(20, 20, 1, 2, 1, True, False, (0, 0), 32, 64, 8)
    mob.cut_sheet(mob_images["cave_monster"]["idle"], 4, 1, "idle", 120, 50)
    mob_images['cave_monster']['idle'] = mob.images
    mob.cut_sheet(mob_images["cave_monster"]["walk"], 6, 1, "walk", 120, 45)
    mob_images['cave_monster']['walk'] = mob.images

    return images, icons, mob_images
