def check_if_can_craft(four_slots: bool, slots: list, recipes: dict):
    # convert slots array to more "sortable" view
    a_slots = ["" for _ in range(2 if four_slots else 3)]
    rows_to_pop = []
    for row in range(len(slots)):
        r_value = slots[row]
        for value in r_value:
            a_slots[row] += " " if value is None else value['item_id']
        a_slots[row] = a_slots[row].replace(" ", "")
        if a_slots[row] == "":
            rows_to_pop.append(row)

    for row in rows_to_pop:
        try:
            a_slots.pop(row)
        except IndexError:
            pass

    for value in recipes:
        pattern = recipes[value].get("pattern", None)
        ingredients = recipes[value].get("ingredients", None)
        if pattern is not None:
            for kk in recipes[value]['key']:
                if type(recipes[value]['key'][kk]) == dict:
                    try:
                        if recipes[value]['key'][kk].get('item', None) is not None:
                            for row in range(len(pattern)):
                                pattern[row] = pattern[row].replace(kk, recipes[value]['key'][kk]['item'])
                    except AttributeError:
                        print(value)

            if pattern == a_slots:
                print('exists', value)
                return True, value
        elif ingredients is not None:
            if recipes[value].get("ingredients", [])[0].get("tag", None) is not None:
                ingredients = [el.get("tag", "").rstrip("s")
                               for el in recipes[value].get("ingredients", [])]
            else:
                try:
                    ingredients = [el.get("item", "") for el in recipes[value].get("ingredients", [])]
                except AttributeError:
                    print("\ncrafts.py(line - 43)\nAttributeError: 'list' object has no attribute 'get'\n")
            if a_slots[0] in ingredients:
                print('exists', value)
                return True, value, recipes[value]

    return [False]
