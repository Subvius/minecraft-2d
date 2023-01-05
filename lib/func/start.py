import sqlite3

import pygame


def get_worlds(cursor: sqlite3.Cursor, window_size: tuple[int, int]):
    worlds = cursor.execute("SELECT * FROM worlds").fetchall()
    worlds_rect = list()

    for world in worlds:
        x = window_size[0] // 2 - 210
        y = 200 + 60 * world[0]
        rect = pygame.Rect(x, y, 410, 55)
        worlds_rect.append(rect)
    return worlds, worlds_rect
