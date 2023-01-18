from lib.models.particles import Particle, Particles


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
        self.charges = list()
        self.map_view_settings = {
            "max_zoom": 4,
            "min_zoom": 1,
            "zoom": 4,
            "max_block_size": 32,
            "camera_x": 500,
            "camera_y": 500,

        }
        self.mouse_pressed = {
            "left": False,
            "middle": False,
            "right": False,
        }
        self.particles = Particles()

    def change_scene(self, screen: str):
        """Changes screen to another. Can't be same as current"""
        if self.screen == screen:
            return
        self.screen = screen

    def set_zoom(self, y):
        zoom = self.map_view_settings.get("zoom", 4)
        zoom += y
        if zoom > 4:
            zoom = 4
        elif zoom < 1:
            zoom = 1
        self.map_view_settings.update({"zoom": zoom})

    def set_map_view_camera(self, x, y):
        self.map_view_settings.update({"camera_x": x})
        self.map_view_settings.update({"camera_y": y})

    def get_map_view_block_size(self) -> int:
        return self.map_view_settings.get("max_block_size", 32) // self.map_view_settings.get("zoom", 1)

    def get_map_view_camera_coord(self):
        return self.map_view_settings.get("camera_x"), self.map_view_settings.get("camera_y")

    def toggle_pause(self):
        self.paused = not self.paused

    def set_world(self, world):
        self.world = world

    def add_charge(self, charge):
        self.charges.append(charge)

    def remove_charges(self, ids: list[int]):
        try:
            for i in ids[::-1]:
                self.charges.pop(i)
        except IndexError:
            print('INVALID INDEX')

    def update_charge(self, index: int, new_value):
        try:
            self.charges[index] = new_value
        except IndexError:
            print('INVALID INDEX')

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
