import pygame


class Button:
    def __init__(self, label: str = "Button Label", width: int = 100, height: int = 20, background_color: str = "black",
                 text_color: str = "white", x: int = 0, y: int = 0, hover_color: str = "gray", id: int = 1
                 ):
        self.label = label
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.is_hovered = False
        self.hover_color = hover_color
        self.id = id

    def render(self, surface, font):
        text_surface = font.render(self.label, False, self.text_color)
        pygame.draw.rect(surface, self.background_color if not self.is_hovered else self.hover_color, self.rect)
        surface.blit(text_surface, (self.rect.midtop[0] - len(self.label) * 3.5, self.rect.midtop[1]))

    def on_mouse_motion(self, x, y):
        rect = pygame.Rect(x, y, 1, 1)
        if self.rect.colliderect(rect):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def on_mouse_click(self, x, y) -> bool:
        rect = pygame.Rect(x, y, 1, 1)
        if self.rect.colliderect(rect):
            return True
        return False
