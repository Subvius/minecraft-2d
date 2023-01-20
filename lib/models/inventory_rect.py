import random

import pygame

from lib.func.blocks import get_block_data_by_name


class InventoryRect:
    def __init__(self, rect: pygame.Rect, row, col, inv_type):
        self.rect = rect
        self.high_lighted = False
        self.row, self.col = row, col
        self.inventory_type = inv_type

    def check_collide(self, pos):
        return self.rect.collidepoint(*pos)

    def toggle_high_light(self, val):
        self.high_lighted = val

    def get_value(self, types: dict, blocks_data):
        slots = types.get(self.inventory_type, None)
        item = None
        block = None
        if self.inventory_type not in ["craft_result", "blocks_to_show"]:
            item = slots[self.row][self.col]
        elif self.inventory_type == 'blocks_to_show':
            index = self.row * 9 + self.col % 9
            index += types.get("scroll")
            if index < len(slots.keys()):
                key = list(slots.keys())[index]
                item = slots[key]
        else:
            if slots is not None:
                block = get_block_data_by_name(blocks_data, slots['result']['item'])
                if block is not None:
                    item = {
                        'item_id': block['item_id'],
                        'numerical_id': block['numerical_id'],
                        'quantity': slots['result'].get("count", 1)
                    }

        index = list(types.keys()).index(self.inventory_type)
        if item is not None:
            block = get_block_data_by_name(blocks_data, item['item_id'])
            item['type'] = 'block' if block.get("material",
                                                None) is not None else "tool" if block.get(
                "best_for", None) is not None else "item"
            item['best_for'] = block.get("best_for")
            item['damage'] = block.get("damage")

        return item, index, block

    def __eq__(self, other):
        return self.rect.x == other.rect.x and self.rect.y == other.rect.y and self.row == other.row \
               and self.col == other.col and self.inventory_type == other.inventory_type
