class Screen:
    def __init__(self, start_screen: str = "main", paused: bool = True):
        self.screen = start_screen
        self.paused = paused
        self.world = None
        self.show_inventory = False
        self.inventories = {
            "crafting_table": False,
            "furnace": False,
        }
        self.dimension = "overworld"
        self.mouse_pos = (0, 0)
        self.world_time = 0
        self.creative_inventory_scroll = 0
        self.creative_inventory_text_field_text = ""

    def change_scene(self, screen: str):
        """Changes screen to another. Can't be same as current"""
        if self.screen == screen:
            return
        self.screen = screen

    def toggle_pause(self):
        self.paused = not self.paused

    def set_world(self, world):
        self.world = world

    def toggle_inventory(self, inventory=None):
        if inventory is None:
            toggled = False
            for inv in self.inventories:
                if self.inventories[inv]:
                    self.inventories[inv] = not self.inventories[inv]
                    toggled = True
                    break
            if not toggled:
                self.show_inventory = not self.show_inventory
        else:
            try:
                self.inventories[inventory] = not self.inventories[inventory]
            except KeyError:
                print('INVALID INVENTORY NAME -' + inventory)
        self.toggle_pause()
        self.update_creative_text("")

    def change_dimension(self, dimension):
        self.dimension = dimension

    def set_mouse_pos(self, pos):
        self.mouse_pos = pos

    def update_creative_scroll(self, momentum: int, blocks_data: dict):
        self.creative_inventory_scroll += momentum
        if self.creative_inventory_scroll < 0:
            self.creative_inventory_scroll = 0
        elif self.creative_inventory_scroll > len(list(blocks_data.keys())) // 9:
            self.creative_inventory_scroll = len(list(blocks_data.keys())) // 9

    def update_creative_text(self, text: str):
        self.creative_inventory_text_field_text = text

    def reset_world_time(self):
        self.world_time = 0

    def set_world_time(self, ticks: int):
        self.world_time = ticks

    def update_world_time(self):
        self.world_time += 1
        if self.world_time > 48_000:
            self.reset_world_time()
