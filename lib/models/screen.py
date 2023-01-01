class Screen:
    def __init__(self, start_screen: str = "main", paused: bool = True):
        self.screen = start_screen
        self.paused = paused
        self.world = None
        self.show_inventory = False
        self.dimension = "overworld"
        self.mouse_pos = (0, 0)
        self.world_time = 0

    def change_scene(self, screen: str):
        """Changes screen to another. Can't be same as current"""
        if self.screen == screen:
            return
        self.screen = screen

    def toggle_pause(self):
        self.paused = not self.paused

    def set_world(self, world):
        self.world = world

    def toggle_inventory(self):
        self.show_inventory = not self.show_inventory

    def change_dimension(self, dimension):
        self.dimension = dimension

    def set_mouse_pos(self, pos):
        self.mouse_pos = pos

    def reset_world_time(self):
        self.world_time = 0

    def set_world_time(self, ticks: int):
        self.world_time = ticks

    def update_world_time(self):
        self.world_time += 1
        if self.world_time > 48_000:
            self.reset_world_time()
