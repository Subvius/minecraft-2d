import json


class Settings:
    def __init__(self, path: str):
        self.move_left = "K_a"
        self.move_right = "K_d"
        self.jump = "K_SPACE"
        self.attack = 1
        self.use_item = 3
        self.inventory = "K_e"
        self.drop = "K_q"
        self.toggle_creative_mode = "K_c"
        self.portal_interact = "K_f"
        self.play_music = True
        self.blocks_sound = True
        self.toggle_map = "K_m"
        self.path = path
        self.default = {
            "move_left": "K_a",
            "move_right": "K_d",
            "jump": "K_SPACE",
            "attack": 1,
            "use_item": 3,
            "inventory": "K_e",
            "drop": "K_q",
            "toggle_creative_mode": "K_c",
            "portal_interact": "K_f",
            "toggle_map": "K_m"
        }
        self.load_settings()

    def load_settings(self):
        with open(self.path, "r") as f:
            data: dict = json.load(f)

        self.move_left = data['move_left']
        self.move_right = data['move_right']
        self.jump = data['jump']
        self.attack = data['attack']
        self.use_item = data['use_item']
        self.inventory = data['inventory']
        self.drop = data['drop']
        self.toggle_creative_mode = data['toggle_creative_mode']
        self.portal_interact = data['portal_interact']
        self.play_music = data['music']
        self.blocks_sound = data['blocks']
        self.toggle_map = data["toggle_map"]

    def update_setting(self, setting: str, new_value: any):
        with open(self.path, "r") as f:
            data: dict = json.load(f)

        data.update({setting: new_value})

        with open(self.path, "w") as f:
            json.dump(data, f)

        self.load_settings()

    def convert_to_dict(self) -> dict:
        res = {
            "move_left": self.move_left,
            "move_right": self.move_right,
            "jump": self.jump,
            "attack": self.attack,
            "use_item": self.use_item,
            "inventory": self.inventory,
            "drop": self.drop,
            "toggle_creative_mode": self.toggle_creative_mode,
            "portal_interact": self.portal_interact,
            "toggle_map": self.toggle_map
        }
        return res
