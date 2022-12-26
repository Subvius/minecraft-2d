import datetime
import math
import random

import noise
import pygame
from lib.models.player import Player
from lib.func.blocks import *


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


def on_left_click(pos, player_rect, map_objects, scroll, game_map, player: Player, hold_start, blocks_data):
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
            if tile != "0":

                block_data = blocks_data[tile]
                breaking_time = calculate_breaking_time(block_data['hardness'], 1)
                now = datetime.datetime.now()
                if now - hold_start >= datetime.timedelta(seconds=breaking_time):
                    game_map[value_y][value_x] = '0'
                    map_objects.remove(pygame.Rect(value_x * 32, value_y * 32, 32, 32))
                    hold_start = now
                else:
                    time_spent = now - hold_start
                    percentage = (time_spent / datetime.timedelta(
                        seconds=breaking_time)) * 100
                    game_map[value_y][value_x] = f"{tile}-{int(percentage)}"
        except IndexError:
            print('доделать!!!!! (lib/models/map.py), line: 26')

    return map_objects, game_map, hold_start


def draw_health_bar(screen, player: Player, width, height, icons):
    inventory = player.inventory
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


def draw_expanded_inventory(screen, inventory, width, height, font, images, blocks_data):
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
    pygame.draw.line(screen, "black", (left + x, top + y), (left + x + 28, top + y))
    pygame.draw.line(screen, "black", (left + x, top + y), (left + x, top + y + 28))
    pygame.draw.line(screen, "white", (left + x, top + y + 28), (left + x + 28, top + y + 28))
    pygame.draw.line(screen, "white", (left + x + 28, top + y), (left + x + 28, top + y + 28))


def generate_chunks(screen, blocks_data, y_max, quantity_of_chunks, seed, dimension):
    x_max = 8 * quantity_of_chunks
    tile_size = 32
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
 1110111
111101111
    0
    0
        """
    ]

    if dimension == 'overworld':
        for tile_y in range(y_max):
            y = tile_y * tile_size
            for tile_x in range(x_max):
                x = tile_x * tile_size

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

                    if tile_y <= (70 + 65) // 2 - height:
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
    elif dimension == 'nether':
        for tile_y in range(y_max):
            y = tile_y * tile_size
            for tile_x in range(x_max):
                x = tile_x * tile_size

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
