def check_if_can_craft(four_slots: bool, slots: list, recipes: dict):
    # convert slots array to more "sortable" view
    size = 2 if four_slots else 3
    i_slots = ["" for _ in range(2 if four_slots else 3)]
    p_slots = [['' for _ in range(2 if four_slots else 3)] for _ in range(2 if four_slots else 3)]
    rows_to_pop = []
    for row in range(len(slots)):
        r_value = slots[row]
        for value_i in range(len(r_value)):
            value = r_value[value_i]
            item: str = value['item_id'] if value is not None else " "
            if item.endswith("planks"):
                item = item.split("_")[1]
            i_slots[row] += " " if value is None else item
            p_slots[row][value_i] = item if item != " " else None
        i_slots[row] = i_slots[row].replace(" ", "")
        if i_slots[row] == "":
            rows_to_pop.append(row)
    for row in rows_to_pop[::-1]:
        try:
            i_slots.pop(row)
        except IndexError:
            pass
    if not i_slots:
        return [False]
    empty_slots = dict()
    to_pop = []
    for row_i in range(len(p_slots)):
        row = p_slots[row_i]
        for value_id in range(len(row)):
            value = row[value_id]
            if value is None:
                empty_slots.update({value_id: empty_slots.get(value_id, 0) + 1})
        if row == [None for _ in range(size)]:
            to_pop.append(row_i)

    for index in to_pop[::-1]:
        p_slots.pop(index)

    for element in sorted(empty_slots, reverse=True):
        if empty_slots[element] == size:
            for row_i in range(len(p_slots)):
                row = p_slots[row_i]
                for value_id in range(len(row)):
                    if element == value_id:
                        row.pop(value_id)

                p_slots[row_i] = row

    for row_i in range(len(p_slots)):
        row = p_slots[row_i]
        for value_id in range(len(row)):
            value = row[value_id]
            row[value_id] = value if value is not None else " "
        row = "".join(row)
        p_slots[row_i] = row
    print(p_slots)
    for value in recipes:
        pattern = recipes[value].get("pattern", None)
        ingredients = recipes[value].get("ingredients", None)
        if pattern is not None:
            for kk in recipes[value]['key']:
                if type(recipes[value]['key'][kk]) == dict:
                    try:
                        if recipes[value]['key'][kk].get('item', None) is not None:
                            for row in range(len(pattern)):
                                new_value = recipes[value]['key'][kk]['item']
                                if new_value.endswith("planks"):
                                    new_value = new_value.split("_")[1]
                                pattern[row] = pattern[row].replace(kk, new_value)
                        elif recipes[value]['key'][kk].get('tag', None) is not None:
                            for row in range(len(pattern)):
                                pattern[row] = pattern[row].replace(kk, recipes[value]['key'][kk]['tag'])
                    except AttributeError:
                        print(value)
            if value == 'acacia_boat':
                print(pattern)
            if pattern == p_slots:
                print('exists', value)
                return True, value, recipes[value]
        elif ingredients is not None:
            if recipes[value].get("ingredients", [])[0].get("tag", None) is not None:
                ingredients = [el.get("tag", "").rstrip("s")
                               for el in recipes[value].get("ingredients", [])]
            else:
                try:
                    ingredients = [el.get("item", "") if not el.get("item", "").endswith("planks") else
                                   el.get("item", "").split("_")[1] for el in recipes[value].get("ingredients", [])]
                except AttributeError:
                    print("\ncrafts.py(line - 43)\nAttributeError: 'list' object has no attribute 'get'\n")
            if i_slots[0] in ingredients and len(i_slots) == 1:
                print('exists', value)
                return True, value, recipes[value]

    return [False]
