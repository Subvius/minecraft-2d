import pygame


def draw_text(screen: pygame.Surface, font: pygame.font.Font, text: str, color,
              pos: tuple[int, int], has_shadow: bool, shadow_color=(0, 0, 0)):
    if has_shadow:
        shadowed_text = font.render(text, False, shadow_color)
        screen.blit(shadowed_text, (pos[0] + font.get_height() * 0.085, pos[1] + font.get_height() * 0.085))

    text_surface = font.render(text, False, color)
    screen.blit(text_surface, pos)
