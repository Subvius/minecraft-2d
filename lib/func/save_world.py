import json
from lib.models.player import Player
from lib.models.screen import Screen
import sqlite3
import datetime


def save(game_map: list, player: Player, screen_status: Screen, cursor: sqlite3.Cursor,
         con: sqlite3.Connection, session_stats: dict):
    if screen_status.world is not None:
        seed: int = screen_status.world[1]
        if screen_status.dimension == 'overworld':
            with open("lib/storage/worlds_data.json", "r") as f:
                data_json = json.load(f)

            data_json[str(seed)]["blocks"] = game_map
            data_json[str(seed)]["player_inventory"] = player.inventory
            data_json[str(seed)]["player_hp"] = player.hp
            data_json[str(seed)]["player_exp"] = player.exp
            data_json[str(seed)]['player_coord'] = (player.rect.x, player.rect.y)
            data_json[str(seed)]['world_time'] = screen_status.world_time
            data_json[str(seed)]['dimension'] = 'overworld'

            with open("lib/storage/worlds_data.json", "w") as f:
                json.dump(data_json, f)
        else:
            if screen_status.dimension == 'nether':
                with open("lib/storage/nether_worlds_data.json", "r") as f:
                    data_json = json.load(f)

                data_json[str(seed)]["blocks"] = game_map
                data_json[str(seed)]['player_coord'] = (player.rect.x, player.rect.y)
                with open("lib/storage/nether_worlds_data.json", "w") as f:
                    json.dump(data_json, f)

            with open("lib/storage/worlds_data.json", "r") as f:
                data_json = json.load(f)

            data_json[str(seed)]["player_inventory"] = player.inventory
            data_json[str(seed)]["player_hp"] = player.hp
            data_json[str(seed)]['world_time'] = screen_status.world_time
            data_json[str(seed)]["player_exp"] = player.exp
            data_json[str(seed)]['dimension'] = 'nether'
            with open("lib/storage/worlds_data.json", "w") as f:
                json.dump(data_json, f)
        with open("lib/storage/statistics.json", "r") as f:
            stats: dict = json.load(f)

        data_before: dict = stats.get(seed.__str__(), {})
        keys = list(session_stats.keys())
        for key in keys:
            value_before = data_before.get(key, 0)
            value_after = session_stats.get(key)
            if key == "total_play_time":
                value_after = (datetime.datetime.now() - value_after).seconds
            elif key == 'total_experience_gain':
                value_after = player.exp - value_after
            data_before.update({key: value_before + value_after})
        stats.update({seed.__str__(): data_before})

        with open("lib/storage/statistics.json", "w") as f:
            json.dump(stats, f)
        cursor.execute(
            f"UPDATE worlds SET updatedAt = '{datetime.datetime.now().strftime('%d/%m/%Y, %H:%M')}'"
            f" WHERE seed = {seed}")
        con.commit()
