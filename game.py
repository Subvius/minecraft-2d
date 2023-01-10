import json
import sqlite3

import sys

import pygame
from pygame.locals import *

from lib.func.load_images import load_images
from lib.func.map import *
from lib.models.arrow import Arrow
from lib.models.player import Player
from lib.models.screen import *
from lib.models.buttons import Button, set_controls_buttons
from lib.models.cave_monster import *
from lib.models.sound import Sound
from lib.models.settings import Settings
from lib.func.crafts import *
from lib.func.save_world import save
from lib.func.start import get_worlds
from lib.models.wand_charge import Charge

clock = pygame.time.Clock()

con = sqlite3.connect('lib/storage/database.db')
cursor = con.cursor()

pygame.init()
pygame.font.init()
inventory_font = pygame.font.SysFont('Comic Sans MS', 12)
main_screen_font = pygame.font.SysFont('Comic Sans MS', 16)
create_world_font = pygame.font.SysFont('Comic Sans MS', 25)

WIDTH, HEIGHT = 1184, 768
WINDOW_SIZE = (WIDTH, HEIGHT)
JUMP_HEIGHT = 2

worlds, worlds_rect = get_worlds(cursor, WINDOW_SIZE)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

display = pygame.Surface((WIDTH, HEIGHT))

moving_right = False
moving_left = False

text_field_focused = False
text_field_text = ""
input_box = pygame.Rect(WINDOW_SIZE[0] // 2 - 200, 100, 400, 50)

holding_left_button = False
hold_start = datetime.datetime.now()
hold_end = datetime.datetime.now()
hold_pos = [0, 0]

crafting_table_slots = [[None for _ in range(3)] for _ in range(3)]
inventory_crafting_slots = [[None for _ in range(2)] for __ in range(2)]
craft_result = None
with open('lib/storage/recipes.json', "r") as f:
    recipes = json.load(f)
    f.close()

settings = Settings("lib/storage/settings.json")

vertical_momentum = 0
air_timer = 0

true_scroll = [0, 0]

with open('./lib/func/blocks.json') as f:
    blocks_data = json.load(f)

images, icons, mob_images = load_images(blocks_data)

sounds = Sound()
sounds.load_all()
if settings.play_music:
    sounds.play_music("minecraft_music", -1)

screen_status = Screen()
map_objects = []
scroll = [0, 0]

falling_items = []
arrows: list[Arrow] = list()

close_to_portal = False
can_light_portal = [False, []]

selected_item = None

player_img = pygame.image.load('lib/assets/character.png')
player_rect = pygame.Rect(100, 1500, 50, 70)

player = Player(player_rect, player_img, [[None for _ in range(9)] for __ in range(4)], 0, 16.5, 20)

player.inventory.append([None for i in range(4)])

player.inventory[0][0] = {
    "type": 'block',
    'item_id': 'obsidian',
    'numerical_id': '49',
    'quantity': 64
}

player.cut_sheet(pygame.image.load("lib/assets/animations/player/idle.png"), 4, 1, "idle")
player.cut_sheet(pygame.image.load("lib/assets/animations/player/run.png"), 6, 1, "run")
player.cut_sheet(pygame.image.load("lib/assets/animations/player/throw.png"), 4, 1, "throw")

main_screen_buttons = [
    Button(label="settings", width=150, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 75, y=WINDOW_SIZE[1] // 2 + 15, hover_color="lightgray", uniq_id=1),
    Button(label="X", width=22, height=22, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] - 50, y=25, hover_color="lightgray", uniq_id=2),
    Button(label="singleplayer", width=150, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 75, y=WINDOW_SIZE[1] // 2 - 15, hover_color="lightgray", uniq_id=0
           )

]

world_select_buttons = [
    Button(label="Create New World", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", uniq_id=1),
    Button(label="Cancel", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 210, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", uniq_id=0
           )

]

create_world_buttons = [
    Button(label="Create New World", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", uniq_id=1),
    Button(label="Cancel", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 210, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", uniq_id=0
           )

]

stats_buttons = [
    Button(label="Done", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", uniq_id=0
           )

]

game_menu_buttons = [
    Button(label="Back to Game", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 - 15, hover_color="lightgray", uniq_id=0),
    Button(label="Options", width=95, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 + 15, hover_color="lightgray", uniq_id=1),
    Button(label="Statistics", width=95, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100 + 105, y=WINDOW_SIZE[1] // 2 + 15, hover_color="lightgray", uniq_id=2),
    Button(label="Save and Quit to Title", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 + 45, hover_color="lightgray", uniq_id=3),

]
options_buttons = [
    Button(label="Music & Sounds...", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 - 15, hover_color="lightgray", uniq_id=0),
    Button(label="Controls...", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 + 15, hover_color="lightgray", uniq_id=1),
    Button(label="Done", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 + 45, hover_color="lightgray", uniq_id=2),
]

music_and_sounds_buttons = [
    Button(label=f"Music: {'On' if settings.play_music else 'Off'}", width=200, height=25, background_color="gray",
           text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 - 15, hover_color="lightgray", uniq_id=0),
    Button(label=f"Blocks: {'On' if settings.blocks_sound else 'Off'}", width=200, height=25, background_color="gray",
           text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 + 15, hover_color="lightgray", uniq_id=1),
    Button(label="Done", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 + 45, hover_color="lightgray", uniq_id=2),
]

death_screen_buttons = [
    Button(label="Главное меню", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 + 15, hover_color="lightgray", uniq_id=1),
    Button(label="Возродиться", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 100, y=WINDOW_SIZE[1] // 2 - 15, hover_color="lightgray", uniq_id=0
           )

]

controls_buttons = set_controls_buttons(settings, WINDOW_SIZE)
controls_select_key = [False, 0]

animation_duration = 200
last_update = pygame.time.get_ticks()
levitating_blocks_animation = 8
blocks_animation_reverse = False
last_heal = pygame.time.get_ticks()
HEAL_DELAY = 1500
WALK_SOUND_DELAY = 500
walk_sound = 1
last_walk_sound_play = pygame.time.get_ticks()

session_stats = {
    "blocks_mined": 0,
    "blocks_placed": 0,
    "mob_killed": 0,
    "total_experience_gain": 0,
    "total_play_time": datetime.datetime.now(),
    "distance_traveled": 0,
    "total_jumps": 0,
    "successful_crafts": 0
}

mobs = list()
game_map = list()

while True:
    if screen_status.screen == 'game':
        pygame.display.set_caption(f"Minecraft 2D - {screen_status.world[4]}")
        if screen_status.dimension == 'overworld':
            if screen_status.world_time < 36000:
                percent = math.ceil(screen_status.world_time / 36000 * 100)
                if percent <= 10 or percent >= 90:
                    if 10 >= percent >= 7 or 93 >= percent >= 90:
                        display.fill((255, 239, 122))
                    elif 7 > percent >= 4 or 96 >= percent > 93:
                        display.fill((247, 193, 106))
                    elif 4 > percent >= 0 or 100 >= percent > 96:
                        display.fill((255, 107, 62))
                else:
                    display.fill((120, 167, 255))
            else:
                display.fill((39, 33, 78))
            # display.fill("black")
            # display.blit(pygame.transform.scale(images['overworld_background'], (width, height)),
            #              (0, 0 - (scroll[1] - 1370 if player.rect.y // 32 >= 57 or scroll[1] >= 1372 else 0)))
            draw_sun(display, screen_status, icons)

        elif screen_status.dimension == 'nether':
            display.fill((88, 30, 65))

        current_time = pygame.time.get_ticks()
        if current_time - last_update >= animation_duration:
            player.update_image()
            last_update = current_time

        if not screen_status.paused:
            screen_status.update_world_time()

            # update player image

            if current_time - last_heal >= HEAL_DELAY:
                player.heal()
                last_heal = current_time

        if player.frame == 3 and player.condition == 'throw':
            player.change_condition('idle')
            player.frame = 0

        true_scroll[0] += (player.rect.x - true_scroll[0] - WIDTH // 2 - player.image.get_width() // 2) / 20
        true_scroll[1] += (player.rect.y - true_scroll[1] - HEIGHT // 2 - player.image.get_height() // 2) / 20
        scroll = true_scroll.copy()

        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        map_objects = []
        possible_x = [num if abs(player_rect.x - num * 32) <= WIDTH // 2 + 64 else 0 for num in range(len(game_map[0]))]
        possible_y = [num if abs(player_rect.y - num * 32) <= WIDTH // 2 else 0 for num in range(128)]

        possible_x = list(filter((0).__ne__, possible_x))
        possible_y = list(filter((0).__ne__, possible_y))

        y = 0
        for tile_y in possible_y:
            x = 0
            for tile_x in possible_x:
                tile = game_map[tile_y][tile_x]
                block_id = tile
                percentage = 0
                # if abs(player_rect.x - x * 32) <= width // 2 and abs(player_rect.y - y * 32) <= height // 2:
                if tile.count("-") > 0:
                    separated = tile.split("-")
                    block_id = separated[0]
                    percentage = math.floor(float(separated[1]) / 10)
                if tile.count(":") > 0:

                    data = json.loads(tile)
                    block_id = list(data.keys())[0]
                    if game_map[tile_y + 1][tile_x] == "0":
                        for key in list(data.keys()):
                            for i in range(data[key]):
                                falling_items.append({
                                    "direction": "down",
                                    "x": tile_x * 32 + 8,
                                    "y": tile_y * 32,
                                    "numerical_id": key
                                })
                        game_map[tile_y][tile_x] = "0"
                    else:
                        block = blocks_data[block_id]
                        display.blit(pygame.transform.scale(images[block['item_id']], (16, 16)),
                                     (tile_x * 32 - scroll[0] + 8,
                                      tile_y * 32 - scroll[1] + levitating_blocks_animation))
                        if not blocks_animation_reverse and not screen_status.paused:
                            levitating_blocks_animation += .1
                            if int(levitating_blocks_animation) >= 12:
                                blocks_animation_reverse = True

                        if blocks_animation_reverse and not screen_status.paused:
                            levitating_blocks_animation -= .1
                            if int(levitating_blocks_animation) <= 6:
                                blocks_animation_reverse = False

                if block_id != '0' and not tile.count(":"):
                    block = blocks_data[block_id]
                    display.blit(pygame.transform.scale(images[block['item_id']], (32, 32)),
                                 (tile_x * 32 - scroll[0], tile_y * 32 - scroll[1]))

                    mouse_coord = screen_status.mouse_pos
                    mrect = pygame.Rect(mouse_coord[0], mouse_coord[1], 1, 1)
                    rect = pygame.Rect(tile_x * 32 - scroll[0], tile_y * 32 - scroll[1], 32, 32)
                    close = is_close(mouse_coord[0] + scroll[0], mouse_coord[1] + scroll[1], player.rect.x,
                                     player.rect.y, 4)

                    if mrect.colliderect(rect) and close:
                        pygame.draw.rect(display, (232, 115, 104), rect, width=2)

                    if percentage:
                        image = pygame.image.load(
                            f'./lib/assets/animations/block_breaking/image'
                            f' ({percentage if percentage < 10 else 9}).png'
                        )
                        image.set_colorkey((0, 0, 0), RLEACCEL)
                        display.blit(image, (tile_x * 32 - scroll[0], tile_y * 32 - scroll[1]))
                    if block_id != "58":
                        map_objects.append(pygame.Rect(tile_x * 32, tile_y * 32, 32, 32))
                x += 1
            y += 1

        if random.randint(0, 1000) == 5 and screen_status.world_time > 36_000 and not screen_status.paused:
            position = [random.choice(possible_x) * 32, random.choice(possible_y) * 32]
            # position = [player.rect.x, player.rect.y]

            mob = CaveMonster(20, 20, 1, 2, 1, True, False, position, 32, 64, 8)

            mobs.append(mob)

        for item in falling_items:
            rect = pygame.Rect(item["x"], item["y"], 16, 16)
            rect = rect.move(-1 if item['direction'] == 'left' else 1 if item['direction'] == 'right' else 0, 2)

            collide = False
            for block in map_objects:
                # if block.colliderect(rect):
                #     collide = True
                #     break
                if block.colliderect(rect):
                    if rect.bottom >= block.top and block.left < rect.x < block.right:
                        collide = True

                        # if game_map[(rect.bottom - 1) // 32][rect.x // 32] != "0" \
                        #         and game_map[(rect.bottom - 1) // 32][rect.x // 32].count(":") == 0:
                        #     print("entered")
                        #     for temp_y in range((rect.bottom - 1) // 32, -1, -1):
                        #         if game_map[temp_y][rect.x // 32] == "0":
                        #             rect.x = block.midtop[0]
                        #             rect.y = temp_y * 32
                        #             print('break')
                        #             break
                        # else:
                        #     rect.x, rect.bottom = block.midtop

                        if game_map[(block.top - 1) // 32][rect.x // 32] != "0" \
                                and game_map[(block.top - 1) // 32][rect.x // 32].count(":") == 0:
                            for temp_y in range((block.top - 1) // 32, -1, -1):
                                if game_map[temp_y][rect.x // 32] == "0" \
                                        or game_map[temp_y][rect.x // 32].count(":") > 0:
                                    rect.x = block.midtop[0]
                                    rect.y = temp_y * 32
                                    break
                        else:
                            rect.x, rect.bottom = block.midtop

                        data_json = game_map[rect.y // 32][rect.x // 32]
                        if data_json == "0":
                            game_map[(rect.bottom - 1) // 32][rect.x // 32] = '{_}' \
                                .replace("_", f'"{item["numerical_id"]}":{1}')
                        else:
                            data = json.loads(data_json)
                            data.update({f"{item['numerical_id']}": data.get(item["numerical_id"], 0) + 1})
                            game_map[(rect.bottom - 1) // 32][rect.x // 32] = json.dumps(data)
                        break
                    elif block.top < rect.y < block.bottom and (block.left < rect.right or block.right > rect.left):
                        rect.x = block.left if rect.right > block.left else block.right
            if collide:
                falling_items.remove(item)

            else:
                index = falling_items.index(item)

                item["x"], item['y'] = rect.x, rect.y
                falling_items[index] = item
            rect.x -= scroll[0]
            rect.y -= scroll[1]
            pygame.draw.rect(display, "black", rect)
            block = blocks_data[item['numerical_id']]
            display.blit(pygame.transform.scale(images[block['item_id']], (16, 16)), (rect.x, rect.y))

        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
            player.moving_direction = 'right'
        if moving_left:
            player_movement[0] -= 2
            player.moving_direction = 'left'

        if moving_left or moving_right:
            player.change_condition('run')
        elif player.condition != "throw":
            player.change_condition('idle')

        player_movement[1] += vertical_momentum
        vertical_momentum += 0.5
        if vertical_momentum > 3:
            vertical_momentum = 3
        player_rect, collisions = move(player.rect, player_movement, map_objects)
        player_rect.width = 32
        player_rect.height = 64
        player.rect = player_rect

        temp_rect = player_rect.copy()
        temp_rect.x -= player_movement[0]
        if temp_rect.x // 32 != player.rect.x // 32:
            session_stats['distance_traveled'] += 1

        if player.condition == 'run' and collisions['bottom'] and settings.blocks_sound:
            numerical_id = game_map[player.rect.y // 32 + 2][player.rect.x // 32]
            if numerical_id.count("{") == 0 and numerical_id != '0':
                if numerical_id.count("-") > 0:
                    numerical_id = numerical_id.split("-")[0]
                block = blocks_data[numerical_id]
                if block['material'] in ["wood", "rock", "dirt"]:
                    sound_name = block['item_id']
                    if sound_name in ['grass_block', "dirt"]:
                        sound_name = 'grass'
                    sound_name += walk_sound.__str__()
                    current_time = pygame.time.get_ticks()
                    if current_time - last_walk_sound_play > WALK_SOUND_DELAY:
                        sounds.play_sound(sound_name)
                        last_walk_sound_play = current_time
                        walk_sound += 1
                        if walk_sound > 4:
                            walk_sound = 1

        can_pick_up = player.can_pick_up(game_map)
        if can_pick_up[0]:
            blocks: dict = json.loads(can_pick_up[1])
            for block in blocks:
                if block == "998":
                    for _ in range(blocks.get(block, 1)):
                        player.add_exp(3, sounds)
                    blocks.update({block: 0})
                    continue
                for row in player.inventory:
                    row_index = player.inventory.index(row)
                    for slot in row:
                        slot_index = row.index(slot)
                        data = blocks_data[block]
                        max_size = data['max_stack_size']
                        if slot is not None:

                            if slot['quantity'] < max_size and slot['numerical_id'] == block and blocks.get(block,
                                                                                                            0) > 0:
                                slot['quantity'] += blocks.get(block, 0)

                                if slot['quantity'] > max_size:
                                    blocks.update({block: slot['quantity'] - max_size})
                                    slot['quantity'] = max_size
                                else:
                                    blocks.update({block: 0})
                        else:
                            if blocks.get(block, 0) > 0:
                                block_data = blocks_data[block]
                                slot = {
                                    "item_id": block_data['item_id'],
                                    'quantity': blocks.get(block, 0),
                                    "numerical_id": str(block),
                                    "type": "block"
                                }

                                if slot['quantity'] > max_size:
                                    blocks.update({block: slot['quantity'] - max_size})
                                    slot['quantity'] = max_size
                                else:
                                    blocks.update({block: 0})

                        player.inventory[row_index][slot_index] = slot
            filtered = {k: v for k, v in blocks.items() if v}
            blocks.clear()
            blocks.update(filtered)

            game_map[player.rect.y // 32 + 1][player.rect.x // 32] = "0" if not sum(
                list(blocks.values())) else json.dumps(
                blocks)

        if collisions['bottom']:
            air_timer = 0
            vertical_momentum = 0

            if player.jump_start is not None:
                jump_start = player.jump_start

                fall_distance = abs(player.rect.y // 32 - jump_start[1])
                damage = max(0, fall_distance - JUMP_HEIGHT * 2)
                player.damage(damage)

            player.jump_start = None
        else:
            air_timer += 1

        mobs = draw_mobs(display, player, mobs, possible_x, possible_y, scroll, map_objects, game_map, mob_images,
                         screen_status.paused, inventory_font, icons, screen_status, sounds)

        item = player.inventory[0][player.selected_inventory_slot]
        if holding_left_button and item is not None and item['item_id'] == 'bow':
            center = player.rect.center
            x, y = (center[0] - scroll[0], center[1] - scroll[1])
            draw_trajectory(display, *screen_status.mouse_pos, x, y, WIDTH)

        display.blit(
            pygame.transform.scale(pygame.transform.flip(player.image, player.moving_direction == "left", False),
                                   (32, 64)),
            (player.rect.x - scroll[0], player.rect.y - scroll[1]))
        # player.draw(display, player_rect.x - scroll[0], player_rect.y - scroll[1])

        # Рисуем предмет, который находиться в руке игрока
        if player.inventory[0][player.selected_inventory_slot] is not None and not screen_status.paused:
            draw_handholding_item(display, images, player, scroll, screen_status)

        if holding_left_button and not screen_status.paused:
            map_objects, game_map, hold_start, falling_items = on_left_click(hold_pos, player.rect, map_objects, scroll,
                                                                             game_map,
                                                                             player,
                                                                             hold_start,
                                                                             blocks_data, falling_items, mobs, False,
                                                                             sounds, session_stats)

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

        to_remove = []
        for index in range(len(screen_status.charges)):
            charge = screen_status.charges[index]
            arrived_dest = charge.move()
            if arrived_dest:
                to_remove.append(index)
            visible_rect = pygame.Rect(charge.rect.x + scroll[0], charge.rect.y + scroll[1],
                                       charge.rect.width,
                                       charge.rect.height)
            hit_list = collision_test(visible_rect, map_objects)
            if len(hit_list):
                if to_remove.count(index) == 0:
                    to_remove.append(index)
            for mob in mobs:
                if visible_rect.colliderect(mob.rect):
                    if to_remove.count(index) == 0:
                        to_remove.append(index)

                    mob.damage(charge.damage, sounds)
            charge.render(screen)

        screen_status.remove_charges(to_remove)

        if game_map[player.rect.y // 32][player.rect.x // 32 - 1] == "49":
            start_x = player.rect.x // 32 - 1
            start_y = player.rect.y // 32 - 3
            is_portal = True
            has_frames = None
            frames_to_light = []
            for tile_x in range(4):
                if not is_portal:
                    break
                for tile_y in range(5):
                    if 1 <= tile_x <= 2 and 1 <= tile_y <= 3:
                        if has_frames is None:
                            if game_map[start_y + tile_y][start_x - tile_x] == "90":
                                has_frames = True
                            else:
                                has_frames = False
                                frames_to_light.append([start_y + tile_y, start_x - tile_x])
                        elif not has_frames:
                            frames_to_light.append([start_y + tile_y, start_x - tile_x])
                    else:
                        if game_map[start_y + tile_y][start_x - tile_x] != "49":
                            is_portal = False
                            break

            if is_portal:
                close_to_portal = True
                if not has_frames:

                    can_light_portal = [True, frames_to_light]

                    start_x = player.rect.x - scroll[0] + 10
                    start_y = player.rect.y - scroll[1] - 32

                    text_surface = inventory_font.render(f"press F to light the portal", False,
                                                         "black")

                    screen.blit(text_surface, (start_x, start_y))

                else:
                    start_x = player.rect.x - scroll[0] + 10
                    start_y = player.rect.y - scroll[1] - 32

                    text_surface = inventory_font.render(f"press F to enter", False,
                                                         "black")

                    screen.blit(text_surface, (start_x, start_y))
            else:
                can_light_portal = [False]
                close_to_portal = False
        else:
            if can_light_portal[0] or close_to_portal:
                can_light_portal = [False]
                close_to_portal = False

        draw_inventory(screen, player.inventory, WIDTH, HEIGHT, inventory_font, player.selected_inventory_slot, images,
                       blocks_data)
        if player.game_mode == 'survival':
            draw_health_bar(screen, player, WIDTH, HEIGHT, icons)
            draw_exp_bar(screen, player, icons, main_screen_font)

        if screen_status.show_inventory and player.game_mode == 'survival':
            draw_expanded_inventory(screen, player.inventory, WIDTH, HEIGHT, inventory_font,
                                    images, blocks_data, inventory_crafting_slots, craft_result, player)
        elif screen_status.show_inventory and player.game_mode == 'creative':
            draw_creative_inventory(screen, player.inventory, WIDTH, HEIGHT, inventory_font,
                                    images, blocks_data, player, main_screen_font,
                                    screen_status.creative_inventory_scroll,
                                    screen_status.creative_inventory_text_field_text)
        elif screen_status.inventories.get("crafting_table", False):
            draw_crafting_table_inventory(screen, player.inventory, WIDTH, HEIGHT, inventory_font,
                                          images,
                                          blocks_data, crafting_table_slots, craft_result, main_screen_font)

        if selected_item is not None and (
                screen_status.show_inventory or sorted(list(screen_status.inventories.values()))[-1]):
            screen.blit(pygame.transform.scale(images[selected_item['item_id']], (24, 24)),
                        (selected_item["x"], selected_item["y"]))
            draw_text(screen, inventory_font, f"{selected_item['quantity']}", "white",
                      (selected_item['x'] + 10, selected_item['y'] + 10), False)

        if screen_status.paused and not player.is_dead and (
                not screen_status.show_inventory and not sorted(list(screen_status.inventories.values()))[-1]):
            draw_rect_alpha(screen, (0, 0, 0, 127,), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))

            for button in game_menu_buttons:
                button.render(screen, main_screen_font)
        elif player.is_dead:
            moving_left = moving_right = False
            if (
                    screen_status.show_inventory or sorted(list(screen_status.inventories.values()))[-1]):
                screen_status.toggle_inventory()
            screen_status.paused = True
            draw_rect_alpha(screen, (75, 0, 0, 127,), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))

            draw_text(screen, create_world_font, "Вы умерли!", "white", (WINDOW_SIZE[0] // 2 - 75, 150), True)
            draw_text(screen, main_screen_font, "Счёт: ", "white", (WINDOW_SIZE[0] // 2 - 50, 200), True)
            draw_text(screen, main_screen_font, f"{player.exp}", "yellow", (WINDOW_SIZE[0] // 2, 200), True)

            for button in death_screen_buttons:
                button.render(screen, main_screen_font)

    elif screen_status.screen == 'settings':
        pygame.display.set_caption("Minecraft 2D - Options")
        screen.blit(images['world_select_bg'], (0, 0))

        for button in options_buttons:
            button.render(screen, main_screen_font)
    elif screen_status.screen == 'music_options':
        pygame.display.set_caption("Minecraft 2D - Music & Sounds Options")
        screen.blit(images['world_select_bg'], (0, 0))

        for button in music_and_sounds_buttons:
            button.render(screen, main_screen_font)
    elif screen_status.screen == 'statistics':
        pygame.display.set_caption(f"Minecraft 2D - {screen_status.world[4]} Stats")
        screen.blit(images['world_select_bg'], (0, 0))

        for button in stats_buttons:
            button.render(screen, main_screen_font)

        with open("lib/storage/statistics.json", "r") as f:
            stats: dict = json.load(f)
        world_stats = stats[screen_status.world[1].__str__()]
        keys = list(world_stats.keys())
        for index in range(len(keys)):
            element = keys[index]
            value = world_stats[element]
            if element.count("distance") > 0:
                value = f"{value}m"
            if element.count("play_time") > 0:
                value = str(datetime.timedelta(seconds=value)) + "s"
            element = element.split("_")
            for i in range(len(element)):
                word = element[i].capitalize()
                element[i] = word

            y = 30 * index
            draw_text(screen, main_screen_font, " ".join(element), "white",
                      (WINDOW_SIZE[0] // 2 + 75 - 250, 100 - 15 + y), False)
            draw_text(screen, main_screen_font, f"{value}", "white", (WINDOW_SIZE[0] // 2 + 75, 100 - 15 + y), False)
    elif screen_status.screen == 'controls':
        pygame.display.set_caption("Minecraft 2D - Controls Options")
        screen.blit(images['world_select_bg'], (0, 0))

        for button in controls_buttons:
            button.render(screen, main_screen_font)

        keys = list(settings.convert_to_dict().keys())
        for index in range(len(keys)):
            element = keys[index]
            element = element.split("_")
            for i in range(len(element)):
                word = element[i].capitalize()
                element[i] = word

            y = 30 * index
            draw_text(screen, main_screen_font, " ".join(element), "white",
                      (WINDOW_SIZE[0] // 2 + 75 - 250, 100 - 15 + y), False)
    elif screen_status.screen == 'main':
        pygame.display.set_caption("Minecraft 2D")
        screen.blit(images['main_screen_bg'], (0, 0))

        for button in main_screen_buttons:
            button.render(screen, main_screen_font)
    elif screen_status.screen == "world_select":
        pygame.display.set_caption("Minecraft 2D - world selection")
        screen.blit(images['world_select_bg'], (0, 0))

        for button in world_select_buttons:
            button.render(screen, main_screen_font)

        for world in worlds:
            rect = worlds_rect[worlds.index(world)]
            pygame.draw.rect(screen, "white", rect, width=1)
            title = main_screen_font.render(world[4], False, "white")
            desc = main_screen_font.render(world[3], False, 'gray')
            screen.blit(title, (rect.x + 15, rect.y + 5))
            screen.blit(desc, (rect.x + 15, rect.y + 25))
    elif screen_status.screen == 'create_world':
        pygame.display.set_caption("Minecraft 2D - create new world")
        screen.blit(images['world_select_bg'], (0, 0))

        for button in create_world_buttons:
            button.render(screen, main_screen_font)

        pygame.draw.rect(screen, (127, 127, 127), input_box)
        pygame.draw.rect(screen, "white", input_box, width=3)
        world_name = create_world_font.render(text_field_text, False, (0, 0, 0))
        world_name_desc = main_screen_font.render('World Name', False, "white")
        screen.blit(world_name, (input_box.midleft[0] + 15, input_box.midleft[1] - 20))
        screen.blit(world_name_desc, (input_box.midleft[0] + 15, input_box.midleft[1] - 60))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

            save(game_map, player, screen_status, cursor, con, session_stats)

            sys.exit()
        if (
                event.type == pygame.WINDOWMINIMIZED or event.type == pygame.WINDOWFOCUSLOST) and \
                screen_status.screen == "game":
            if screen_status.paused and (
                    screen_status.show_inventory or sorted(list(screen_status.inventories.values()))[-1]):
                screen_status.toggle_inventory()
                screen_status.toggle_pause()
                text_field_focused = False
                text_field_text = ""
            elif not screen_status.paused:
                screen_status.toggle_pause()
        if event.type == pygame.KEYDOWN and screen_status.screen == 'create_world' and text_field_focused:
            if event.key == pygame.K_BACKSPACE:
                text_field_text = text_field_text[:-1]
            else:
                if len(text_field_text) < 22:
                    text_field_text += event.unicode

        if event.type == pygame.MOUSEMOTION and screen_status.screen in ['main', 'world_select', 'create_world',
                                                                         "game", 'settings', 'music_options',
                                                                         'controls', "statistics"]:
            if screen_status.screen == 'main':
                for button in main_screen_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'world_select':
                for button in world_select_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'create_world':
                for button in create_world_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'settings':
                for button in options_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'music_options':
                for button in music_and_sounds_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'statistics':
                for button in stats_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'controls':
                for button in controls_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'game' and player.is_dead:
                for button in death_screen_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'game' and screen_status.paused and (
                    not screen_status.show_inventory and not sorted(list(screen_status.inventories.values()))[-1]):
                for button in game_menu_buttons:
                    button.on_mouse_motion(*event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and screen_status.screen == 'main':
            btn = None
            for button in main_screen_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:
                    screen_status.change_scene('world_select')
                    worlds, worlds_rect = get_worlds(cursor, WINDOW_SIZE)
                elif btn.id == 1:
                    screen_status.change_scene("settings")
                elif btn.id == 2:
                    pygame.quit()
                    sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and screen_status.screen == 'world_select':
            btn = None
            for button in world_select_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:
                    screen_status.change_scene('main')
                elif btn.id == 1:
                    screen_status.change_scene('create_world')
                    text_field_text = "New world"
            rect = pygame.Rect(*event.pos, 1, 1)
            for world_rect in worlds_rect:
                if world_rect.colliderect(rect):
                    world = worlds[worlds_rect.index(world_rect)]
                    screen_status.set_world(world)
                    screen_status.change_scene('game')
                    screen_status.toggle_pause()
                    holding_left_button = False
                    with open("lib/storage/worlds_data.json", "r") as f:
                        data_json = json.load(f)
                    data = data_json[str(world[1])]
                    dimension = data.get('dimension', "overworld")
                    player.inventory = data.get("player_inventory", player.inventory)
                    player.exp = data.get("player_exp", 0)
                    player.level = math.floor(player.get_level_from_exp())
                    player.hp = data.get("player_hp", player.max_hp)
                    player.is_dead = data.get("player_is_dead", False)
                    if dimension == 'overworld':
                        coords = data["player_coord"]

                        player.rect.x = coords[0]
                        player.rect.y = coords[1]
                        game_map = data["blocks"]
                    elif dimension == 'nether':
                        with open("lib/storage/nether_worlds_data.json", "r") as f:
                            data_json = json.load(f)
                        nether_data = data_json[str(world[1])]
                        coords = nether_data["player_coord"]
                        player.rect.x = coords[0]
                        player.rect.y = coords[1]
                        game_map = nether_data["blocks"]
                        screen_status.change_dimension("nether")

                    screen_status.set_world_time(int(data.get('world_time', 0)))
                    session_stats = {
                        "blocks_mined": 0,
                        "blocks_placed": 0,
                        "mob_killed": 0,
                        "total_experience_gain": player.exp,
                        "total_play_time": datetime.datetime.now(),
                        "distance_traveled": 0,
                        "total_jumps": 0,
                        "successful_crafts": 0
                    }

        elif event.type == pygame.MOUSEBUTTONDOWN and screen_status.screen == 'create_world':
            btn = None
            for button in world_select_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:
                    screen_status.change_scene('world_select')
                    worlds, worlds_rect = get_worlds(cursor, WINDOW_SIZE)

                    text_field_text = ""
                elif btn.id == 1:
                    now = datetime.datetime.now()
                    seed = random.randint(1, 400)
                    cursor.execute(
                        f"""INSERT INTO worlds(seed, createdAt, updatedAt, name) VALUES({seed},
'{now.strftime('%d/%m/%Y, %H:%M')}', '{now.strftime('%d/%m/%Y, %H:%M')}', '{text_field_text}')""")
                    con.commit()
                    data_json = generate_chunks(screen, blocks_data, 128, 1_000, seed, "overworld")
                    with open("lib/storage/worlds_data.json", "r") as f:
                        obj = json.load(f)
                    inventory = [[None for _ in range(9)] for __ in range(4)]

                    inventory.append([None for i in range(4)])

                    obj[seed] = {
                        "seed": seed,
                        "name": text_field_text,
                        "player_coord": (1000 * 32 // 2, 60 * 32),
                        "blocks": data_json,
                        "player_inventory": inventory,
                        'player_hp': 20,
                        "player_exp": 0
                    }
                    with open("lib/storage/worlds_data.json", "w") as f:
                        json.dump(obj, f)

                    world = (
                        -1, seed, now.strftime('%d/%m/%Y, %H:%M'), now.strftime('%d/%m/%Y, %H:%M'), text_field_text)
                    screen_status.set_world(world)
                    screen_status.change_scene('game')
                    screen_status.toggle_pause()
                    holding_left_button = False
                    game_map = data_json
                    player.rect.x = 1000 * 32 // 2
                    player.rect.y = 60 * 32
                    player.exp = 0
                    player.level = math.floor(player.get_level_from_exp())
                    player.inventory = inventory
                    screen_status.reset_world_time()
                    session_stats = {
                        "blocks_mined": 0,
                        "blocks_placed": 0,
                        "mob_killed": 0,
                        "total_experience_gain": player.exp,
                        "total_play_time": datetime.datetime.now(),
                        "distance_traveled": 0,
                        "total_jumps": 0,
                        "successful_crafts": 0
                    }

            rect = pygame.Rect(*event.pos, 1, 1)
            if rect.colliderect(input_box):
                text_field_focused = True
            else:
                text_field_focused = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not player.is_dead and screen_status.screen == 'game' and \
                screen_status.paused and (
                not screen_status.show_inventory and not sorted(list(screen_status.inventories.values()))[-1]):
            btn = None
            for button in game_menu_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:
                    screen_status.toggle_pause()
                    holding_left_button = False
                elif btn.id == 1:
                    screen_status.change_scene("settings")
                elif btn.id == 2:
                    screen_status.change_scene("statistics")
                elif btn.id == 3:
                    save(game_map, player, screen_status, cursor, con, session_stats)
                    screen_status.change_scene("world_select")
                    worlds, worlds_rect = get_worlds(cursor, WINDOW_SIZE)
                    screen_status.set_world(None)

        elif event.type == pygame.MOUSEBUTTONDOWN and screen_status.screen == 'settings':
            btn = None
            for button in options_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:
                    screen_status.change_scene('music_options')
                elif btn.id == 1:
                    screen_status.change_scene('controls')
                elif btn.id == 2:
                    if screen_status.world is not None:
                        screen_status.change_scene('game')
                    else:
                        screen_status.change_scene("main")

        elif event.type == pygame.MOUSEBUTTONDOWN and screen_status.screen == 'game' and player.is_dead:
            btn = None
            for button in death_screen_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:
                    player.is_dead = False
                    player.heal(20)
                    player.change_condition("idle")

                    player.rect.x = 1000 * 32 // 2
                    player.rect.y = 60 * 32
                elif btn.id == 1:
                    save(game_map, player, screen_status, cursor, con, session_stats)
                    screen_status.change_scene("world_select")
                    worlds, worlds_rect = get_worlds(cursor, WINDOW_SIZE)
                    screen_status.set_world(None)
        elif event.type == pygame.MOUSEBUTTONDOWN and screen_status.screen == 'statistics':
            btn = None
            for button in stats_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:

                    if screen_status.world is not None:
                        screen_status.change_scene('game')
                    else:
                        screen_status.change_scene("main")
        elif event.type == pygame.MOUSEBUTTONDOWN and screen_status.screen == 'music_options':
            btn = None
            for button in music_and_sounds_buttons:
                res = button.on_mouse_click(*event.pos)
                if res:
                    btn = button
                    break
            if btn is not None:
                if btn.id == 0:
                    new_value = not settings.play_music
                    music_and_sounds_buttons[0].label = f"Music: {'On' if new_value else 'Off'}"
                    settings.update_setting("music", new_value)
                    if new_value:
                        sounds.play_music("minecraft_music", -1)
                    else:
                        sounds.stop_music("minecraft_music", 200)
                elif btn.id == 1:
                    new_value = not settings.blocks_sound
                    music_and_sounds_buttons[1].label = f"Blocks: {'On' if new_value else 'Off'}"
                    settings.update_setting("blocks", new_value)
                elif btn.id == 2:
                    screen_status.change_scene('settings')

        elif (event.type == pygame.MOUSEBUTTONDOWN or (
                event.type == pygame.KEYDOWN and controls_select_key[0])) and screen_status.screen == 'controls':
            if controls_select_key[0]:
                keys = list(settings.default.keys())
                key = keys[controls_select_key[1]]
                new_value = None
                if event.type == pygame.KEYDOWN:
                    char = event.unicode
                    name = pygame.key.name(event.key)
                    if name.count("alt") or name.count("ctrl") or name.count("shift"):
                        pass
                    else:
                        if name in ["space", "return"]:
                            new_value = f"K_{name.upper()}"
                        else:
                            if char != "":
                                new_value = "K_" + char
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    new_value = event.button
                if new_value is not None:
                    settings.update_setting(key, new_value)
                    controls_buttons = set_controls_buttons(settings, WINDOW_SIZE)

                    controls_select_key = [False, 0]

            else:
                btn = None
                for button in controls_buttons:
                    res = button.on_mouse_click(*event.pos)
                    if res:
                        btn = button
                        break
                if btn is not None:
                    if btn.id not in [9, 10]:
                        controls_select_key = [True, btn.id]
                        btn.toggle_high_light()
                    elif btn.id == 9:
                        screen_status.change_scene('settings')
                    elif btn.id == 10:
                        keys = list(settings.default.keys())
                        for key in keys:
                            settings.update_setting(key, settings.default.get(key))
                        controls_buttons = set_controls_buttons(settings, WINDOW_SIZE)

        if event.type == pygame.MOUSEMOTION and not screen_status.paused \
                and screen_status.screen == 'game' and not player.is_dead:
            coord = event.pos
            screen_status.set_mouse_pos(coord)

        if event.type == pygame.MOUSEBUTTONDOWN and not player.is_dead and event.button == settings.use_item and \
                not screen_status.paused \
                and screen_status.screen == 'game' and (
                not screen_status.show_inventory and not sorted(list(screen_status.inventories.values()))[-1]):

            map_objects, game_map = on_right_click(event, player.rect, map_objects, scroll, game_map, player,
                                                   screen_status, session_stats)

            item = player.inventory[0][player.selected_inventory_slot]
            if item is not None and item['item_id'].count("wand") > 0:
                data = blocks_data[item["numerical_id"]]
                x0, y0 = (player.rect.midleft[0] - scroll[0], player.rect.midleft[1] - scroll[1])
                charge = Charge(item['item_id'], "charge", (x0, y0), event.pos, 3, data.get('charge_damage', 1), WIDTH,
                                HEIGHT)
                screen_status.add_charge(charge)
        if event.type == pygame.MOUSEBUTTONDOWN and not player.is_dead and event.button == settings.attack and \
                not screen_status.paused \
                and screen_status.screen == 'game':
            holding_left_button = True
            hold_start = datetime.datetime.now()
            hold_pos = event.pos
            map_objects, game_map, hold_start, falling_items = on_left_click(hold_pos, player.rect, map_objects, scroll,
                                                                             game_map,
                                                                             player,
                                                                             hold_start,
                                                                             blocks_data, falling_items, mobs, True,
                                                                             sounds, session_stats)

        if event.type == pygame.MOUSEBUTTONUP and event.button == settings.attack and not screen_status.paused \
                and screen_status.screen == 'game':
            holding_left_button = False
            hold_end = datetime.datetime.now()

        if event.type == pygame.MOUSEBUTTONDOWN and not player.is_dead and event.button in [1,
                                                                                            3] and \
                screen_status.screen == "game" \
                and (screen_status.show_inventory or sorted(list(screen_status.inventories.values()))[-1]):
            window_width = (288 - 50) * 1.25
            window_height = (256 - 30) * 1.25
            left = WIDTH // 2 - window_width // 2
            top = HEIGHT // 2 - window_height // 2
            mx = event.pos[0]
            my = event.pos[1]

            rect = pygame.Rect(left, top, WIDTH, HEIGHT)
            mouse_rect = pygame.Rect(mx, my, 1, 1)
            # Пользователь кликнул в инвентарь
            if rect.colliderect(mouse_rect):
                # В какой слот кликнул пользователь
                item = None
                button = event.button
                if 10 <= mx - left <= 10 + 9 * 30 + 1 * 9 and (42 + 3 * 30 + 1 * 3) + 10 <= my - top <= (
                        42 + 3 * 30 + 1 * 3) + 10 + 30 * 3 + 1 * 3 and (
                        player.game_mode == 'survival' or sorted(list(screen_status.inventories.values()))[-1]):
                    size = 30
                    column = int(mx - left + 15) // size
                    row = int((my - top - (
                            42 + 3 * 30 + 1 * 3) - 10) // size)
                    item = player.inventory[row + 1][column - 1]
                    if item is not None and selected_item is None:
                        if button == 1:
                            block = blocks_data[item["numerical_id"]]

                            selected_item = {
                                "x": mx,
                                "y": my,
                                "item_id": block['item_id'],
                                "quantity": item["quantity"],
                                "type": item["type"],
                                "numerical_id": block['numerical_id']
                            }
                            if player.inventory[row + 1][column - 1].get('best_for', None) is not None:
                                selected_item.update(
                                    {"best_for": player.inventory[row + 1][column - 1].get('best_for', None)})

                            player.remove_from_inventory(column - 1, item['quantity'], row + 1)
                        elif button == 3 and item['quantity'] // 2 != 0:
                            block = blocks_data[item["numerical_id"]]

                            selected_item = {
                                "x": mx,
                                "y": my,
                                "item_id": block['item_id'],
                                "quantity": item["quantity"] // 2,
                                "type": item["type"],
                                "numerical_id": block['numerical_id']
                            }
                            item['quantity'] -= item['quantity'] // 2
                            player.inventory[row + 1][column - 1] = item

                    elif item is None and selected_item is not None:
                        if button == 1:
                            player.inventory[row + 1][column - 1] = {
                                "type": selected_item['type'],
                                'item_id': selected_item['item_id'],
                                'numerical_id': selected_item['numerical_id'],
                                'quantity': selected_item['quantity']
                            }
                            if selected_item.get('best_for', None) is not None:
                                player.inventory[row + 1][column - 1].update(
                                    {"best_for": selected_item.get('best_for', None)})

                            selected_item = None
                        elif button == 3:
                            player.inventory[row + 1][column - 1] = {
                                "type": selected_item['type'],
                                'item_id': selected_item['item_id'],
                                'numerical_id': selected_item['numerical_id'],
                                'quantity': 1
                            }

                            if selected_item['quantity'] - 1 == 0:
                                selected_item = None
                            else:
                                selected_item['quantity'] -= 1
                    elif item is not None and selected_item is not None:
                        if item['item_id'] == selected_item['item_id']:
                            block = blocks_data[item['numerical_id']]
                            max_size = block.get("max_stack_size", 1)
                            if int(item["quantity"]) < max_size:
                                item['quantity'] += selected_item['quantity'] if button == 1 else 1

                                if item['quantity'] > max_size:
                                    selected_item['quantity'] = item['quantity'] - max_size
                                    item['quantity'] = max_size
                                    player.inventory[row + 1][column - 1] = item
                                else:
                                    if button == 1:
                                        selected_item = None
                                    else:
                                        selected_item['quantity'] -= 1
                                        if selected_item["quantity"] <= 0:
                                            selected_item = None
                        else:
                            if button == 1:
                                player.inventory[row + 1][column - 1], selected_item = selected_item, \
                                                                                       player.inventory[row + 1][
                                                                                           column - 1]
                                selected_item['x'] = mx
                                selected_item['y'] = my
                elif 10 <= mx - left <= 10 + 9 * 30 + 1 * 9 and 52 <= my - top <= 52 + 30 * 6 + 1 * 6 and \
                        player.game_mode == 'creative' and screen_status.show_inventory and \
                        player.creative_inventory_page != 'inventory':
                    size = 30
                    column = int(mx - left + 15) // size - 1
                    row = int((my - top - 52) // size)
                    if player.creative_inventory_page == 'search':
                        text = screen_status.creative_inventory_text_field_text
                        blocks_to_show: dict = {}
                        if text != "":
                            for block in blocks_data:
                                if blocks_data[block]['item_id'].__contains__(text):
                                    blocks_to_show.update({block: blocks_data[block]})
                        else:
                            blocks_to_show = blocks_data

                        index = row * 9 + column + screen_status.creative_inventory_scroll * 9
                        if index < len(list(blocks_to_show.keys())) and selected_item is None:
                            keys = pygame.key.get_pressed()
                            block = blocks_to_show.get(list(blocks_to_show.keys())[index])
                            selected_item = {
                                "item_id": block['item_id'],
                                "numerical_id": block['numerical_id'],
                                "quantity": block["max_stack_size"] if keys[pygame.K_LSHIFT] else 1,
                                'x': mx,
                                'y': my,
                                "type": 'block' if block.get("material", None) is not None else "tool" if block.get(
                                    "best_for", None) is not None else "item",
                            }
                            if block.get("best_for", None) is not None:
                                selected_item.update({"best_for": block.get("best_for", None)})
                        elif selected_item is not None:
                            selected_item = None

                elif 10 <= mx - left <= 10 + 9 * 30 + 1 * 9 and (
                        (42 + 3 * 30 + 1 * 3) + 10 + 30 * 2 + 1 * 2) + 40 <= my - top <= (
                        (42 + 3 * 30 + 1 * 3) + 10 + 30 * 2 + 1 * 2) + 70:
                    size = 30
                    column = int(mx - left + 15) // size
                    row = 0
                    try:
                        item = player.inventory[row][column - 1]

                        if item is not None and selected_item is None:
                            if button == 1:
                                block = blocks_data[item["numerical_id"]]

                                selected_item = {
                                    "x": mx,
                                    "y": my,
                                    "item_id": block['item_id'],
                                    "quantity": item["quantity"],
                                    "type": item["type"],
                                    "numerical_id": block['numerical_id']
                                }
                                if player.inventory[row][column - 1].get('best_for', None) is not None:
                                    selected_item.update(
                                        {"best_for": player.inventory[row][column - 1].get('best_for', None)})

                                player.remove_from_inventory(column - 1, item['quantity'], row)
                            elif button == 3 and item['quantity'] // 2 != 0:
                                block = blocks_data[item["numerical_id"]]

                                selected_item = {
                                    "x": mx,
                                    "y": my,
                                    "item_id": block['item_id'],
                                    "quantity": item["quantity"] // 2,
                                    "type": item["type"],
                                    "numerical_id": block['numerical_id']
                                }
                                item['quantity'] -= item['quantity'] // 2
                                player.inventory[row][column - 1] = item
                        elif item is None and selected_item is not None:
                            if button == 1:
                                player.inventory[row][column - 1] = {
                                    "type": selected_item['type'],
                                    'item_id': selected_item['item_id'],
                                    'numerical_id': selected_item['numerical_id'],
                                    'quantity': selected_item['quantity']
                                }
                                if selected_item.get('best_for', None) is not None:
                                    player.inventory[row][column - 1].update(
                                        {"best_for": selected_item.get('best_for', None)})
                                selected_item = None
                            elif button == 3:
                                player.inventory[row][column - 1] = {
                                    "type": selected_item['type'],
                                    'item_id': selected_item['item_id'],
                                    'numerical_id': selected_item['numerical_id'],
                                    'quantity': 1
                                }

                                if selected_item['quantity'] - 1 == 0:
                                    selected_item = None
                                else:
                                    selected_item['quantity'] -= 1
                        elif item is not None and selected_item is not None:
                            if item['item_id'] == selected_item['item_id']:
                                block = blocks_data[item['numerical_id']]
                                max_size = block.get("max_stack_size", 1)
                                if int(item["quantity"]) < max_size:
                                    item['quantity'] += selected_item['quantity'] if button == 1 else 1

                                    if item['quantity'] > max_size:
                                        selected_item['quantity'] = item['quantity'] - max_size
                                        item['quantity'] = max_size
                                        player.inventory[row][column - 1] = item
                                    else:
                                        if button == 1:
                                            selected_item = None
                                        else:
                                            selected_item['quantity'] -= 1
                                            if selected_item["quantity"] <= 0:
                                                selected_item = None
                            else:
                                if button == 1:
                                    player.inventory[row][column - 1], selected_item = selected_item, \
                                                                                       player.inventory[row][
                                                                                           column - 1]
                                    selected_item['x'] = mx
                                    selected_item['y'] = my
                    except IndexError:
                        print('INDEX ERROR')
                if button == 1 and (
                        player.game_mode == 'survival' or sorted(list(screen_status.inventories.values()))[-1]):
                    if (10 + 4 * 30 + 1 * 4 + 20) <= mx - left <= (10 + 4 * 30 + 1 * 4 + 20) + 2 * 30 + 1 * 2 and (
                            11 + 32) <= my - top <= (11 + 32) + 30 * 2 + 1 * 2 and screen_status.show_inventory:
                        size = 30
                        column = int(mx - left - (10 + 4 * 30 + 1 * 4 + 20)) // size
                        row = int((my - top - (11 + 32)) // size)
                        if inventory_crafting_slots[row][column] is None and selected_item is not None:
                            inventory_crafting_slots[row][column] = {
                                'item_id': selected_item["item_id"], 'quantity': selected_item["quantity"],
                                'type': selected_item["type"], 'numerical_id': selected_item["numerical_id"]
                            }
                            selected_item = None
                        elif inventory_crafting_slots[row][column] is not None and selected_item is None:
                            selected_item = inventory_crafting_slots[row][column]
                            selected_item["x"] = mx
                            selected_item["y"] = my
                            inventory_crafting_slots[row][column] = None

                        res = check_if_can_craft(True, inventory_crafting_slots, recipes)
                        print(res)
                        if res[0]:
                            craft_result = res[2]
                            print(craft_result)
                        else:
                            craft_result = None
                    elif (10 + 4 * 30 + 1 * 4 + 20) + 1 * 30 + 1 * 1 + 68 <= mx - left <= (
                            10 + 4 * 30 + 1 * 4 + 20) + 1 * 30 + 1 * 1 + 98 and (
                            11 + 30) + 30 * 1 + 1 * 1 - 15 <= my - top <= (
                            11 + 30) + 30 * 1 + 1 * 1 + 15 and screen_status.show_inventory:
                        if craft_result is not None:
                            block = get_block_data_by_name(blocks_data, craft_result['result']['item'])
                            if selected_item is None:
                                selected_item = {
                                    "item_id": block['item_id'],
                                    "numerical_id": block['numerical_id'],
                                    "quantity": craft_result['result'].get("count", 1),
                                    'x': mx,
                                    'y': my,
                                    "type": 'block' if block.get("material", None) is not None else "tool" if block.get(
                                        "best_for", None) is not None else "item",
                                }
                            elif selected_item is not None and selected_item["item_id"] == block["item_id"]:
                                selected_item['quantity'] += craft_result['result'].get("count", 1)
                            if selected_item['item_id'] == block['item_id']:
                                if block.get("best_for", None) is not None:
                                    selected_item.update({"best_for": block.get("best_for", None)})
                                for row in inventory_crafting_slots:
                                    row_index = inventory_crafting_slots.index(row)
                                    for slot in row:
                                        slot_index = row.index(slot)
                                        if slot is not None:
                                            slot["quantity"] -= 1
                                            if slot['quantity'] <= 0:
                                                inventory_crafting_slots[row_index][slot_index] = None
                                            else:
                                                inventory_crafting_slots[row_index][slot_index] = slot
                                session_stats['successful_crafts'] += 1
                                res = check_if_can_craft(True, inventory_crafting_slots, recipes)
                                if res[0]:
                                    craft_result = res[2]
                                else:
                                    craft_result = None

                    if 41 <= mx - left <= 41 + 3 * 30 + 1 * 3 and 25 <= my - top <= 25 + 30 * 3 + 1 * 3 \
                            and screen_status.inventories.get("crafting_table", False):
                        size = 30
                        column = int(mx - left - 41) // size
                        row = int((my - top - 25) // size)
                        if crafting_table_slots[row][column] is None and selected_item is not None:
                            crafting_table_slots[row][column] = {
                                'item_id': selected_item["item_id"], 'quantity': selected_item["quantity"],
                                'type': selected_item["type"], 'numerical_id': selected_item["numerical_id"]
                            }
                            selected_item = None
                        elif crafting_table_slots[row][column] is not None and selected_item is None:
                            selected_item = crafting_table_slots[row][column]
                            selected_item["x"] = mx
                            selected_item["y"] = my
                            crafting_table_slots[row][column] = None

                        res = check_if_can_craft(False, crafting_table_slots, recipes)
                        print(res)
                        if res[0]:
                            craft_result = res[2]
                            print(craft_result)
                        else:
                            craft_result = None
                    elif (10 + 4 * 30 + 1 * 4 + 20) + 68 - 33 <= mx - left <= (10 + 4 * 30 + 1 * 4 + 20) + 68 - 3 and (
                            11 + 30) + 30 * 1 + 1 * 1 - 15 <= my - top <= (
                            11 + 30) + 30 * 1 + 1 * 1 + 15 and screen_status.inventories.get("crafting_table", False):
                        if craft_result is not None:
                            block = get_block_data_by_name(blocks_data, craft_result['result']['item'])
                            if selected_item is None:
                                selected_item = {
                                    "item_id": block['item_id'],
                                    "numerical_id": block['numerical_id'],
                                    "quantity": craft_result['result'].get("count", 1),
                                    'x': mx,
                                    'y': my,
                                    "type": 'block' if block.get("material", None) is not None else "tool" if block.get(
                                        "best_for", None) is not None else "item",
                                }
                            elif selected_item is not None and selected_item["item_id"] == block["item_id"]:
                                selected_item['quantity'] += craft_result['result'].get("count", 1)
                            if selected_item['item_id'] == block['item_id']:
                                if block.get("best_for", None) is not None:
                                    selected_item.update({"best_for": block.get("best_for", None)})
                                for row in crafting_table_slots:
                                    row_index = crafting_table_slots.index(row)
                                    for slot in row:
                                        slot_index = row.index(slot)
                                        if slot is not None:
                                            slot["quantity"] -= 1
                                            if slot['quantity'] <= 0:
                                                crafting_table_slots[row_index][slot_index] = None
                                            else:
                                                crafting_table_slots[row_index][slot_index] = slot
                                session_stats['successful_crafts'] += 1

                                res = check_if_can_craft(False, crafting_table_slots, recipes)
                                if res[0]:
                                    craft_result = res[2]
                                else:
                                    craft_result = None
                elif button == 1 and player.game_mode == 'creative' and screen_status.show_inventory and \
                        player.creative_inventory_page == 'search':
                    x = left + 14 + 30 * 4
                    y = top + 14
                    box_width = 30 * 5 + 2
                    box_height = 24

                    search_rect = pygame.Rect(x, y, box_width, box_height)
                    if search_rect.collidepoint(mx, my):
                        text_field_focused = True
                    else:
                        text_field_focused = False

        if event.type == pygame.MOUSEMOTION and not player.is_dead and screen_status.screen == "game" and (
                screen_status.show_inventory or sorted(list(screen_status.inventories.values()))[-1]) \
                and selected_item is not None:
            rel = event.pos
            selected_item["x"] = rel[0]
            selected_item["y"] = rel[1]

        if event.type == pygame.MOUSEWHEEL and screen_status.screen == "game" and (
                not screen_status.show_inventory and not sorted(list(screen_status.inventories.values()))[-1]):
            player.set_selected_slot(player.selected_inventory_slot - event.y)

        if event.type == pygame.MOUSEWHEEL and screen_status.screen == "game" and screen_status.show_inventory and \
                player.game_mode == 'creative':
            screen_status.update_creative_scroll(-event.y, blocks_data)

        if event.type == KEYDOWN and not player.is_dead and screen_status.screen == 'game' and not text_field_focused:
            if event.key == eval(f"pygame.{settings.inventory}"):
                screen_status.toggle_inventory()
                moving_left = moving_right = False
                craft_result = None
            elif event.key == pygame.K_ESCAPE:
                if not screen_status.show_inventory and not sorted(list(screen_status.inventories.values()))[-1]:
                    screen_status.toggle_pause()
                    holding_left_button = False
                    moving_left = moving_right = False
                    craft_result = None
                else:
                    screen_status.toggle_inventory()
                    moving_left = moving_right = False
                    craft_result = None
        if event.type == KEYDOWN and not player.is_dead and not screen_status.paused \
                and screen_status.screen == 'game' and not text_field_focused:
            if event.key == K_RIGHT or event.key == eval(f"pygame.{settings.move_right}"):
                moving_right = True
            if event.key == eval(f"pygame.{settings.toggle_creative_mode}"):
                player.change_game_mode("creative" if player.game_mode == "survival" else "survival")
            if event.key == K_LEFT or event.key == eval(f"pygame.{settings.move_left}"):
                moving_left = True
            if event.key == K_UP or event.key == eval(f"pygame.{settings.jump}"):
                if air_timer < 6:
                    vertical_momentum = -8
                    player.jump_start = (player.rect.x // 32, player.rect.y // 32)
                    session_stats['total_jumps'] += 1

            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                             pygame.K_8, pygame.K_9, ]:
                player.set_selected_slot(int(event.key) - 49)

            if event.key == eval(f"pygame.{settings.portal_interact}") and can_light_portal[0]:
                for block in can_light_portal[1]:
                    game_map[block[0]][block[1]] = "90"

            if event.key == eval(f"pygame.{settings.portal_interact}") and close_to_portal and not can_light_portal[0] \
                    and screen_status.dimension == 'overworld':
                seed: int = screen_status.world[1]

                with open("lib/storage/worlds_data.json", "r") as f:
                    data_json = json.load(f)

                data_json[str(screen_status.world[1])]["blocks"] = game_map
                data_json[str(screen_status.world[1])]['player_coord'] = (player.rect.x, player.rect.y)
                with open("lib/storage/worlds_data.json", "w") as f:
                    json.dump(data_json, f)

                with open("lib/storage/nether_worlds_data.json", "r") as f:
                    world_data = json.load(f)
                if world_data.get(seed.__str__(), None) is None:
                    data_json = generate_chunks(screen, blocks_data, 128, 125, seed, "nether")
                    player_coord = (125 * 32 // 2, 60 * 32)
                    with open("lib/storage/nether_worlds_data.json", "r") as f:
                        obj = json.load(f)
                    start_x = player_coord[0] // 32 - 1
                    start_y = player_coord[1] // 32 - 3
                    for tile_x in range(4):
                        for tile_y in range(5):
                            if 1 <= tile_x <= 2 and 1 <= tile_y <= 3:
                                data_json[start_y + tile_y][start_x - tile_x] = "90"
                            else:
                                data_json[start_y + tile_y][start_x - tile_x] = "49"
                    data_json[player_coord[1] // 32][player_coord[0] // 32] = "0"
                    data_json[player_coord[1] // 32 - 1][player_coord[0] // 32] = "0"

                    obj[seed] = {
                        "seed": seed,
                        "player_coord": player_coord,
                        "blocks": data_json
                    }
                    with open("lib/storage/nether_worlds_data.json", "w") as f:
                        json.dump(obj, f)
                    now = datetime.datetime.now()
                    screen_status.change_dimension('nether')
                    game_map = data_json
                    player.rect.x, player.rect.y = player_coord
                else:
                    data = world_data.get(seed.__str__())
                    screen_status.change_dimension('nether')
                    game_map = data['blocks']
                    player.rect.x = data["player_coord"][0]
                    player.rect.y = data["player_coord"][1]

            elif event.key == eval(f"pygame.{settings.portal_interact}") and close_to_portal and \
                    not can_light_portal[0] and screen_status.dimension == 'nether':
                seed: int = screen_status.world[1]

                with open("lib/storage/nether_worlds_data.json", "r") as f:
                    data_json = json.load(f)

                data_json[str(screen_status.world[1])]["blocks"] = game_map
                data_json[str(screen_status.world[1])]['player_coord'] = (player.rect.x, player.rect.y)
                with open("lib/storage/nether_worlds_data.json", "w") as f:
                    json.dump(data_json, f)

                with open("lib/storage/worlds_data.json", "r") as f:
                    world_data = json.load(f)
                data = world_data.get(seed.__str__())
                screen_status.change_dimension('overworld')
                game_map = data['blocks']
                player.rect.x = data["player_coord"][0]
                player.rect.y = data["player_coord"][1]

            if event.key == eval(f"pygame.{settings.drop}"):
                if player.inventory[0][player.selected_inventory_slot] is not None:
                    direction = player.moving_direction
                    x, y = player.rect.x, player.rect.y

                    num_id = player.inventory[0][player.selected_inventory_slot]['numerical_id']

                    falling_items.append({
                        "direction": direction,
                        "x": x if direction == "right" else x + 16,
                        "y": y,
                        "numerical_id": num_id
                    })
                    player.remove_from_inventory(player.selected_inventory_slot, 1)
                    player.change_condition('throw')
                    player.frame = 0
        if event.type == KEYDOWN and not player.is_dead and screen_status.screen == 'game' and text_field_focused:
            text = screen_status.creative_inventory_text_field_text
            if event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            else:
                if len(text) < 16:
                    text += event.unicode
                    print(text)

            screen_status.update_creative_text(text)

        if event.type == KEYUP and not screen_status.paused \
                and screen_status.screen == 'game':
            if event.key == K_RIGHT or event.key == eval(f"pygame.{settings.move_right}"):
                moving_right = False
            if event.key == K_LEFT or event.key == eval(f"pygame.{settings.move_left}"):
                moving_left = False

    pygame.display.update()
    clock.tick(60)
