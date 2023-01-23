import pygame




def Shadows(display, WIDTH, HEIGHT, y):
    if y > 1760 and y < 2016:
        rect = (0, HEIGHT - (y - 1760) // 32 * 32, WIDTH, 288)
        rec = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(rec, pygame.Color(0, 0, 0), rec.get_rect())
        display.blit(rec, rect)