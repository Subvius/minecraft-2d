import math

import pygame
from typing import List, Tuple

from lib.models.player import Player


class Arrow:
    def __init__(self, player: Player, trajectory, mouse_pos, force: int = 3, ):
        self.player = player
        self.trajectory = trajectory
        self.force = force
        self.x, self.y = self.player.rect.center
        self.trajectory_point = 0
        self.mouse_pos = mouse_pos
        self.angle = 0

    def move(self):
        if self.trajectory is not None and self.trajectory_point + 1 < len(self.trajectory):
            x, y = self.trajectory[self.trajectory_point]
            if self.trajectory_point + 1 > len(self.trajectory) // 2 + 1:
                self.angle = self.get_angle_for_display(x, y, *self.trajectory[-1]) - 40
            elif self.trajectory_point + 1 <= len(self.trajectory) // 2 + 1:
                self.angle = self.get_angle_for_display(x, y, *self.mouse_pos) - 40

            # angle = get_angle_for_display(rect.x, rect.y, x, y)
            self.x, self.y = x, y
            self.trajectory_point += 3

    @staticmethod
    def get_angle_for_display(x, y, mouse_x, mouse_y) -> float:
        rel_x, rel_y = mouse_x - x, mouse_y - y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        return angle


def get_trajectory(x0, y0, x, y, width, height):
    matrix = pygame.Surface((width, height))
    pygame.draw.line(matrix, "white", (x, y), (x0, y0))
    x1, y1 = x0 + abs(x0 - x) if x0 > x else x0 - abs(x0 - x), y0 + abs(y0 - y)
    pygame.draw.line(matrix, "white", (x0, y0), (x1, y1))
    trajectory_points = []
    reached_top = False
    if x0 > x:
        for cell_x in range(width):
            if reached_top:
                break
            if y0 <= y:
                for cell_y in range(height - 1, -1, -1):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))

                    if (x0, y0) == (cell_x, cell_y):
                        reached_top = True
                        break
            elif y0 > y:
                for cell_y in range(height):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))

                    if (x0, y0) == (cell_x, cell_y):
                        reached_top = True
                        break
        for cell_x in range(x0 % width, width):
            if y1 <= y0:
                for cell_y in range(height - 1, -1, -1):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))
            elif y1 > y0:
                for cell_y in range(height):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))
    elif x0 < x:
        for cell_x in range(width - 1, -1, -1):
            if reached_top:
                break
            if y0 <= y:
                for cell_y in range(height - 1, -1, -1):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))

                    if (x0, y0) == (cell_x, cell_y):
                        reached_top = True
                        break
            elif y0 > y:
                for cell_y in range(height):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))

                    if (x0, y0) == (cell_x, cell_y):
                        reached_top = True
                        break
        for cell_x in range(x0, x1 if x1 >= 0 else 0, -1):
            if y1 <= y0:
                for cell_y in range(height - 1, -1, -1):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))
            elif y1 > y0:
                for cell_y in range(height):
                    res = matrix.get_at((cell_x, cell_y))
                    if res != (0, 0, 0, 0):
                        trajectory_points.append((cell_x, cell_y))
    return trajectory_points
