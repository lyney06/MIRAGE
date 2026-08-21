# task_converter.py

import random
from collections import defaultdict
from .utils import pluralize
from .constant import FLAVOR_TO_SEASONINGS, RECIPES
from pdb import set_trace as st

def convert_task_to_text(task):
    lines = []

    for dish in task.get("dishes", []):
        name = dish.get("name", "Unknown Dish")
        flavor = dish.get("flavor", "unspecified flavor")
        servings = dish.get("n_servings", 1)
        serving_str = f"{servings} serving" if servings == 1 else f"{servings} servings"
        seasonings = FLAVOR_TO_SEASONINGS.get(flavor, {})

        # Special naming of sushi + remove duplicate of main protein
        display_name = name
        topping_exclude = set()
        if name == "sushi" and "during_cooking" in seasonings:
            if "chicken" in dish["required_ingredients"]:
                display_name = f"sushi with {flavor} chicken"
                topping_exclude.add("chicken")
            elif "beef" in dish["required_ingredients"]:
                display_name = f"sushi with {flavor} beef"
                topping_exclude.add("beef")
            else:
                display_name = f"sushi ({flavor})"
        else:
            display_name = f"{name} ({flavor})"

        # Collect ingredients (except rice)
        ingredient_state_map = {}  # {ingredient_name: set of state tuples}
        recipe_def = RECIPES[name]  # from original recipe

        for group in ["main_ingredients", "required_ingredients", "optional_ingredients"]:
            for ing, prep_list in dish.get(group, {}).items():
                if ing == "rice":
                    continue
                if ing == "tortilla":
                    continue
                if ing not in ingredient_state_map:
                    ingredient_state_map[ing] = set()

                # possible states of the ingredient in RECIPES
                recipe_group = recipe_def.get(group, {})
                all_possible_preps = recipe_group.get(ing, [])
                for prep in all_possible_preps:
                    states = prep[:-1]  # discard the last number
                    ingredient_state_map[ing].add(tuple(states))

        # remove the protein of sushi (already in topping_exclude)
        for ing in topping_exclude:
            ingredient_state_map.pop(ing, None)

        ingredients = []
        for ing in sorted(ingredient_state_map.keys()):
            state_set = ingredient_state_map[ing]
            # state in current task (only one)
            sampled_states = dish.get("main_ingredients", {}).get(ing) or \
                            dish.get("required_ingredients", {}).get(ing) or \
                            dish.get("optional_ingredients", {}).get(ing)

            sampled_states = sampled_states[0] if sampled_states else ()  # e.g., ('raw', 'chopped')

            if len(state_set) == 1:
                # If the ingredient has only one state_set, return by plural form
                ingredients.append(pluralize(ing))
            else:
                if len(sampled_states) == 1:
                    state_desc = sampled_states[-1]
                else:
                    state_desc = ", ".join(sampled_states[:-1]) + f' and {sampled_states[-1]}'
                ingredients.append(f"{pluralize(ing)} ({state_desc})")

        if not ingredients:
            ing_phrase = ""
        elif len(ingredients) == 1:
            ing_phrase = ingredients[0]
        elif len(ingredients) == 2:
            ing_phrase = f"{ingredients[0]} and {ingredients[1]}"
        else:
            ings = [x for x in ingredients[:-1]]
            ing_phrase = ", ".join(ings) + f", and {ingredients[-1]}"

        # Different description for different dish
        if name == "sushi":
            if ing_phrase:
                line = f"{serving_str} of **{display_name}**, topped with {ing_phrase}."
            else:
                line = f"{serving_str} of **{display_name}**."
        elif name == "fried_rice":
            line = f"{serving_str} of **{display_name}**, mixed with {ing_phrase}."
        elif name == "salad":
            line = f"{serving_str} of **{display_name}**, tossed with {ing_phrase}."
        elif name == "taco":
            line = f"{serving_str} of **{display_name}**, filled with {ing_phrase}."
        elif name == "baked_seafood":
            line = f"{serving_str} of **{display_name}**, baked with {ing_phrase}."
        else:
            line = f"{serving_str} of **{display_name}**, with {ing_phrase}."

        lines.append(line)
        
    for dish in task.get("dishes", []):
        lines.append(describe_dish_raw(dish))

    return "\n".join(lines)


def describe_dish_raw(dish):
    name = dish.get("name").replace('_', ' ')
    flavor = dish.get("flavor", "unspecified flavor")

    # Ingredients
    main_ingredients = dish.get("main_ingredients", {})
    optional_ingredients = dish.get("optional_ingredients", {})
    required_ingredients = dish.get("required_ingredients", {})

    def format_ingredient(ingredient, steps):
        step_str = ' and '.join(steps)
        return f"{step_str} {ingredient}".strip()

    main_list = [format_ingredient(ing, steps[0]) for ing, steps in main_ingredients.items()]
    optional_list = [format_ingredient(ing, steps[0]) for ing, steps in optional_ingredients.items()]
    required_list = [format_ingredient(ing, steps[0]) for ing, steps in required_ingredients.items()]

    # Flavor seasonings
    seasoning_str = ""
    if FLAVOR_TO_SEASONINGS and flavor in FLAVOR_TO_SEASONINGS:
        seasonings = FLAVOR_TO_SEASONINGS[flavor]
        during = seasonings.get("during_cooking", [])
        after = seasonings.get("after_cooking", [])
        parts = []
        if during:
            parts.append("seasoned during cooking with " + ", ".join(during))
        if after:
            parts.append("topped with " + ", ".join(after))
        if parts:
            seasoning_str = " The dish is " + " and ".join(parts) + "."
    # Build description
    desc = f"The desired {name} is a dish made with "
    desc += ', '.join(main_list + optional_list + required_list) + '.'
    desc += seasoning_str
    return desc

def convert_single_dish_to_text(dish):
    # describe_dish_raw(dish)
    name = dish.get("name", "Unknown Dish")
    flavor = dish.get("flavor", "unspecified flavor")
    servings = dish.get("n_servings", 1)
    serving_str = f"{servings} serving" if servings == 1 else f"{servings} servings"
    seasonings = FLAVOR_TO_SEASONINGS.get(flavor, {})

    # special for sushi
    display_name = name
    topping_exclude = set()
    if name == "sushi" and "during_cooking" in seasonings:
        if "chicken" in dish.get("required_ingredients", {}):
            display_name = f"sushi with {flavor} chicken"
            topping_exclude.add("chicken")
        elif "beef" in dish.get("required_ingredients", {}):
            display_name = f"sushi with {flavor} beef"
            topping_exclude.add("beef")
        else:
            display_name = f"sushi ({flavor})"
    else:
        display_name = f"{name} ({flavor})"

    ingredient_state_map = {}
    recipe_def = RECIPES[name]  # from original recipes

    for group in ["main_ingredients", "required_ingredients", "optional_ingredients"]:
        for ing, prep_list in dish.get(group, {}).items():
            if ing in {"rice", "tortilla"}:
                continue
            if ing not in ingredient_state_map:
                ingredient_state_map[ing] = set()
            recipe_group = recipe_def.get(group, {})
            all_possible_preps = recipe_group.get(ing, [])
            for prep in all_possible_preps:
                states = prep[:-1]
                ingredient_state_map[ing].add(tuple(states))

    for ing in topping_exclude:
        ingredient_state_map.pop(ing, None)

    ingredients = []
    for ing in sorted(ingredient_state_map.keys()):
        state_set = ingredient_state_map[ing]
        sampled_states = dish.get("main_ingredients", {}).get(ing) or \
                         dish.get("required_ingredients", {}).get(ing) or \
                         dish.get("optional_ingredients", {}).get(ing)

        sampled_states = sampled_states[0] if sampled_states else ()

        if len(state_set) == 1:
            ingredients.append(pluralize(ing))
        else:
            if sampled_states:
                state_desc = ", ".join(sampled_states[:-1]) + f' and {sampled_states[-1]}' if len(sampled_states) > 1 else sampled_states[0]
                ingredients.append(f"{pluralize(ing)} ({state_desc})")
            else:
                ingredients.append(pluralize(ing))

    # ingredient phrase
    if not ingredients:
        ing_phrase = ""
    elif len(ingredients) == 1:
        ing_phrase = ingredients[0]
    elif len(ingredients) == 2:
        ing_phrase = f"{ingredients[0]} and {ingredients[1]}"
    else:
        ings = [x for x in ingredients[:-1]]
        ing_phrase = ", ".join(ings) + f", and {ingredients[-1]}"

    if name == "sushi":
        if ing_phrase:
            line = f"{serving_str} of **{display_name}**, topped with {ing_phrase}."
        else:
            line = f"{serving_str} of **{display_name}**."
    elif name == "fried_rice":
        line = f"{serving_str} of **{display_name}**, mixed with {ing_phrase}."
    elif name == "salad":
        line = f"{serving_str} of **{display_name}**, tossed with {ing_phrase}."
    elif name == "taco":
        line = f"{serving_str} of **{display_name}**, filled with {ing_phrase}."
    elif name == "baked_seafood":
        line = f"{serving_str} of **{display_name}**, baked with {ing_phrase}."
    else:
        line = f"{serving_str} of **{display_name}**, with {ing_phrase}."

    return line