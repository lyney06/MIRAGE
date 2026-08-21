from copy import deepcopy
from collections import defaultdict
from .constant import *
from .utils import pluralize
from .recipe_utils import generate_inconsistent_recipe
from pdb import set_trace as st

TOOL_PREPOSITIONS = {
    "oven": "in",
    "deep_fryer": "in",
    "pot": "in",
    "steamer": "in",
    "pan": "on",
    "electric grill": "on",
    "dish": "on",
    "cutting_board": "with",  # should not happen in seasoning context
}


def change_state(ingredient_states, name, method):
    if name not in ingredient_states:
        ingredient_states[name] = ['raw']

    if method == 'chopped':
        ingredient_states[name].append(method)
    elif 'raw' in ingredient_states[name]:
        ingredient_states[name] = [s if s != 'raw' else method for s in ingredient_states[name]]
    elif method not in ingredient_states[name]:
        ingredient_states[name].append(method)
    return

def describe_ingredient_states(dish):
    description = []
    
    def describe_category(category_name, ingredients):
        lines = []
        for ing, states in ingredients.items():
            for state in states:
                if len(state) == 1:
                    lines.append(f"{ing} is {state[0]}")
                else:
                    joined_states = " and ".join(state)
                    lines.append(f"{ing} is {joined_states}")
                    
        return f"\n".join(f"- {line}" for line in lines)

    main_text = describe_category("main ingredients", dish.get("main_ingredients", {}))
    required_text = describe_category("required ingredients", dish.get("required_ingredients", {}))
    optional_text = describe_category("optional ingredients", dish.get("optional_ingredients", {}))
    
    for part in [main_text, required_text, optional_text]:
        if part:
            description.append(part)
            
    seasonings = FLAVOR_TO_SEASONINGS.get(dish["flavor"], {})
    during = seasonings.get("during_cooking", [])
    after = seasonings.get("after_cooking", [])
    if during:
        description.append('The seasonings should be added during cooking.')
    elif after:
        description.append('The seasonings should be put to the plate after cooking.')
    
    return "\n".join(description)


def process_tool(tool_usage, used_tool, name):
    if not used_tool:
        return
    
    for tool in list(tool_usage.keys()):
        tool_usage[tool] = [x for x in tool_usage[tool] if x != name]
        if not tool_usage[tool]:
            del tool_usage[tool]

    if used_tool in tool_usage:
        tool_usage[used_tool].append(name)
    else:
        tool_usage[used_tool] = [name]

def get_raw_only_ingredients(ingredients, kitchen):
    """
    Returns:
        - List of ingredient names whose prep states are only 'raw'
        - String like "fridge" or "fridge and cabinet" showing all unique locations
        - Detailed string like "lettuce and spinach from fridge, croutons from cabinet"
    """
    raw_only_ings = []
    ing_to_loc = {}  # {loc: [ing1, ing2, ...]}
    storage_locations = set()

    for ing_name, prep_list in ingredients.items():
        if all(len(prep) == 1 and prep[0] == "raw" for prep in prep_list):
            raw_only_ings.append(ing_name)
            full_name = f"raw {ing_name}"

            # Determine location
            if full_name in kitchen.fridge_ingredients:
                loc = "fridge"
            elif full_name in kitchen.cabinet_ingredients:
                loc = "cabinet"
            else:
                # Fallback guess if not currently in fridge/cabinet
                if ing_name in PLANTABLE_INGREDIENTS + FISHABLE_INGREDIENTS + ADDITIONAL_SEAFOOD + MEATS:
                    loc = "fridge"
                elif ing_name in BASE_SEASONINGS + CABINET_INGREDIENTS + SPECIAL_SEASONINGS:
                    loc = "cabinet"
                else:
                    loc = "fridge"

            ing_to_loc.setdefault(loc, []).append(ing_name)
            storage_locations.add(loc)

    # Build location string (like "fridge" or "fridge and cabinet")
    locs = sorted(storage_locations)
    if len(locs) == 0:
        # no raw only ingredients
        return raw_only_ings, '', ''
    
    if len(locs) == 1:
        loc_string = locs[0]
    elif len(locs) == 2:
        loc_string = f"{locs[0]} and {locs[1]}"
    else:
        loc_string = ", ".join(locs[:-1]) + f", and {locs[-1]}"


    parts = []
    for loc in sorted(ing_to_loc.keys()):
        items = sorted(ing_to_loc[loc])
        raw_items = [f"raw {item}" for item in items]
        
        if len(raw_items) == 1:
            part = f"{raw_items[0]} from {loc}"
        elif len(raw_items) == 2:
            part = f"{raw_items[0]} and {raw_items[1]} from {loc}"
        else:
            part = f"{', '.join(raw_items[:-1])}, and {raw_items[-1]} from {loc}"
        
        parts.append(part)

    detail_string = ", ".join(parts)

    return raw_only_ings, loc_string, detail_string


def describe_action(actions, all_ingredients, seasonings, kitchen):
    step_text_lines = []
    tool_usage = {}

    all_raw, locs, _ = get_raw_only_ingredients(all_ingredients, kitchen)

    for action in actions:
        step_texts = []
        for entry in action:
            if entry[0] == "seasonings":
                when, where = entry[1], entry[2]
                season_list = seasonings.get(when, [])
                if season_list:
                    joined = ", ".join([pluralize(x) for x in season_list])
                    preposition = TOOL_PREPOSITIONS.get(where, "on")
                    if when == 'during_cooking':
                        assert where in ['pan', 'oven']
                        step_texts.append(f"add {joined} {preposition} the {where}")
                    else:
                        step_texts.append(f"finally, add {joined} {preposition} top of the {where}")
                    # seasoning can also appear in tool_usage (optional)
                    # not counted as tool_usage here, since it's only seasoning rather than ingredient
            elif entry[0] == "ingredient":
                method = entry[1]
                if method == "assembled":
                    if tool_usage:
                        tools_str = ", ".join(['cutting board' if x in ('knife', 'cutting_board') else x for x in sorted(tool_usage)])
                        if all_raw:
                            step_text_lines.append(f"wait for all ingredients to finish cooking, then assemble all the ingredients from the {tools_str}, along with the required raw ingredients, onto the same plate.")
                        else:
                            step_text_lines.append(f"wait for all ingredients to finish cooking, then assemble all the ingredients from the {tools_str} onto the same plate.")
                    else:
                        assert locs
                        step_text_lines.append(f"assemble all the raw ingredients onto the plate.")
                else:
                    targets = [pluralize(ing) for ing, state in all_ingredients.items() if method in state[0]]
                    for ing in targets:
                        tool = METHOD_TO_TOOL.get(STATE_TO_METHOD[method])
                        process_tool(tool_usage, tool, ing)
                    if targets:
                        joined = ", ".join(targets)
                        step_texts.append(f"{STATE_TO_METHOD[method]} the {joined}")
            else:
                name, method = entry
                if name in all_ingredients:
                    step_texts.append(f"{STATE_TO_METHOD[method]} the {pluralize(name)}")
                    tool = METHOD_TO_TOOL.get(STATE_TO_METHOD[method])
                    process_tool(tool_usage, tool, name)

        if step_texts:
            step_text_lines.append("; then ".join(step_texts) + '.')

    return step_text_lines


def describe_detailed_action(actions, all_ingredients, seasonings, kitchen):
    # manual_type == 2
    step_text_lines = []
    ingredient_states = {}
    tool_usage = {}

    for action in actions:
        step_texts = []
        for entry in action:
            if entry[0] == "seasonings":
                when, where = entry[1], entry[2]
                season_list = seasonings.get(when, [])
                if season_list:
                    joined = ", ".join([pluralize(x) for x in season_list])
                    preposition = TOOL_PREPOSITIONS.get(where, "on")
                    if when == 'during_cooking':
                        step_texts.append(f"add {joined} {preposition} the {where}")
                    else:
                        step_texts.append(f"finally, add {joined} {preposition} top of the {where}")
            elif entry[0] == "ingredient":
                method = entry[1]
                if method == "assembled":
                    # along with the raw ones from the kitchen, 
                    all_raw, locs, raw_loc_str = get_raw_only_ingredients(all_ingredients, kitchen)

                    if tool_usage:
                        tools_str = ", ".join(['cutting board' if x in ('knife', 'cutting_board') else x for x in sorted(tool_usage)])
                        all_states = set(state for prep in all_ingredients.values() for combo in prep for state in combo)
                        if all_states.issubset({'raw', 'chopped'}):
                            if raw_loc_str:
                                step_text_lines.append(f"assemble all the ingredients from the {tools_str}, along with the {raw_loc_str}, onto the same plate.")
                            else:
                                step_text_lines.append(f"assemble all the ingredients from the {tools_str} onto the same plate.")
                        elif all_raw:
                            if raw_loc_str:
                                step_text_lines.append(f"wait for all ingredients to finish cooking, then assemble all the ingredients from the {tools_str}, along with the {raw_loc_str}, onto the same plate.")
                            else:
                                step_text_lines.append(f"wait for all ingredients to finish cooking, then assemble all the ingredients from the {tools_str}, along with the required raw ingredients, onto the same plate.")
                        else:
                            step_text_lines.append(f"wait for all ingredients to finish cooking, then assemble all the ingredients from the {tools_str} onto the same plate.")
                    else:
                        assert locs
                        step_text_lines.append(f"assemble all the raw ingredients - {raw_loc_str} onto the plate.")
                targets = []
                for ing, state in all_ingredients.items():
                    if method in state[0]:
                        if ing in ingredient_states:
                            full_name = f"{', '.join(ingredient_states[ing])} {ing}"
                        else:
                            full_name = f"raw {ing}"
                        change_state(ingredient_states, ing, method)
                        targets.append(full_name)
                        used_tool = METHOD_TO_TOOL.get(STATE_TO_METHOD[method])
                        process_tool(tool_usage, used_tool, ing)
                if targets:
                    targets_plural = [pluralize(t) for t in targets]
                    joined = ", ".join(targets_plural)
                    step_texts.append(f"{STATE_TO_METHOD[method]} the {joined}")
            else:
                name, method = entry
                if name in ingredient_states:
                    full_name = f"{', '.join(ingredient_states[name])} {name}"
                else:
                    full_name = f"raw {name}"
                if name in all_ingredients:
                    step_texts.append(f"{STATE_TO_METHOD[method]} the {pluralize(full_name)}")
                change_state(ingredient_states, name, method)
                used_tool = METHOD_TO_TOOL.get(STATE_TO_METHOD[method])
                process_tool(tool_usage, used_tool, name)
                
        if step_texts:
            step_text_lines.append("; then ".join(step_texts) + '.')
    
    return step_text_lines


def get_multi_step_ingredients(task):
    # This is for manual_type 3, it's not used yet
    """
    Identify ingredients that go through 2 or more state transitions.
    
    Returns:
        - multi_step_ings: dict of ingredient -> [state1, state2, ...]
        - first_steps: list of (ingredient, first_state) tuples that can be omitted
    """
    multi_step_ings = {}
    first_steps = []

    for dish in task["dishes"]:
        for group in ["main_ingredients", "required_ingredients", "optional_ingredients"]:
            ingredients = dish.get(group, {})
            for ing_name, prep_list in ingredients.items():
                for prep in prep_list:
                    prep = [x for x in prep if not (x.endswith(' g') or x.endswith('count') or x=='raw')]
                    if len(prep) >= 2:
                        # print(prep_list)
                        state_seq = list(prep)
                        multi_step_ings[ing_name] = state_seq
                        first_steps.append((ing_name, state_seq[0]))

    return multi_step_ings, first_steps



def get_ingredients(dish,
                    recipe_texts=None):
    if recipe_texts is None:
        recipe_texts = []
    # Gather ingredients
    all_ings = list(dish["main_ingredients"].keys()) + \
                list(dish["required_ingredients"].keys()) + \
                list(dish["optional_ingredients"].keys())
    
    if all_ings:
        recipe_texts.append("### Ingredients:")
        ings_with_amount = [f"{pluralize(x)} x 1 serving" if x in SEASONINGS or x in BASE_SEASONINGS or x in SPECIAL_SEASONINGS else f"raw {pluralize(x)} x 1 serving" for x in sorted(all_ings)]
        recipe_texts.append(", ".join(ings_with_amount) + ".")

        # Add seasoning description
        seasonings = FLAVOR_TO_SEASONINGS.get(dish["flavor"], {})
        during = seasonings.get("during_cooking", [])
        after = seasonings.get("after_cooking", [])

        if during or after:
            lines = []
            if during:
                lines.append("Add during cooking: " + ", ".join(sorted(during)))
            if after:
                lines.append("Add to the plate after cooking: " + ", ".join(sorted(after)))
            recipe_texts.append("### Seasonings:")
            recipe_texts.append("; ".join(lines).capitalize() + ".")
    return during, after, all_ings, recipe_texts


def verbal_recipe(kitchen, 
                  original_dish, 
                  recipe_texts, 
                  mode):
    # ### Ingredients:
    # Avocado x 1 serving, beef x 1 serving, rice x 1 serving, shrimp x 1 serving.
    # ### Cooking Steps:
    # - steam the rice; then chop the avocado.
    # - boil the shrimp; then pan-fry the beef; then add rice vinegar, chili sauce, sugar on the pan.
    # - wait for all ingredients to finish cooking, then assemble them onto a plate.

    name = original_dish["name"]
    # simplify this for now
    # if mode in [0, 1, 2, 3, 4]:
    servings = 1
    # else:
        # servings = original_dish['n_servings']
    flavor = original_dish["flavor"]

    title = ''

    if mode == 4: # we use an alternative dish instead
        dish = generate_inconsistent_recipe(deepcopy(original_dish))
        state_description = describe_ingredient_states(original_dish)
        title += "We couldn't find the exact recipe the customer requested. However, here is some basic information we can provide about the dish:\n"
        title += f"{state_description}\n"
        title += "In addition, here is a recipe for a similar dish that we hope will be helpful:\n"
    else:
        dish = original_dish

    # Title
    title += "recipe for "
    if name == "sushi" and "chicken" in dish["required_ingredients"]:
        title += f"{servings} serving of **{name} with {flavor} chicken**"
    elif name == "sushi" and "beef" in dish["required_ingredients"]:
        title += f"{servings} serving of **{name} with {flavor} beef**"
    elif name == "sushi":
        title += f"{servings} serving of **{name} ({flavor})**"
    else:
        title += f"{servings} serving of **{name} ({flavor})**"
    recipe_texts.append(title)

    during, after, all_ings, recipe_texts = get_ingredients(dish, recipe_texts)
    
    # Step-by-step instruction
    recipe_texts.append("### Cooking Steps:")

    name = dish["name"]
    flavor = dish["flavor"]
    seasonings = FLAVOR_TO_SEASONINGS.get(flavor, {})

    recipe = RECIPES[name]
    steps = recipe["cooking_steps"]

    # merge all ingredients
    all_ingredients = {}
    all_ingredients.update(dish.get("main_ingredients", {}))
    all_ingredients.update(dish.get("required_ingredients", {}))
    all_ingredients.update(dish.get("optional_ingredients", {}))

    # for step_group in steps:
    if mode == 1:
        step_text_lines = describe_action(steps, all_ingredients, seasonings, kitchen)
    else:
        step_text_lines = describe_detailed_action(steps, all_ingredients, seasonings, kitchen)

    recipe_texts.append("\n".join(f"- {s}" for s in step_text_lines))

    if mode == 4:
        during, after, all_ings, _ = get_ingredients(original_dish, [])
    return recipe_texts, during, after, all_ings

def generate_recipe_from_task(kitchen, 
                              fishing,
                              task, 
                              ingredient_locations,
                              mode):
    if mode is None:
        return ''
    recipe_texts = []
    
    # ----
    # mode 0: [Changed] same as mode 2, but recipe only, no location
    # mode 1: recipe plus where to collect ingredients.
    # mode 2: more detailed than mode 1
    # mode 3: mode 2, but jump some cooking steps 
    # mode 4: inconsistent recipe (with slightly different ingredients (for example, taco, but not for chicken, but for beef))
    
    all_dishes_ings = []
    recipe_texts = []

    for dish in task["dishes"]:
        recipe_texts, during, after, all_ings = verbal_recipe(kitchen, dish, recipe_texts, mode)
        
        if mode in [1, 2, 3, 4]:
            all_dishes_ings.extend(all_ings + during + after)

    # add location information after processing all dishes
    if mode in [1, 2, 3, 4] and all_dishes_ings:
        location_priorities = ['restaurant', 'farm', 'fishing', 'store']
        location_to_ings = defaultdict(list)
        location_to_loc = {
            'restaurant': 'restaurant',
            'farm': 'farm',
            'fishing': 'harbor',
            'store': 'store'
        }

        for ing in all_dishes_ings:
            for loc in location_priorities:
                if any(item == ing or (isinstance(item, tuple) and item[0] == ing) for item in ingredient_locations[loc]):
                    location_to_ings[loc].append(ing)
                    break

        has_non_restaurant = any(
            loc in location_to_ings and location_to_ings[loc]
            for loc in location_priorities[1:]
        )

        if has_non_restaurant:
            recipe_texts.append("### You'll need to collect ingredients from the following locations:")
            for loc in location_priorities[1:]:  # ignore 'restaurant'
                if location_to_ings[loc]:
                    if loc == 'fishing' and mode in [2, 4]:
                        idx = fishing.get_available_harbor()[0]
                        recipe_texts.append(f"**Harbor_{idx}**: " + ", ".join(sorted(set(location_to_ings[loc]))))
                    else:
                        recipe_texts.append(f"**{location_to_loc[loc].capitalize()}**: " + ", ".join(sorted(set(location_to_ings[loc]))))
    return "\n".join(recipe_texts)