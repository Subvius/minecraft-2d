import json
import os

with open("../storage/sounds.json") as f:
    data: dict = json.load(f)

for obj in data.get("objects"):
    start = 'minecraft/sounds/mob/zombie/'
    # if obj[0:len(start)] == start and obj.count("cloth") == 0 and obj.count("scaffold") == 0:
    #     value = data["objects"][obj]
    #     hash_value = value['hash']
    #     folder_name = hash_value[0: 2]
    #     filename = obj.replace(start, "")
    #     os.replace(f"../storage/objects/{folder_name}/{hash_value}", f"../assets/sounds/{filename}")
    if obj[0:len(start)] == start:
        value = data["objects"][obj]
        hash_value = value['hash']
        folder_name = hash_value[0: 2]
        filename = obj.replace(start.replace("zombie/", ""), "")
        filename = filename.replace('/', "_")
        os.replace(f"../storage/objects/{folder_name}/{hash_value}", f"../assets/sounds/{filename}")

"""

    if obj.count('step') > 0:
        print(obj)
"""
