def calculate_breaking_time(hardness, tool_multiplier) -> float:
    return (1.5 * hardness) / tool_multiplier


def get_block_data_by_name(blocks_data: dict, name: str):
    for block in list(blocks_data.items()):
        if block[1]['item_id'] == name:
            return block[1]

    return
