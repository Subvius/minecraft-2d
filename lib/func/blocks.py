from lib.models.player import Player


def calculate_breaking_time(block, player: Player) -> float:
    tool_multiplier = 1
    hardness = block['hardness']
    # Предмет в руке
    item = player.inventory[0][player.selected_inventory_slot]
    can_harvest = True

    tools_constant_multiplier = {
        "wooden": 2,
        'stone': 4,
        "iron": 6,
        "diamond": 8,
        "netherite": 9,
        "golden": 12,
        "sword": 1.5
    }

    if item is not None:
        block_type = block['material']
        if item.get("best_for", "") == block_type:
            tool_multiplier = tools_constant_multiplier.get(item.get("item_id", "_").split("_")[0], 1)

            if item.get("enchantments", {}).get("efficiency", None) is not None:
                tool_multiplier += item.get("enchantments", {}).get("efficiency", None) ** 2 + 1
        else:
            can_harvest = False

    return ((1.5 if can_harvest else 5) * hardness) / tool_multiplier


def get_block_data_by_name(blocks_data: dict, name: str):
    for block in list(blocks_data.items()):
        if block[1]['item_id'] == name:
            return block[1]

    return


def get_block_from_coords(y: int, x: int, game_map: list) -> dict:
    try:
        data = game_map[y][x]
    except IndexError:
        print("INDEX ERROR CAUSED BY WRONG BLOCK COORD")
        return {}
    return data
