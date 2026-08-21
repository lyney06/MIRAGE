import random
from collections import Counter, defaultdict
from .constant import *

from pdb import set_trace as st

UNCOUNTABLE = {
    "corn", "lettuce", "chicken", "beef", "lamb", "pork", "ham", "rice",
    "flour", "milk", "cheese", "spinach", "tofu", "mushroom", "croutons", "avocado",
}
for seasoning in SEASONINGS:
    UNCOUNTABLE.add(seasoning)

IRREGULAR_PLURALS = {
    "tomato": "tomatoes",
    "potato": "potatoes"
}


def pluralize(word):
    if isinstance(word, list):
        return word
    word = word.strip()
    
    # If end with uncountable, remain the same
    for uncountable in UNCOUNTABLE:
        if word.endswith(uncountable):
            return word

    # irregular plural
    for singular, plural in IRREGULAR_PLURALS.items():
        if word.endswith(singular):
            return word[: -len(singular)] + plural

    # regular plural
    if word.endswith('y') and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    else:
        return word + 's'
    

REVERSE_IRREGULAR = {v: k for k, v in IRREGULAR_PLURALS.items()}

def singularize(word):
    word = word.strip()

    # If end with uncountable, remain the same
    for uncountable in UNCOUNTABLE:
        if word.endswith(uncountable):
            return word

    # irregular plural
    for singular, plural in IRREGULAR_PLURALS.items():
        if word.endswith(plural):
            return word[: -len(plural)] + singular

    # regular plural
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    elif word.endswith('es') and (
        word[:-2].endswith(('s', 'sh', 'ch', 'x', 'z')) or word.endswith('ses')
    ):
        return word[:-2]
    elif word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    else:
        return word
    

def ingredient_to_phrase(ingredient_dict):
    states = ingredient_dict.get('state', [])
    name = ingredient_dict.get('name', '')
    if states and 'standard' not in states:
        state_str = ",".join(states)
        return f"{state_str} {name}"
    else:
        return name


def parse_ingredient_phrase(ingredient_phrase):
    """
    Parses an ingredient phrase like:
      - "raw, chopped cucumber" → (('raw', 'chopped'), 'cucumber')
      - "rice vinegar" (a seasoning) → ((), 'rice vinegar')

    Args:
        ingredient_phrase (str): The full input phrase.
        seasonings_set (set): A set of valid seasonings (e.g., BASE + SPECIAL).

    Returns:
        tuple: (states: tuple[str], ingredient_name: str)

    Raises:
        ValueError: If the input is empty or malformed.
    """
    phrase = ingredient_phrase.strip()
    if not phrase:
        raise ValueError("Empty ingredient phrase.")

    if phrase in SEASONINGS:
        return ('standard',), phrase

    parts = phrase.split()
    ingredient_name = parts[-1]
    state_part = " ".join(parts[:-1])

    if not state_part:
        states = []
    else:
        states = list(s.strip() for s in state_part.split(","))

    return states, ingredient_name

def get_seasoning_target_map(recipe, flavor_seasoning):
    # First check if it's during_cooking or after_cooking seasoning
    steps = recipe.get("cooking_steps", [])
    for step in steps:
        for entry in step:
            if entry[0] == "seasonings":
                _, when, target = entry
                if when in flavor_seasoning:
                    return target
    return None


def join_with_commas_and(items):
    """Join a list: A, B, and C"""
    if len(items) == 0:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]
    

def describe_plate(plate, task):
    plate_id = plate.get("id", "unnamed plate")
    ingredients = plate.get("ingredients", [])
    seasoning_parts = plate.get("seasonings", [])

    # describe plate content (the state and seasonings of every ingredient)
    plate_combos = []
    for ing_entry, seasoning in zip(ingredients, seasoning_parts):
        season_tuple = tuple(sorted(seasoning)) if seasoning else ()
        for ing in ing_entry:
            name = ing["name"]
            states = tuple(sorted(ing.get("state", [])))
            plate_combos.append((name, states, season_tuple))
        if not ing_entry: # for after cooking seasonings
            plate_combos.append(('', '', season_tuple))

    plate_counter = Counter(plate_combos)

    # Is it the dish required in the task?
    for dish in task["dishes"]:
        name = dish["name"]
        flavor = dish["flavor"]
        flavor_seasoning = FLAVOR_TO_SEASONINGS.get(flavor, {})

        if "during_cooking" in flavor_seasoning:
            seasoning_type = "during_cooking"
        elif "after_cooking" in flavor_seasoning:
            seasoning_type = "after_cooking"
        else:
            seasoning_type = None
        seasoning_set = set(flavor_seasoning.get(seasoning_type, []))

        expected_combos = []
        location = get_seasoning_target_map(RECIPES[name], flavor_seasoning)

        for group in ["main_ingredients", "required_ingredients", "optional_ingredients"]:
            for ing_name, prep_list in dish.get(group, {}).items():

                for prep in prep_list:
                    states = tuple(sorted(prep))
                    seasoning_tuple = ()
                    if "during_cooking" in flavor_seasoning:
                        state = COOKING_METHOD_TO_STATE[COOKING_TOOLS[location]]
                        if state in states:
                            seasoning_tuple = tuple(sorted(seasoning_set))

                    if ing_name:
                        expected_combos.append((ing_name, states, seasoning_tuple))


        if "after_cooking" in flavor_seasoning:
            expected_combos.append(('', '', tuple(sorted(seasoning_set))))

        expected_counter = Counter(expected_combos)

        # we also have to check if the after_cooking seasonings are the last ones in the plate 
        after_cooking_seasoning_order = True
        if "after_cooking" in flavor_seasoning and ingredients:
            if not (len(ingredients[-1]) == 0 and set(seasoning_parts[-1]) == seasoning_set):
                after_cooking_seasoning_order = False

        if plate_counter == expected_counter and after_cooking_seasoning_order:
            # ✔️ Match found
            display_name = name
            if name == "sushi" and "during_cooking" in flavor_seasoning:
                if "chicken" in dish["required_ingredients"]:
                    display_name = f"sushi with {flavor} chicken"
                elif "beef" in dish["required_ingredients"]:
                    display_name = f"sushi with {flavor} beef"
                else:
                    display_name = f"sushi ({flavor})"
            else:
                display_name = f"{name} ({flavor})"

            return f"{plate_id}: A successfully prepared serving of the requested **{display_name}**."

    # If it's not a pre-defined dish, describe the ingredients.
    count_map = defaultdict(int)
    extra_seasonings = []
    for i, ing_entry in enumerate(ingredients):
        seasoning = seasoning_parts[i] if i < len(seasoning_parts) else []
        for ing in ing_entry:
            states = ing.get("state", [])
            name = ing["name"]
            state_text = ", ".join(states)
            season_text = ", ".join(seasoning) if seasoning else ""
            key = (name, state_text, season_text)
            count_map[key] += 1
        if not ing_entry:
            extra_seasonings.extend(seasoning)
    
    # Step1:  group by seasoning
    grouped_by_seasoning = defaultdict(list)
    for (name, state_text, season_text), count in sorted(count_map.items()):
        desc = f"{count} serving{'s' if count > 1 else ''} of {state_text} {name}".strip()
        grouped_by_seasoning[season_text].append(desc)

    # Generate natural laguage description
    parts = []

    for season_text, items in sorted(grouped_by_seasoning.items(), key=lambda x: (x[0] == "", x[0])):
        if season_text:
            joined_items = join_with_commas_and(items)
            parts.append(f"{joined_items}, all seasoned with {join_with_commas_and(season_text.split(', '))}")
        else:
            parts.extend([f'{x} without any seasoning' for x in items])  # no seasonings

    if extra_seasonings:
        counts = Counter(extra_seasonings)
        seasoning_phrases = [f"{k} x {v}" for k, v in sorted(counts.items())]
        seasonings_text = ', '.join(seasoning_phrases)
        if parts:
            parts.append(f"everything seasoned with {seasonings_text}")
        else:
            parts.append(f"seasonings: {seasonings_text}")

    if parts:
        return f"{plate_id}: a plated dish with " + "; ".join(parts) + "."
    else:
        return f"{plate_id}: (empty plate)"


def get_required_ingredient_locations(task, ingredient_locations):
    """
    Extract all required ingredients from a task and map them to the locations they are available.

    Args:
        task (dict): The task dictionary containing dishes and their required ingredients.
        ingredient_locations (dict): A mapping from location name to list of ingredients available there.

    Returns:
        dict: A dictionary mapping each required ingredient to a list of locations where it's found.
    """

    required_ings = set()

    for dish in task.get("dishes", []):
        for group in ["main_ingredients", "required_ingredients", "optional_ingredients"]:
            required_ings.update(dish[group].keys())
        required_ings.update(FLAVOR_TO_SEASONINGS[dish['flavor']].get('during_cooking', {}))
        required_ings.update(FLAVOR_TO_SEASONINGS[dish['flavor']].get('after_cooking', {}))

    ing_to_locs = defaultdict(list)
    for loc, ing_list in ingredient_locations.items():
        for ing in ing_list:
            if ing in required_ings:
                ing_to_locs[ing].append(loc)

    return dict(ing_to_locs)


def mark_storage_loss(ingredient_locations, ing, loss_type, reason):
    # for loc in ingredient_locations:
    if ing in ingredient_locations['restaurant']:
        ingredient_locations['restaurant'].remove(ing)
        # did you discover the loss or not? 
        ingredient_locations['restaurant'].append((ing, loss_type, reason, False))

    # make sure the agent can find it in farm / fishing / store
    fallback_locations = ["farm", "fishing", "store"]
    still_accessible = any(
        ing in ingredient_locations[loc] or
        any(isinstance(x, tuple) and x[0] == ing for x in ingredient_locations[loc])
        for loc in fallback_locations
    )


    # If it exists nowhere after loss, add a random fallback copy
    if not still_accessible:
        # fallback = random.choice(fallback_locations)
        # ingredient_locations[fallback].append(ing)
        if ing in FISHABLE_INGREDIENTS:
            ingredient_locations['fishing'].append(ing)
        elif ing in PLANTABLE_INGREDIENTS and len(ingredient_locations['farm']) < 4:
            ingredient_locations['farm'].append(ing)
        else:
            ingredient_locations['store'].append(ing)
    
    return ingredient_locations


def storage_loss(task, 
                 ingredient_locations,
                 process_num=1):
    required_ing_locations = get_required_ingredient_locations(task, ingredient_locations)

    possible_ings = list(required_ing_locations.keys())
    process_num = min(process_num, len(possible_ings))
    affected_ings = random.sample(possible_ings, process_num)
    for ing in affected_ings:
        if ing not in ingredient_locations['restaurant']:
            ingredient_locations['restaurant'].append(ing)

    # add 1 additional non-required elements here
    non_required_in_kitchen = set(ingredient_locations['restaurant']) - set(possible_ings)
    if sorted(non_required_in_kitchen):
        additional = random.sample(non_required_in_kitchen, 1)
        affected_ings.extend(additional)
    
    # Classification results
    loss_records = {
        "precheck_loss": [],
        "on_demand_loss": [],
    }

    REASON_TEMPLATES = {"plant": {
                            "precheck_loss": [
                                "all the {ing} were all used by another chef",
                                # "the {ing} were misplaced and can't be found now",
                                "all the {ing} were taken away by a customer order",
                            ],
                            "on_demand_loss": [
                                ("the {ing} have wilted and are no longer usable", 'spoiled'),
                                ("you find the {ing} already moldy", 'spoiled'),
                                # "the {ing} were infested with bugs",
                            ]
                        },
                        "meat_seafood": {
                            "precheck_loss": [
                                "someone else used all the {ing} for another dish",
                                "all the {ing} were sold out just before you returned",
                            ],
                            "on_demand_loss": [
                                ("the {ing} smell off and cannot be used", 'spoiled'),
                                ("the packaging of the {ing} was broken and they went bad", 'spoiled'),
                            ]
                        },
                        "seasoning": {
                            "precheck_loss": [
                                # "the {ing} were moved somewhere and can't be found",
                                "someone else used all the {ing} for another dish",
                            ],
                            "on_demand_loss": [
                                ("the jars labeled '{ing}' are mysteriously empty", 'empty'),
                                ("you discover the {ing} have expired", 'spoiled'),
                                ("you try to shake out some {ing}, but the jar is already empty", 'empty'),
                                ("the {ing} container was left open and they're spoiled", 'spoiled'),
                                # "there's only dust left in the {ing} jar",
                                ("you reach for the {ing}, but the containers are already empty", 'empty'),
                            ]
                        },
                        "dairy": {
                            "precheck_loss": [
                                "someone else used up all the {ing}",
                                "customers urgently took all the {ing}",
                            ],
                            "on_demand_loss": [
                                ("the {ing} smells sour and is unusable", 'spoiled'),
                                ("the {ing} has curdled and needs to be discarded", 'spoiled'),
                                ("the {ing} was left out too long and spoiled", 'spoiled'),
                                ("you find the {ing} moldy and have to throw them away", 'spoiled'),
                            ]
                        },
                        "fallback": {
                            "precheck_loss": [
                                # "the {ing} are nowhere to be found",
                                "someone else used all the {ing} for another dish",
                                "all the {ing} were taken away by a customer order",
                                "all the {ing} were all used by another chef",
                                "customers urgently took all the {ing}",
                            ],
                            "on_demand_loss": [
                                ("you check the container for {ing}, but it's completely empty", 'empty'),
                                ("you find the {ing} moldy and have to throw them away", 'spoiled'),
                            ]
                        }
                    }
    
    def get_ingredient_type(ing):
        if ing in PLANTABLE_INGREDIENTS:
            return "plant"
        elif ing in MEAT_SEAFOOD_DICT["all"]:
            return "meat_seafood"
        elif ing in SEASONINGS:
            return "seasoning"
        elif ing in ["milk", "cheese", "butter", "cream", "sour cream"]:
            return "dairy"
        else:
            return "fallback"
        
    def sample_storage_loss_reason(ing, loss_type):
        ing_type = get_ingredient_type(ing)
        templates = REASON_TEMPLATES.get(ing_type)
        candidates = templates.get(loss_type)
        template = random.choice(candidates)
        return template

    for ing in affected_ings:
        loss_type = random.choices(population=['on_demand_loss', 'precheck_loss'],
                                    weights=[0.8, 0.2],
                                    k=1)[0]
        reason = sample_storage_loss_reason(ing, loss_type)
        # print(ing, loss_type, reason)
        ingredient_locations = mark_storage_loss(ingredient_locations, ing, loss_type, reason)

    print(f'influenced ingredients: {affected_ings}')
    return ingredient_locations
    