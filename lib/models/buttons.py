import pygame

from lib.models.settings import Settings


class Button:
    def __init__(self, label: str = "Button Label", width: int = 100, height: int = 20, background_color: str = "black",
                 text_color: str = "white", x: int = 0, y: int = 0, hover_color: str = "gray", uniq_id: int = 1
                 ):
        self.label = label
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.is_hovered = False
        self.hover_color = hover_color
        self.id = uniq_id
        self.high_lighted = False

    def render(self, surface, font):
        text_surface = font.render(self.label, False, self.text_color)
        pygame.draw.rect(surface, self.background_color if not self.is_hovered else self.hover_color, self.rect)
        if self.high_lighted:
            pygame.draw.rect(surface, (10, 10, 225), self.rect, width=2)

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

    def toggle_high_light(self):
        self.high_lighted = not self.high_lighted


def set_controls_buttons(settings: Settings, window_size: tuple[int, int]) -> list[Button]:
    buttons = [
        Button(label="Done", width=200, height=25, background_color="gray", text_color="white",
               x=window_size[0] // 2 - 210, y=int(window_size[1] // 1.075), hover_color="lightgray", uniq_id=9
               ),
        Button(label="Reset Keys", width=200, height=25, background_color="gray", text_color="white",
               x=window_size[0] // 2, y=int(window_size[1] // 1.075), hover_color="lightgray", uniq_id=10),
    ]
    values = settings.convert_to_dict()
    default_keys = list(values.keys())
    for i in range(9):
        y = 30 * i
        key = default_keys[i]
        value = values.get(key)
        if type(value) == int:
            text = f'Button {value}'
        else:
            text = value.replace("K_", "").upper()
        buttons.append(Button(label=text, width=100, height=25, background_color="gray", text_color="white",
                              x=window_size[0] // 2 + 75, y=100 - 15 + y, hover_color="lightgray",
                              uniq_id=i), )

    return buttons
