import datetime
import json
import os
import random
import sqlite3

import sys

import pygame.image
from pygame.locals import *

from lib.func.map import *
from lib.models.player import *
from lib.models.screen import *
from lib.models.buttons import *
from lib.models.entity import *

clock = pygame.time.Clock()

con = sqlite3.connect('lib/storage/database.db')
cursor = con.cursor()

worlds = cursor.execute("SELECT * FROM worlds").fetchall()
worlds_rect = list()

pygame.init()
pygame.font.init()
inventory_font = pygame.font.SysFont('Comic Sans MS', 12)
main_screen_font = pygame.font.SysFont('Comic Sans MS', 16)
create_world_font = pygame.font.SysFont('Comic Sans MS', 25)

width, height = 1184, 768
WINDOW_SIZE = (width, height)
JUMP_HEIGHT = 2

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

for world in worlds:
    x = WINDOW_SIZE[0] // 2 - 210
    y = 200 + 60 * world[0]
    rect = pygame.Rect(x, y, 410, 55)
    worlds_rect.append(rect)

display = pygame.Surface((width, height))

moving_right = False
moving_left = False

text_field_focused = False
text_field_text = ""
input_box = pygame.Rect(WINDOW_SIZE[0] // 2 - 200, 100, 400, 50)

holding_left_button = False
hold_start = datetime.datetime.now()
hold_end = datetime.datetime.now()
hold_pos = [0, 0]

vertical_momentum = 0
air_timer = 0

true_scroll = [0, 0]

with open('./lib/func/blocks.json') as f:
    blocks_data = json.load(f)

images = dict()
icons = dict()

for block in list(blocks_data.values()):
    images.update({block['item_id']: pygame.image.load(f"lib/assets/{block['image_root']}")})
images.update({"main_screen_bg": pygame.image.load("lib/assets/main_screen_bg.jpg")})
images.update({"world_select_bg": pygame.image.load("lib/assets/world_select_bg.jpg")})

for file in os.listdir("lib/assets/icons"):
    if file.endswith(".webp"):
        icons.update({f"{file.split('.')[0]}": pygame.image.load(f"lib/assets/icons/{file}")})

screen_status = Screen()

falling_items = []
close_to_portal = False
can_light_portal = [False, []]

selected_item = None
"""
{
    "x" : int,
    "y" : int,
    "item_id" : int,
    "quantity" : int
}
"""

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
           x=WINDOW_SIZE[0] // 2 - 75, y=WINDOW_SIZE[1] // 2 + 15, hover_color="lightgray", id=1),
    Button(label="X", width=22, height=22, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] - 50, y=25, hover_color="lightgray", id=2),
    Button(label="singleplayer", width=150, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 75, y=WINDOW_SIZE[1] // 2 - 15, hover_color="lightgray", id=0
           )

]

world_select_buttons = [
    Button(label="Create New World", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", id=1),
    Button(label="Cancel", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 210, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", id=0
           )

]

create_world_buttons = [
    Button(label="Create New World", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", id=1),
    Button(label="Cancel", width=200, height=25, background_color="gray", text_color="white",
           x=WINDOW_SIZE[0] // 2 - 210, y=int(WINDOW_SIZE[1] // 1.075), hover_color="lightgray", id=0
           )

]




animation_duration = 200
last_update = pygame.time.get_ticks()
levitating_blocks_animation = 8
blocks_animation_reverse = False
last_heal = pygame.time.get_ticks()
HEAL_DELAY = 1500

mobs = list()

while True:
    if screen_status.screen == 'game':
        pygame.display.set_caption(f"Minecraft 2D - {screen_status.world[4]}")
        if screen_status.dimension == 'overworld':
            display.fill((146, 244, 255))
        elif screen_status.dimension == 'nether':
            display.fill((88, 30, 65))

        # update player image
        current_time = pygame.time.get_ticks()
        if current_time - last_update >= animation_duration:
            player.update_image()
            last_update = current_time

        if current_time - last_heal >= HEAL_DELAY:
            player.heal()
            last_heal = current_time

        if player.frame == 3 and player.condition == 'throw':
            player.change_condition('idle')
            player.frame = 0

        true_scroll[0] += (player.rect.x - true_scroll[0] - width // 2 - player.image.get_width() // 2) / 20
        true_scroll[1] += (player.rect.y - true_scroll[1] - height // 2 - player.image.get_height() // 2) / 20
        scroll = true_scroll.copy()

        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        map_objects = []
        possible_x = [num if abs(player_rect.x - num * 32) <= width // 2 + 64 else 0 for num in range(len(game_map[0]))]
        possible_y = [num if abs(player_rect.y - num * 32) <= width // 2 else 0 for num in range(128)]

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

                    block = blocks_data[block_id]
                    display.blit(pygame.transform.scale(images[block['item_id']], (16, 16)),
                                 (tile_x * 32 - scroll[0] + 8, tile_y * 32 - scroll[1] + levitating_blocks_animation))
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
                    display.blit(images[block['item_id']], (tile_x * 32 - scroll[0], tile_y * 32 - scroll[1]))

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

                    map_objects.append(pygame.Rect(tile_x * 32, tile_y * 32, 32, 32))
                x += 1
            y += 1

        if random.randint(0, 1000) == 5:
            print('mobb')
            position = [random.choice(possible_x) * 32, random.choice(possible_y) * 32]
            # position = [player.rect.x, player.rect.y]

            mob = Entity(20, 20, 1, 2, 1, True, False, position, 32, 64, 8)
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

        can_pick_up = player.can_pick_up(game_map)
        if can_pick_up[0]:
            blocks: dict = json.loads(can_pick_up[1])
            for block in blocks:
                for row in player.inventory:
                    row_index = player.inventory.index(row)
                    for slot in row:
                        slot_index = row.index(slot)
                        if slot is not None:
                            if slot['quantity'] < 64 and slot['numerical_id'] == block and blocks.get(block, 0) > 0:
                                slot['quantity'] += blocks.get(block, 0)

                                if slot['quantity'] > 64:
                                    blocks.update({block: slot['quantity'] - 64})
                                    slot['quantity'] = 64
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

                                if slot['quantity'] > 64:
                                    blocks.update({block: slot['quantity'] - 64})
                                    slot['quantity'] = 64
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

        display.blit(
            pygame.transform.scale(pygame.transform.flip(player.image, player.moving_direction == "left", False),
                                   (32, 64)),
            (player.rect.x - scroll[0], player.rect.y - scroll[1]))
        # player.draw(display, player_rect.x - scroll[0], player_rect.y - scroll[1])

        if holding_left_button:
            map_objects, game_map, hold_start, falling_items = on_left_click(hold_pos, player.rect, map_objects, scroll,
                                                                             game_map,
                                                                             player,
                                                                             hold_start,
                                                                             blocks_data, falling_items)

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

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

        draw_inventory(screen, player.inventory, width, height, inventory_font, player.selected_inventory_slot, images,
                       blocks_data)
        draw_health_bar(screen, player, width, height, icons)

        draw_mobs(screen, player, mobs, possible_x, possible_y, scroll, map_objects, game_map)

        if screen_status.show_inventory:
            draw_expanded_inventory(screen, player.inventory, width, height, inventory_font,
                                    images,
                                    blocks_data)

        if selected_item is not None:
            screen.blit(pygame.transform.scale(images[selected_item['item_id']], (24, 24)),
                        (selected_item["x"], selected_item["y"]))
            text_surface = inventory_font.render(f"{selected_item['quantity']}", False,
                                                 "white")

            screen.blit(text_surface, (selected_item['x'] + 10, selected_item['y'] + 10))

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

            if screen_status.world is not None:
                if screen_status.dimension == 'overworld':
                    with open("lib/storage/worlds_data.json", "r") as f:
                        data_json = json.load(f)

                    data_json[str(screen_status.world[1])]["blocks"] = game_map
                    data_json[str(screen_status.world[1])]["player_inventory"] = player.inventory
                    data_json[str(screen_status.world[1])]["player_hp"] = player.hp
                    data_json[str(screen_status.world[1])]['player_coord'] = (player.rect.x, player.rect.y)
                    with open("lib/storage/worlds_data.json", "w") as f:
                        json.dump(data_json, f)
                else:
                    if screen_status.dimension == 'nether':
                        with open("lib/storage/nether_worlds_data.json", "r") as f:
                            data_json = json.load(f)

                        data_json[str(screen_status.world[1])]["blocks"] = game_map
                        data_json[str(screen_status.world[1])]['player_coord'] = (player.rect.x, player.rect.y)
                        with open("lib/storage/nether_worlds_data.json", "w") as f:
                            json.dump(data_json, f)

                    with open("lib/storage/worlds_data.json", "r") as f:
                        data_json = json.load(f)

                    data_json[str(screen_status.world[1])]["player_inventory"] = player.inventory
                    data_json[str(screen_status.world[1])]["player_hp"] = player.hp
                    with open("lib/storage/worlds_data.json", "w") as f:
                        json.dump(data_json, f)

                cursor.execute(
                    f"UPDATE worlds SET updatedAt = '{datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}'"
                    f" WHERE seed = {screen_status.world[1]}")
                con.commit()

            sys.exit()

        if event.type == pygame.KEYDOWN and screen_status.screen == 'create_world' and text_field_focused:
            if event.key == pygame.K_BACKSPACE:
                text_field_text = text_field_text[:-1]
            else:
                if len(text_field_text) < 22:
                    text_field_text += event.unicode

        if event.type == pygame.MOUSEMOTION and screen_status.screen in ['main', 'world_select', 'create_world']:
            if screen_status.screen == 'main':
                for button in main_screen_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'world_select':
                for button in world_select_buttons:
                    button.on_mouse_motion(*event.pos)
            elif screen_status.screen == 'create_world':
                for button in create_world_buttons:
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
                if btn.id == 2:
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
                if btn.id == 1:
                    screen_status.change_scene('create_world')
                    text_field_text = "New world"
            rect = pygame.Rect(*event.pos, 1, 1)
            for world_rect in worlds_rect:
                if world_rect.colliderect(rect):
                    world = worlds[worlds_rect.index(world_rect)]
                    screen_status.set_world(world)
                    screen_status.change_scene('game')
                    screen_status.toggle_pause()
                    with open("lib/storage/worlds_data.json", "r") as f:
                        data_json = json.load(f)
                    game_map = data_json[str(world[1])]["blocks"]
                    coords = data_json[str(world[1])]["player_coord"]
                    player.inventory = data_json[str(world[1])].get("player_inventory", player.inventory)
                    player.hp = data_json[str(world[1])].get("player_hp", player.max_hp)
                    player.rect.x = coords[0]
                    player.rect.y = coords[1]

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
                    text_field_text = ""
                if btn.id == 1:
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
                        'player_hp': 20
                    }
                    with open("lib/storage/worlds_data.json", "w") as f:
                        json.dump(obj, f)

                    world = (
                        -1, seed, now.strftime('%d/%m/%Y, %H:%M'), now.strftime('%d/%m/%Y, %H:%M'), text_field_text)
                    screen_status.set_world(world)
                    screen_status.change_scene('game')
                    screen_status.toggle_pause()
                    game_map = data_json
                    player.rect.x = 1000 * 32 // 2
                    player.rect.y = 60 * 32
                    player.inventory = inventory

            rect = pygame.Rect(*event.pos, 1, 1)
            if rect.colliderect(input_box):
                text_field_focused = True
            else:
                text_field_focused = False

        if event.type == pygame.MOUSEMOTION and not screen_status.paused \
                and screen_status.screen == 'game':
            coord = event.pos
            screen_status.set_mouse_pos(coord)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not screen_status.paused \
                and screen_status.screen == 'game':
            map_objects, game_map = on_right_click(event, player.rect, map_objects, scroll, game_map, player)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not screen_status.paused \
                and screen_status.screen == 'game':
            holding_left_button = True
            hold_start = datetime.datetime.now()
            hold_pos = event.pos
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not screen_status.paused \
                and screen_status.screen == 'game':
            holding_left_button = False
            hold_end = datetime.datetime.now()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and screen_status.screen == "game" and screen_status.show_inventory:
            window_width = (288 - 50) * 1.25
            window_height = (256 - 30) * 1.25
            left = width // 2 - window_width // 2
            top = height // 2 - window_height // 2
            mx = event.pos[0]
            my = event.pos[1]

            rect = pygame.Rect(left, top, width, height)
            mouse_rect = pygame.Rect(mx, my, 1, 1)
            # Пользователь кликнул в инвентарь
            if rect.colliderect(mouse_rect):
                # В какой слот кликнул пользователь
                item = None
                if 10 <= mx - left <= 10 + 9 * 30 + 1 * 9 and (42 + 3 * 30 + 1 * 3) + 10 <= my - top <= (
                        42 + 3 * 30 + 1 * 3) + 10 + 30 * 3 + 1 * 3:
                    size = 30
                    column = int(mx - left + 15) // size
                    row = int((my - top - (
                            42 + 3 * 30 + 1 * 3) - 10) // size)
                    item = player.inventory[row + 1][column - 1]
                    if item is not None and selected_item is None:
                        block = blocks_data[item["numerical_id"]]

                        selected_item = {
                            "x": mx,
                            "y": my,
                            "item_id": block['item_id'],
                            "quantity": item["quantity"],
                            "type": item["type"],
                            "numerical_id": block['numerical_id']
                        }

                        player.remove_from_inventory(column - 1, item['quantity'], row + 1)
                    elif item is None and selected_item is not None:
                        player.inventory[row + 1][column - 1] = {
                            "type": selected_item['type'],
                            'item_id': selected_item['item_id'],
                            'numerical_id': selected_item['numerical_id'],
                            'quantity': selected_item['quantity']
                        }
                        selected_item = None
                elif 10 <= mx - left <= 10 + 9 * 30 + 1 * 9 and (
                        (42 + 3 * 30 + 1 * 3) + 10 + 30 * 2 + 1 * 2) + 40 <= my - top <= (
                        (42 + 3 * 30 + 1 * 3) + 10 + 30 * 2 + 1 * 2) + 70:
                    size = 30
                    column = int(mx - left + 15) // size
                    row = 0
                    item = player.inventory[row][column - 1]

                    if item is not None and selected_item is None:
                        block = blocks_data[item["numerical_id"]]

                        selected_item = {
                            "x": mx,
                            "y": my,
                            "item_id": block['item_id'],
                            "quantity": item["quantity"],
                            "type": item["type"],
                            "numerical_id": block['numerical_id']
                        }

                        player.remove_from_inventory(column - 1, item['quantity'], row)
                    elif item is None and selected_item is not None:
                        player.inventory[row][column - 1] = dict(type=selected_item['type'],
                                                                 item_id=selected_item['item_id'],
                                                                 numerical_id=selected_item['numerical_id'],
                                                                 quantity=selected_item['quantity'])
                        selected_item = None

        if event.type == pygame.MOUSEMOTION and screen_status.screen == "game" and screen_status.show_inventory \
                and selected_item is not None:
            rel = event.pos
            selected_item["x"] = rel[0]
            selected_item["y"] = rel[1]

        if event.type == pygame.MOUSEWHEEL and screen_status.screen == "game" and not screen_status.show_inventory:
            player.set_selected_slot(player.selected_inventory_slot - event.y)

        if event.type == KEYDOWN and screen_status.screen == 'game':
            if event.key == pygame.K_e:
                screen_status.toggle_inventory()
                screen_status.toggle_pause()
                moving_left = moving_right = False
        if event.type == KEYDOWN and not screen_status.paused \
                and screen_status.screen == 'game':
            if event.key == K_RIGHT or event.key == pygame.K_d:
                moving_right = True
            if event.key == K_LEFT or event.key == pygame.K_a:
                moving_left = True
            if event.key == K_UP or event.key == pygame.K_SPACE:
                if air_timer < 6:
                    vertical_momentum = -8
                    player.jump_start = (player.rect.x // 32, player.rect.y // 32)

            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                             pygame.K_8, pygame.K_9, ]:
                player.set_selected_slot(int(event.key) - 49)

            if event.key == pygame.K_f and can_light_portal[0]:
                for block in can_light_portal[1]:
                    game_map[block[0]][block[1]] = "90"

            if event.key == pygame.K_f and close_to_portal and not can_light_portal[0] \
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

            elif event.key == pygame.K_f and close_to_portal and not can_light_portal[0] \
                    and screen_status.dimension == 'nether':
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

            if event.key == pygame.K_q:
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

        if event.type == KEYUP and not screen_status.paused \
                and screen_status.screen == 'game':
            if event.key == K_RIGHT or event.key == pygame.K_d:
                moving_right = False
            if event.key == K_LEFT or event.key == pygame.K_a:
                moving_left = False

    pygame.display.update()
    clock.tick(60)
