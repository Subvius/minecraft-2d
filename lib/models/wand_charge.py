import math
import os

import pygame


class Charge:
    def __init__(self, wand_type: str, image_name: str, launch_pos: tuple[int, int], mouse_pos: tuple[int, int],
                 force: int = 3, damage: int = 1, width: int = 1184, height: int = 768, fly_distance: int = 32 * 5):
        self.image_name = image_name
        self.launch_pos = launch_pos
        self.mouse_pos = mouse_pos
        self.force = force
        self.fly_distance = fly_distance

        self.frame = 1
        self.wand_type = wand_type
        self.max_frames, self.images = self.get_max_frames()
        self.damage = damage
        self.trajectory_point = 0
        self.width, self.height = width, height
        self.rect: pygame.Rect = pygame.Rect(self.launch_pos[0], self.launch_pos[1], 24, 24)
        self.angle = 0
        self.trajectory = self.get_trajectory()
        self.last_update = pygame.time.get_ticks()
        self.update_delay = 100

    def get_max_frames(self):
        try:
            path = f"lib/assets/animations/weapons/{self.wand_type}_charges"
            files = os.listdir(path)
            images = list()
            frames = 0
            for file in files:
                if file.endswith(".png"):
                    frames += 1
                    images.append(pygame.image.load(f"{path}/{file}"))
        except FileNotFoundError:
            return 0, []
        return frames, images

    @staticmethod
    def get_angle_for_display(x, y, x1, y1) -> float:
        rel_x, rel_y = x1 - x, y1 - y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        return angle

    def render(self, screen: pygame.Surface):
        image = self.images[self.frame]
        screen.blit(
            pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(image, (24, 24)), self.angle), True,
                                  True),
            (self.rect.x, self.rect.y))
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.update_delay:
            self.frame = (self.frame + 1) % len(self.images)
            self.last_update = current_time

    def move(self) -> bool:
        if self.trajectory is not None and self.trajectory_point < len(self.trajectory):
            x, y = self.trajectory[self.trajectory_point]
            if self.trajectory_point + 1 > len(self.trajectory) // 2 + 1:
                self.angle = self.get_angle_for_display(x, y, *self.trajectory[-1])
            elif self.trajectory_point + 1 <= len(self.trajectory) // 2 + 1:
                self.angle = self.get_angle_for_display(x, y, *self.mouse_pos)

            # angle = get_angle_for_display(rect.x, rect.y, x, y)
            self.rect.x, self.rect.y = x, y

            self.trajectory_point += self.force
            return False
        else:
            return True

    def get_trajectory(self) -> list[list[int, int]]:
        x, y = self.launch_pos
        x0, y0 = self.mouse_pos
        matrix = pygame.Surface((self.width, self.height))
        pygame.draw.line(matrix, "white", (x, y),
                         (x0 if abs(
                             x - x0) <= self.fly_distance else x - self.fly_distance if x > x0 else (
                                 x + self.fly_distance),
                          y0 if abs(
                              y - y0) <= self.fly_distance else y - self.fly_distance if y > y0 else (
                                  y + self.fly_distance)))
        trajectory_points = []
        reached_top = False
        if x0 > x:
            for cell_x in range(self.width):
                if reached_top:
                    break
                if y0 <= y:
                    for cell_y in range(self.height - 1, -1, -1):
                        res = matrix.get_at((cell_x, cell_y))
                        if res != (0, 0, 0, 0):
                            trajectory_points.append((cell_x, cell_y))

                        if (x0, y0) == (cell_x, cell_y):
                            reached_top = True
                            break
                elif y0 > y:
                    for cell_y in range(self.height):
                        res = matrix.get_at((cell_x, cell_y))
                        if res != (0, 0, 0, 0):
                            trajectory_points.append((cell_x, cell_y))

                        if (x0, y0) == (cell_x, cell_y):
                            reached_top = True
                            break
        elif x0 < x:
            for cell_x in range(self.width - 1, -1, -1):
                if reached_top:
                    break
                if y0 <= y:
                    for cell_y in range(self.height - 1, -1, -1):
                        res = matrix.get_at((cell_x, cell_y))
                        if res != (0, 0, 0, 0):
                            trajectory_points.append((cell_x, cell_y))

                        if (x0, y0) == (cell_x, cell_y):
                            reached_top = True
                            break
                elif y0 > y:
                    for cell_y in range(self.height):
                        res = matrix.get_at((cell_x, cell_y))
                        if res != (0, 0, 0, 0):
                            trajectory_points.append((cell_x, cell_y))

                        if (x0, y0) == (cell_x, cell_y):
                            reached_top = True
        return trajectory_points
