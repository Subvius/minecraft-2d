import pygame
from math import pi

pygame.init()

size = [600, 600]
screen = pygame.display.set_mode(size)
while True:
    screen.fill((255, 0, 0))

    vertical_line = pygame.Surface((600, 600), pygame.SRCALPHA)
    vertical_line.fill((0, 255, 0, 100)) # You can change the 100 depending on what transparency it is.
    screen.blit(vertical_line, (0, 0))


    pygame.display.flip()

pygame.quit()