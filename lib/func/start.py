import json
import os.path
import sqlite3

import pygame
from typing import Tuple


def get_worlds(cursor: sqlite3.Cursor, window_size: Tuple[int, int]):
    worlds = cursor.execute("SELECT * FROM worlds").fetchall()
    worlds_rect = list()

    for world in worlds:
        x = window_size[0] // 2 - 210
        y = 200 + 60 * world[0]
        rect = pygame.Rect(x, y, 410, 55)
        worlds_rect.append(rect)
    return worlds, worlds_rect


def check_files_existence(files=None):
    if files is None:
        files = ["lib/storage/worlds_data.json", "lib/storage/nether_worlds_data.json"]
    for file in files:
        exists = os.path.exists(file)

        if not exists:
            if file.endswith(".json"):
                with open(file, "w") as f:
                    json.dump({}, f)
