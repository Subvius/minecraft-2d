import json
import os

data = dict()

for file in os.listdir("../storage/recipes/"):
    with open(f"../storage/recipes/{file}", "r") as f:
        json_data: dict = json.load(f)
    json_str = json.dumps(json_data)
    json_str = json_str.replace("minecraft:", "")
    json_data = json.loads(json_str)
    data.update({file.split(".")[0]: json_data})

with open("../storage/recipes.json", "w") as f:
    json.dump(data, f)
