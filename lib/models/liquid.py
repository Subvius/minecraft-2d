import pygame

Point = pygame.Vector2

screen_width = 1200
screen_height = 720


class WaterSpring:
    def __init__(self, x=0, target_height=None):
        if not target_height:
            self.target_height = screen_height // 2 + 150
        else:
            self.target_height = target_height
        self.height = self.target_height
        self.vel = 0
        self.x = x

    def update(self):
        height = self.target_height - self.height
        if abs(height) < 0.01:
            self.height = self.target_height
        self.vel += 0.01 * height - self.vel * 0.05
        self.height += self.vel

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, 'white', (self.x, self.height), 1)


class Wave:
    def __init__(self, width, height, x, y):
        diff = 16
        self.springs = [WaterSpring(x=i * diff + 0, target_height=height) for i in range(width // diff + 1)]
        self.points = []
        self.diff = diff
        self.position = (x, y)
        self.width, self.height = width, height

    def get_spring_index_for_x_pos(self, x, scroll_x=0):
        return int((x - (self.position[0] - scroll_x)) // self.diff)

    def __eq__(self, other):
        return self.position == other.position and self.width == other.width and self.height == other.height

    def update(self, scroll: list[int, int]):
        for i in self.springs:
            i.update()
        self.spread_wave()
        self.points = [Point(i.x + (self.position[0] - scroll[0]), i.height + (self.position[1] - scroll[1])) for i in
                       self.springs]
        self.points.extend([Point(screen_width, screen_height), Point(0, screen_height)])

    #
    # def draw(self, surf: pygame.Surface):
    #     pygame.draw.polygon(surf, (0, 0, 255, 50), self.points)

    def draw_line(self, surf: pygame.Surface):
        pygame.draw.lines(surf, 'white', False, self.points[:-2], 1)

    def spread_wave(self):
        spread = 0.05
        for i in range(len(self.springs)):
            if i > 0:
                self.springs[i - 1].vel += spread * (self.springs[i].height - self.springs[i - 1].height)
            try:
                self.springs[i + 1].vel += spread * (self.springs[i].height - self.springs[i + 1].height)
            except IndexError:
                pass

    def splash(self, index, vel):
        try:
            self.springs[index].vel += vel
        except IndexError:
            pass
