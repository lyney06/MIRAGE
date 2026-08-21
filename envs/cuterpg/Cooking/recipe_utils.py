import copy
import random
from .constant import *
from collections import defaultdict

def generate_inconsistent_recipe(original_dish):
    """
    Given a dish (from a task), re-sample a similar dish:
    - same name & flavor
    - different ingredients from the original dish (maximize difference)
    """
    dish_name = original_dish["name"]
    flavor = original_dish["flavor"]
    n_servings = original_dish["n_servings"]

    recipe = RECIPES[dish_name]
    required_seasonings = FLAVOR_TO_SEASONINGS[flavor]

    method_usage = defaultdict(int)

    def update_method_usage(prep_tuple):
        for state in prep_tuple:
            method = STATE_TO_METHOD.get(state)
            if method:
                method_usage[method] += 1

    def method_available(prep_tuple):
        for state in prep_tuple:
            method = STATE_TO_METHOD.get(state)
            if method:
                for tool, methods in COOKING_TOOLS.items():
                    if method in methods:
                        if method_usage[method] >= TOOL_MAX_CAP.get(tool, 1):
                            return False
        return True

    # Set of original ingresients
    original_ings = set(original_dish["main_ingredients"].keys()) | \
                    set(original_dish["required_ingredients"].keys()) | \
                    set(original_dish["optional_ingredients"].keys())

    def sample_different_ingredients(candidates, num_required):
        """
        Sample ingredients from `candidates`, prioritizing those not in original_ings.
        """
        shuffled = list(candidates)
        random.shuffle(shuffled)

        # Prioritize those not in the original set
        preferred = [ing for ing in shuffled if ing not in original_ings]
        fallback = [ing for ing in shuffled if ing in original_ings]

        result = preferred[:num_required]
        if len(result) < num_required:
            result += fallback[:(num_required - len(result))]
        return result

    # --- main_ingredients ---
    main_ingredients = {}
    for name, options in recipe["main_ingredients"].items():
        valid_options = [p for p in options if method_available(p[:-1])]
        if not valid_options:
            continue
        selected_prep = random.choice(valid_options)
        main_ingredients[name] = [selected_prep[:-1]]
        update_method_usage(selected_prep[:-1])

    # --- required_ingredients ---
    required_ingredients = {}
    num_required = random.randint(*recipe["rules"]["required"])
    candidate_requireds = list(recipe["required_ingredients"].keys())
    selected_requireds = sample_different_ingredients(candidate_requireds, num_required)
    for ingredient in selected_requireds:
        valid_options = [p for p in recipe["required_ingredients"][ingredient] if method_available(p[:-1])]
        if not valid_options:
            continue
        selected_prep = random.choice(valid_options)
        required_ingredients[ingredient] = [selected_prep[:-1]]
        update_method_usage(selected_prep[:-1])

    # --- optional_ingredients ---
    optional_ingredients = {}
    num_optional = random.randint(*recipe["rules"]["optional"])
    candidate_optionals = list(recipe["optional_ingredients"].keys())
    selected_optionals = sample_different_ingredients(candidate_optionals, num_optional)
    for ingredient in selected_optionals:
        valid_options = [p for p in recipe["optional_ingredients"][ingredient] if method_available(p[:-1])]
        if not valid_options:
            continue
        selected_prep = random.choice(valid_options)
        optional_ingredients[ingredient] = [selected_prep[:-1]]
        update_method_usage(selected_prep[:-1])

    # Special process for Sushi
    if dish_name == "sushi" and "during_cooking" in required_seasonings:
        has_chicken = "chicken" in required_ingredients
        has_beef = "beef" in required_ingredients
        if has_chicken and has_beef:
            to_remove = random.choice(["chicken", "beef"])
            del required_ingredients[to_remove]
        if not has_chicken and not has_beef:
            extra_protein = random.choice(["chicken", "beef"])
            required_ingredients[extra_protein] = [p[:-1] for p in RECIPES[dish_name]['required_ingredients'][extra_protein]]

    new_dish = {
        "name": dish_name,
        "n_servings": n_servings,
        "flavor": flavor,
        "main_ingredients": main_ingredients,
        "required_ingredients": required_ingredients,
        "optional_ingredients": optional_ingredients,
        "num_ingredients": len(main_ingredients) + len(required_ingredients) + len(optional_ingredients)
    }

    return new_dish