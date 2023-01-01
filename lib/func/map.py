import datetime
import math
import random

import noise
import pygame

import lib.models.screen
from lib.models.player import Player
from lib.func.blocks import *
from lib.models.entity import *


def collision_test(rect, tiles):
    hit_list = []
    for tile_elem in tiles:
        if rect.colliderect(tile_elem):
            hit_list.append(tile_elem)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile_elem in hit_list:
        if movement[0] > 0:
            rect.right = tile_elem.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile_elem.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile_elem in hit_list:
        if movement[1] > 0:
            rect.bottom = tile_elem.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile_elem.bottom
            collision_types['top'] = True
    return rect, collision_types


def is_close(x, y, x0, y0, radius) -> bool:
    return ((x - x0) ** 2 + (y - y0) ** 2) <= (radius * 32) ** 2


def on_right_click(event, player_rect, map_objects, scroll, game_map, player: Player):
    pos = event.pos
    x = pos[0]
    y = pos[1]
    # максимальная дистанция 4 блока (сторона 32)
    close = is_close(x + scroll[0], y + scroll[1], player.rect.x, player.rect.y, 4)
    if close:
        value_x = (x + scroll[0]) // 32
        value_y = (y + scroll[1]) // 32
        try:
            tile = game_map[value_y][value_x]
            # игрок кликнул по "воздуху" и рядом с "воздухом есть блок"
            if tile == "0":
                if game_map[value_y + 1][value_x] != "0" or game_map[value_y - 1][value_x] != "0" \
                        or game_map[value_y][value_x + 1] != "0" or game_map[value_y][value_x - 1] != "0":
                    selected = player.inventory[0][player.selected_inventory_slot]
                    if selected is not None and selected['type'] == 'block':
                        game_map[value_y][value_x] = selected['numerical_id']
                        map_objects.append(pygame.Rect(value_x * 32, value_y * 32, 32, 32))
                        player.remove_from_inventory(player.selected_inventory_slot, 1)
        except IndexError:
            print('доделать!!!!! (lib/models/map.py), line: 26')

    return map_objects, game_map


def on_left_click(pos, player_rect, map_objects, scroll, game_map, player: Player, hold_start, blocks_data,
                  falling_items):
    x = pos[0]
    y = pos[1]
    # максимальная дистанция 4 блока (сторона 32)
    close = is_close(x + scroll[0], y + scroll[1], player.rect.x, player.rect.y, 4)
    if close:
        value_x = (x + scroll[0]) // 32
        value_y = (y + scroll[1]) // 32
        try:
            data = game_map[value_y][value_x]
            tile = data if not data.count("-") else data.split("-")[0]
            if tile != "0" and not tile.count(":"):

                block_data = blocks_data[tile]
                if type(block_data) == dict:
                    if block_data.get('diggable', 0):
                        breaking_time = calculate_breaking_time(block_data['hardness'], 1)
                        now = datetime.datetime.now()
                        if now - hold_start >= datetime.timedelta(seconds=breaking_time):
                            game_map[value_y][value_x] = '0'
                            map_objects.remove(pygame.Rect(value_x * 32, value_y * 32, 32, 32))
                            hold_start = now

                            num_id = tile
                            x += scroll[0]
                            y += scroll[1]
                            falling_items.append({
                                "direction": "down",
                                "x": x,
                                "y": y,
                                "numerical_id": num_id
                            })
                        else:
                            time_spent = now - hold_start
                            percentage = (time_spent / datetime.timedelta(
                                seconds=breaking_time)) * 100
                            game_map[value_y][value_x] = f"{tile}-{int(percentage)}"

        except IndexError:
            print('доделать!!!!! (lib/models/map.py), line: 26')

    return map_objects, game_map, hold_start, falling_items


def draw_mobs(screen: pygame.Surface, player: Player, mobs: list[Entity], possible_x: list[int], possible_y: list[int],
              scroll: list[int], map_objects: list[pygame.Rect], game_map: list, images):
    for mob in mobs:
        rect = mob.rect
        if rect.x // 32 in possible_x and rect.y // 32 in possible_y:
            # pygame.draw.rect(screen, "black",
            #                  pygame.Rect(rect.x - scroll[0], rect.y - scroll[1], rect.width,
            #                              rect.height))
            image = images[mob.mob_type][mob.condition][mob.condition][mob.frame]
            screen.blit(pygame.transform.flip(pygame.transform.scale(image, (mob.width, mob.height)),
                                              mob.moving_direction == 'left', False),
                        (rect.x - scroll[0], rect.y - scroll[1]))
        else:
            mobs.remove(mob)
        close = is_close(rect.x, rect.y, player.rect.x, player.rect.y, mob.trigger_radius)
        if close:
            mob.set_destination(player.rect.midtop)
        else:
            mob.set_destination(None)
        destination = mob.destination

        movement = [0, 0]
        if destination is not None:
            if rect.x < destination[0]:
                movement[0] += 1 * mob.speed
                mob.moving_direction = 'left'
            elif rect.x > destination[0]:
                movement[0] -= 1 * mob.speed
                mob.moving_direction = 'right'

        if movement == [0, 0]:
            if mob.condition != 'idle':
                mob.change_condition('idle')
        else:
            if mob.condition == 'idle':
                mob.change_condition('walk')

        try:
            if game_map[rect.y // 32 + 1][rect.x // 32] == "0":
                movement[1] += 1
        except IndexError:
            # Escaped from map :(
            pass

        movement[1] += mob.vertical_momentum
        rect, collisions = move(rect, movement, map_objects)
        mob.vertical_momentum += 0.5
        if mob.vertical_momentum > 3:
            mob.vertical_momentum = 3
        if collisions['bottom']:
            mob.vertical_momentum = 0

        if movement[0] > 0 and collisions['bottom'] and collisions['right'] and mob.vertical_momentum == 0:
            mob.vertical_momentum -= mob.jump_height * 4.5

        elif movement[0] < 0 and collisions['bottom'] and collisions['left'] and mob.vertical_momentum == 0:
            mob.vertical_momentum -= mob.jump_height * 4.5

        mob.rect = rect
        current_time = pygame.time.get_ticks()
        if current_time - mob.last_update > mob.animation_duration:
            mob.update_image(len(images[mob.mob_type][mob.condition][mob.condition]))
            mob.last_update = current_time

        if mob.rect.topleft == player.rect.midtop:
            if current_time - mob.last_attack >= mob.attack_delay:
                player.damage(mob.attack_damage)
                mob.last_attack = current_time

    return mobs


def draw_health_bar(screen, player: Player, width, height, icons):
    hp = player.hp

    for i in range(10):
        rect = pygame.Rect(width // 2 - 32 * 4.5 + i * (32 * 0.4), height - 58, 32 * 0.4, 32 * 0.4)
        icon = icons["heart"]
        heart = i + 1

        if int(hp) % 2 == 0:
            if heart * 2 > int(hp):
                icon = icons['empty_heart']
        else:
            if heart * 2 - 1 == int(hp):
                icon = icons['half_heart']
            elif heart * 2 - 1 > int(hp):
                icon = icons['empty_heart']

        screen.blit(pygame.transform.scale(icon, (32 * 0.4, 32 * 0.4)), (rect.x, rect.y))


def draw_inventory(screen, inventory, width, height, font, selected_slot, images, blocks_data):
    color = (0, 10, 0)
    # selected_color = (145, 145, 145)
    selected_color = "white"

    for i in range(9):
        rect = pygame.Rect(width // 2 - 32 * 4.5 + i * 32, height - 32, 32, 32)
        pygame.draw.rect(screen, selected_color if i == selected_slot else color,
                         rect, width=2)
        if inventory[0][i]:
            block = blocks_data[inventory[0][i]['numerical_id']]
            screen.blit(pygame.transform.scale(images[block["item_id"]], (16, 16)), (rect.x + 8, rect.y + 8))

            text_surface = font.render(f"{inventory[0][i]['quantity']}", False,
                                       selected_color if i == selected_slot else color)

            screen.blit(text_surface, (rect.x + 16, rect.y + 16))


def draw_expanded_inventory(screen, inventory, width, height, font, images, blocks_data,
                            inventory_crafting_slots: list, craft_result: dict):
    window_width = (288 - 50) * 1.25
    window_height = (256 - 30) * 1.25
    left = width // 2 - window_width // 2
    top = height // 2 - window_height // 2
    # Palette
    tile_color = (160, 160, 160)
    tile_size = 30
    block_size = 22
    background_color = (215, 215, 215)
    pygame.draw.rect(screen, background_color,
                     pygame.Rect(left, top, window_width, window_height))

    pygame.draw.line(screen, "white", (left, top), (left + window_width, top))
    pygame.draw.line(screen, "white", (left, top), (left, top + window_height))
    pygame.draw.line(screen, "black", (left + window_width, top),
                     (left + window_width, top + window_height))
    pygame.draw.line(screen, "black", (left, top + window_height),
                     (left + window_width, top + window_height))

    # Armor render
    for i in range(4):
        y = 10 + i * tile_size + 1 * i
        x = 10
        pygame.draw.rect(screen, tile_color,
                         pygame.Rect(left + x, top + y, 28, 28))
        pygame.draw.line(screen, "black", (left + x, top + y), (left + x + 28, top + y))
        pygame.draw.line(screen, "black", (left + x, top + y), (left + x, top + y + 28))
        pygame.draw.line(screen, "white", (left + x, top + y + 28), (left + x + 28, top + y + 28))
        pygame.draw.line(screen, "white", (left + x + 28, top + y), (left + x + 28, top + y + 28))

        if inventory[4][i] is not None:
            block = blocks_data[inventory[4][i]['numerical_id']]
            screen.blit(pygame.transform.scale(images[block["item_id"]], (block_size, block_size)),
                        (left + x + (tile_size - block_size) // 2, top + y + (tile_size - block_size) // 2))

    # Slots render
    slot_number = 0
    for tile_y in range(3):
        for tile_x in range(9):
            x = 10 + tile_x * tile_size + 1 * tile_x
            y = (42 + 3 * tile_size + 1 * 3) + 10 + tile_size * tile_y + 1 * tile_y
            pygame.draw.rect(screen, tile_color,
                             pygame.Rect(left + x, top + y, 28, 28))
            pygame.draw.line(screen, "black", (left + x, top + y), (left + x + 28, top + y))
            pygame.draw.line(screen, "black", (left + x, top + y), (left + x, top + y + 28))
            pygame.draw.line(screen, "white", (left + x, top + y + 28), (left + x + 28, top + y + 28))
            pygame.draw.line(screen, "white", (left + x + 28, top + y), (left + x + 28, top + y + 28))

            if inventory[tile_y + 1][tile_x] is not None:
                block = blocks_data[inventory[tile_y + 1][tile_x]['numerical_id']]
                screen.blit(pygame.transform.scale(images[block["item_id"]], (block_size, block_size)),
                            (left + x + (tile_size - block_size) // 2, top + y + (tile_size - block_size) // 2))

                text_surface = font.render(f"{inventory[tile_y + 1][tile_x]['quantity']}", False,
                                           "white")

                screen.blit(text_surface, (left + x + tile_size - 16, top + y + tile_size - 16))
            slot_number += 1

    # Hotbar render
    for i in range(9):
        y = ((42 + 3 * tile_size + 1 * 3) + 10 + tile_size * 2 + 1 * 2) + 40
        x = 10 + i * tile_size + 1 * i
        pygame.draw.rect(screen, tile_color,
                         pygame.Rect(left + x, top + y, 28, 28))
        pygame.draw.line(screen, "black", (left + x, top + y), (left + x + 28, top + y))
        pygame.draw.line(screen, "black", (left + x, top + y), (left + x, top + y + 28))
        pygame.draw.line(screen, "white", (left + x, top + y + 28), (left + x + 28, top + y + 28))
        pygame.draw.line(screen, "white", (left + x + 28, top + y), (left + x + 28, top + y + 28))

        if inventory[0][i] is not None:
            block = blocks_data[inventory[0][i]['numerical_id']]
            screen.blit(pygame.transform.scale(images[block["item_id"]], (block_size, block_size)),
                        (left + x + (tile_size - block_size) // 2, top + y + (tile_size - block_size) // 2))

            text_surface = font.render(f"{inventory[0][i]['quantity']}", False,
                                       "white")

            screen.blit(text_surface, (left + x + tile_size - 16, top + y + tile_size - 16))

    # Player area render
    y = 10
    x = 41
    pl_width = 28 * 3 + 6
    pl_height = 28 * 4 + 9
    pygame.draw.rect(screen, "black",
                     pygame.Rect(left + x, top + y, pl_width, pl_height))
    pygame.draw.line(screen, "black", (left + x, top + y), (left + x + pl_width, top + y))
    pygame.draw.line(screen, "black", (left + x, top + y), (left + x, top + y + pl_height))
    pygame.draw.line(screen, "white", (left + x, top + y + pl_height), (left + x + pl_width, top + y + pl_height))
    pygame.draw.line(screen, "white", (left + x + pl_width, top + y), (left + x + pl_width, top + y + pl_height))

    # Craft area render
    for tile_x in range(2):
        for tile_y in range(2):
            x = (10 + 4 * tile_size + 1 * 4 + 20) + tile_x * tile_size + 1 * tile_x
            y = (11 + 32) + tile_size * tile_y + 1 * tile_y
            pygame.draw.rect(screen, tile_color,
                             pygame.Rect(left + x, top + y, 28, 28))
            pygame.draw.line(screen, "black", (left + x, top + y), (left + x + 28, top + y))
            pygame.draw.line(screen, "black", (left + x, top + y), (left + x, top + y + 28))
            pygame.draw.line(screen, "white", (left + x, top + y + 28), (left + x + 28, top + y + 28))
            pygame.draw.line(screen, "white", (left + x + 28, top + y), (left + x + 28, top + y + 28))

            if inventory_crafting_slots[tile_y][tile_x] is not None:
                block = blocks_data[inventory_crafting_slots[tile_y][tile_x]['numerical_id']]
                screen.blit(pygame.transform.scale(images[block["item_id"]], (block_size, block_size)),
                            (left + x + (tile_size - block_size) // 2, top + y + (tile_size - block_size) // 2))

                text_surface = font.render(f"{inventory_crafting_slots[tile_y][tile_x]['quantity']}", False,
                                           "white")

                screen.blit(text_surface, (left + x + tile_size - 16, top + y + tile_size - 16))

    x = (10 + 4 * tile_size + 1 * 4 + 20) + 1 * tile_size + 1 * 1 + 33
    y = (11 + tile_size) + tile_size * 1 + 1 * 1 - 2
    pygame.draw.rect(screen, tile_color, pygame.Rect(left + x, top + y, 25, 4))
    step = 1
    for index in range(12):
        pygame.draw.line(screen, tile_color, (left + x + tile_size - 11 + index * 1, top + y - 9 + index * step),
                         (left + x + tile_size - 11 + index * 1, top + y + 13 - index * step))

    x = (10 + 4 * tile_size + 1 * 4 + 20) + 1 * tile_size + 1 * 1 + 68
    y = (11 + tile_size) + tile_size * 1 + 1 * 1 - 15
    pygame.draw.rect(screen, tile_color,
                     pygame.Rect(left + x, top + y, 28, 28))
    if craft_result is not None:
        result = craft_result.get("result")
        item = result['item']
        count = result.get("count", 1)

        block = get_block_data_by_name(blocks_data, item)
        screen.blit(pygame.transform.scale(images[block["item_id"]], (block_size, block_size)),
                    (left + x + (tile_size - block_size) // 2, top + y + (tile_size - block_size) // 2))

        text_surface = font.render(f"{count}", False,
                                   "white")

        screen.blit(text_surface, (left + x + tile_size - 16, top + y + tile_size - 16))

    pygame.draw.line(screen, "black", (left + x, top + y), (left + x + 28, top + y))
    pygame.draw.line(screen, "black", (left + x, top + y), (left + x, top + y + 28))
    pygame.draw.line(screen, "white", (left + x, top + y + 28), (left + x + 28, top + y + 28))
    pygame.draw.line(screen, "white", (left + x + 28, top + y), (left + x + 28, top + y + 28))


def draw_sun(screen: pygame.Surface, screen_status: lib.models.screen.Screen, icons: dict[str: pygame.Surface]):
    world_time = screen_status.world_time
    DAY_TIME = 36_000
    NIGHT_TIME = 12_000
    Y_MAX = 200
    Y_MIN = 100
    day_night_cycle_percent = world_time / DAY_TIME * 100 if world_time / DAY_TIME * 100 <= 100 else \
        (world_time - DAY_TIME) / NIGHT_TIME * 100
    width, height = screen.get_width(), screen.get_height()
    image = icons["sun"] if world_time / DAY_TIME * 100 <= 100 else icons["moon"]

    pos = (width // 100 * day_night_cycle_percent, (
            Y_MAX - Y_MAX // 100 * day_night_cycle_percent) if day_night_cycle_percent <= 50 else \
        Y_MIN + Y_MAX // 100 * (day_night_cycle_percent - 50))
    screen.blit(pygame.transform.scale(image, (64, 64)), pos)


def generate_chunks(screen, blocks_data, y_max, quantity_of_chunks, seed, dimension):
    x_max = 8 * quantity_of_chunks
    game_map = [["0" for _ in range(x_max)] for _ in range(y_max)]

    mountains = [
        r"""       /\
      /33\
     /3333\
    /333333\
   /33333333\
  /3333333333\
 /333333333333\
/33333333333333\ """,
        r"""       /\    /\
      /33\  /33\
     /3333\/3333\
    /333333333333\
   /33333333333333\
  /3333333333333333\
 /333333333333333333\
/33333333333333333333\ """,
        r"""       /\
      /33\  /\
     /3333\/33\
    /3333333333\
   /333333333333\
  /33333333333333\
 /3333333333333333\
/333333333333333333\ """,
        r"""       /\
      /33\
     /3333\
    /333333\  /\
   /33333333\/33\
  /33333333333333\
 /3333333333333333\
/333333333333333333\ """
    ]

    trees = [
        """ 1111
 1112111
111121111
    2
    2"""
    ]

    if dimension == 'overworld':
        for tile_y in range(y_max):
            for tile_x in range(x_max):

                # if 65 == tile_y:
                #     value = random.randint(1, 1000)
                #
                #     if 30 <= value < 60:
                #         house_list = house_schema.split("\n")
                #         house_list = house_list[::-1]
                #         for y_adder in range(len(house_list)):
                #             for x_adder in range(len(house_list[0])):
                #                 try:
                #                     current = house_list[y_adder][x_adder]
                #                     if current == "7":
                #                         current = "17"
                #                     elif current == '3':
                #                         current = "324"
                #                     elif current == " ":
                #                         current = "0"
                #                     game_map[tile_y + y_adder][tile_x - len(house_list[0]) + x_adder] = current
                #                 except IndexError:
                #                     # мы вышли за границу карты
                #                     pass

                if tile_y == 0:
                    block = get_block_data_by_name(blocks_data, 'stone')
                    game_map[tile_y][tile_x] = block['numerical_id'] if block is not None else '0'
                elif 1 <= tile_y <= 60:
                    value = random.randint(0, 1000)
                    block_id = 0
                    if 0 <= value <= 624:
                        block_id = get_block_data_by_name(blocks_data, 'stone')['numerical_id']
                    elif 925 <= value <= 1000:
                        block_id = ore_generator(tile_y, y_max)

                    game_map[tile_y][tile_x] = block_id.__str__()
                elif 60 <= tile_y <= 64:
                    block_id = get_block_data_by_name(blocks_data, 'dirt')['numerical_id']

                    game_map[tile_y][tile_x] = block_id.__str__()
                elif 65 <= tile_y <= 70:
                    # value = random.randint(1, 1000)
                    height = math.floor(noise.pnoise1(tile_x * 0.1, repeat=9999999) * (seed ** 0.5))

                    if tile_y <= (70 + 65) // 2 - height and game_map[tile_y][tile_x] == "0":
                        game_map[tile_y][tile_x] = "1"
                    # if 1 <= value <= 30:
                    #     if game_map[tile_y - 1][tile_x] != "0":
                    #         mountain = mountains[random.randint(1, 4) - 1]
                    #
                    #         mountain = mountain.replace('/', "1")
                    #         mountain = mountain.replace('\\', "1")
                    #         mountain = mountain.replace(' ', "0")
                    #         mountain_list = mountain.split("\n")
                    #         print(mountain_list)
                    #         mountain_list = mountain_list[::-1]
                    #         print(mountain_list)
                    #
                    #         for y_adder in range(len(mountain_list)):
                    #             for x_adder in range(len(mountain_list[0])):
                    #                 try:
                    #                     current = mountain_list[y_adder][x_adder]
                    #                     game_map[tile_y + y_adder][tile_x - len(mountain_list[0]) + x_adder] = current
                    #                 except IndexError:
                    #                     # мы вышли за границу карты
                    #                     pass
                    #             print()

                if game_map[tile_y][tile_x - 5] == "0" and game_map[tile_y - 1][tile_x - 5] != "0" \
                        and 70 >= tile_y >= 65:
                    value = random.randint(1, 1000)
                    if 0 <= value <= 100:
                        tree = random.choice(trees)
                        tree = tree.replace(' ', "0")
                        tree = tree.split("\n")
                        tree = tree[::-1]
                        print(tree)

                        for y_adder in range(len(tree)):
                            for x_adder in range(len(tree[2])):
                                try:
                                    current = tree[y_adder][x_adder]
                                    if current != "0":
                                        game_map[tile_y + y_adder][
                                            tile_x - 5 - len(tree[
                                                                 0]) + x_adder] = "18" if current == "1" \
                                            else "17"
                                except IndexError:
                                    # мы вышли за границу карты
                                    pass

    elif dimension == 'nether':
        for tile_y in range(y_max):
            for tile_x in range(x_max):

                if tile_y == 0:
                    block = get_block_data_by_name(blocks_data, 'netherrack')
                    game_map[tile_y][tile_x] = block['numerical_id'] if block is not None else '0'
                elif 1 <= tile_y <= 60:
                    value = random.randint(0, 1000)
                    block_id = 0
                    if 0 <= value <= 924:
                        block_id = get_block_data_by_name(blocks_data, 'netherrack')['numerical_id']
                    elif 925 <= value <= 1000:
                        block_id = ore_generator(tile_y, y_max, dimension='nether')
                    game_map[tile_y][tile_x] = block_id.__str__()
                elif 60 <= tile_y <= 64:
                    block_id = get_block_data_by_name(blocks_data, 'netherrack')['numerical_id']
                    game_map[tile_y][tile_x] = block_id.__str__()
                elif 65 <= tile_y <= 70:
                    # value = random.randint(1, 1000)
                    height = math.floor(noise.pnoise1(tile_x * 0.1, repeat=9999999) * (seed ** 0.5))

                    if tile_y <= (70 + 65) // 2 - height:
                        game_map[tile_y][tile_x] = "87"
                elif 95 <= tile_y <= 128:
                    block_id = get_block_data_by_name(blocks_data, 'netherrack')['numerical_id']
                    game_map[tile_y][tile_x] = block_id.__str__()

    if dimension == 'nether':
        for i in range(6):
            y = 90 + i
            game_map[y] = game_map[65 + (5 - i)][:-1]

    return game_map[::-1]


def ore_generator(y, y_max, dimension='overworld') -> str:
    if dimension == 'overworld':
        possible_blocks = [16]
        if y <= y_max // 2:
            possible_blocks.append(15)
        if y <= y_max // 4:
            possible_blocks.append(14)
            possible_blocks.append(21)
            possible_blocks.append(129)
        if y <= y_max // 8:
            possible_blocks.append(56)
            possible_blocks.append(73)
    elif dimension == 'nether':
        possible_blocks = [153]
    else:
        possible_blocks = [16]
    return str(random.choice(possible_blocks))
