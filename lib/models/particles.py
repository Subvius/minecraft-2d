import pygame


class Particle:
    def __init__(self, position: tuple[int, int], velocity: tuple[int, int], timer: int,
                 color: tuple[int, int, int] = (255, 255, 255)):
        self.position = position
        self.velocity = velocity
        self.timer = timer
        self.color = color

    def update(self):
        x, y = self.position
        vel_x, vel_y = self.velocity

        x += vel_x
        y += vel_y
        self.position = (x, y)
        self.timer -= 0.1
        self.velocity[1] += 0.1

    def draw(self, screen):
        pos = self.position
        radius = self.timer
        color = self.color

        pygame.draw.circle(screen, color, pos, radius)


class Particles:
    def __init__(self):
        self.particles: list[Particle] = list()

    def update(self, screen: pygame.Surface):
        self.particles = [p for p in self.particles if p.timer > 0.0]

        for particle in self.particles:
            particle.update()
            particle.draw(screen)

    def add_particle(self, pos, vel, timer, color):
        particle = Particle(pos, vel, timer, color)
        self.particles.append(particle)
