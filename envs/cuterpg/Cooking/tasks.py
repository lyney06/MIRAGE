import math
from collections import defaultdict
import random
from .constant import *
from pdb import set_trace as st

def allocate_ingredients(ingredient_locations, 
                         main_ingredients, 
                         required_ingredients, 
                         optional_ingredients, 
                         seasonings=None,
                         desired_in_farm=False):
    all_ingredients = list(main_ingredients.keys()) + list(required_ingredients.keys()) + list(optional_ingredients.keys())

    for ingredient in all_ingredients:
        # seafood
        if ingredient in FISHABLE_INGREDIENTS:
            assigned = ["fishing"]

            # 10% probability to be found in store or restaurant
            if random.random() < 0.05:
                extra_loc = random.choice(["store", "restaurant"])
                assigned.append(extra_loc)

        else:
            # other ingredients
            locations = []
            if ingredient in PLANTABLE_INGREDIENTS:
                locations.append("farm")
            if ingredient in PURCHASABLE_ONLY_INGREDIENTS or ingredient in PLANTABLE_INGREDIENTS:
                locations.append("store")
            locations.append("restaurant")

            if len(locations) == 1:
                assigned = locations
            else:
                if random.random() < 0.9:
                    assigned = [random.choice(locations)]
                else:
                    assigned = random.sample(locations, k=2)

        # assign ingredients to locations
        for loc in assigned:
            ingredient_locations[loc].append(ingredient)

    if seasonings:
        all_seasonings = []
        for when in ["during_cooking", "after_cooking"]:
            all_seasonings.extend(seasonings.get(when, []))

        for s in all_seasonings:
            
            if s in BASE_SEASONINGS:
                if random.random() < 0.8:
                    if s not in ingredient_locations["restaurant"]:
                        ingredient_locations["restaurant"].append(s)
                else:
                    if s not in ingredient_locations["store"]:
                        ingredient_locations["store"].append(s)
            elif s in SPECIAL_SEASONINGS:
                if random.random() < 0.8:
                    if s not in ingredient_locations["store"]:
                        ingredient_locations["store"].append(s)
                else:
                    if s not in ingredient_locations["restaurant"]:
                        ingredient_locations["restaurant"].append(s)
            else:
                # store by default
                if s not in ingredient_locations["store"]:
                    ingredient_locations["store"].append(s)

    # Arbitratily assign other useless ingredients
    all_pool = sorted(set(PLANTABLE_INGREDIENTS + FISHABLE_INGREDIENTS + PURCHASABLE_ONLY_INGREDIENTS) - set(all_ingredients + all_seasonings))
    extra_ingredients = random.sample(all_pool, len(all_pool) // 4)
    farm_limit = 8
    farm_current = set(ingredient_locations["farm"])
    for item in sorted(farm_current):
        desired_in_farm.append(item)

    for ing in extra_ingredients:
        if ing in PLANTABLE_INGREDIENTS:
            # Plantable ingredients are in either farm or store
            # Note: the farm has a capacity
            if len(farm_current) < farm_limit and random.random() < 0.5:
                ingredient_locations["farm"].append(ing)
                farm_current.add(ing)
            else:
                ingredient_locations["store"].append(ing)
        else:
            # Other ingredients are in the store
            ingredient_locations["store"].append(ing)
    
    extra_choices = random.sample(ADDITIONAL_SEAFOOD, k=2)
    for seafood in extra_choices:
        if seafood not in ingredient_locations["fishing"]:
            ingredient_locations["fishing"].append(seafood)

    if not ingredient_locations["farm"]:
        available_crops = sorted(list(set(PLANTABLE_INGREDIENTS) - set(all_ingredients + all_seasonings)))
        if available_crops:
            num_to_sample = min(2, len(available_crops))
            fallback_crops = random.sample(available_crops, num_to_sample)
            ingredient_locations["farm"].extend(fallback_crops)

    return ingredient_locations

def initialize_task(mode,
                    max_servings=1):
    """
    Generate an arbitrary task, including flavor and ingredients, and assign them to different locations.
    """
    if mode == 'easy':
        num_dishes = 1
    elif mode == 'hard':
        num_dishes = random.randint(2, 3)
        
    selected_dishes = random.sample(sorted(RECIPES.keys()), num_dishes)

    task = {"dishes": []}
    ingredient_locations = {
        "restaurant": [],
        "farm": [],
        "store": [],
        "fishing": []
    }

    # we want something from the farm
    desired_in_farm = []

    for dish in selected_dishes:
        recipe = RECIPES[dish]
        # n_servings = random.randint(1, max_servings)
        n_servings = max_servings

        # Choose a flavor
        possible_flavors = [flavor for flavor, dishes in FLAVOR_TO_DISHES.items() if dish in dishes]
        selected_flavor = random.choice(possible_flavors)
        required_seasonings = FLAVOR_TO_SEASONINGS[selected_flavor]

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
        
        def select_option(ingredient, ing_lst, target):
            valid_options = [p for p in ing_lst[ingredient] if method_available(p[:-1])]
            if not valid_options:
                return
            selected_prep = random.choice(valid_options)
            target[ingredient] = [selected_prep[:-1]] # exclude amount
            update_method_usage(selected_prep[:-1])
            return
        
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
        available_requireds = list(recipe["required_ingredients"].keys())
        random.shuffle(available_requireds)
        for ingredient in available_requireds:
            if len(required_ingredients) >= num_required:
                break
            # valid_options = [p for p in recipe["required_ingredients"][ingredient] if method_available(p[:-1])]
            # if not valid_options:
            #     continue
            # selected_prep = random.choice(valid_options)
            # required_ingredients[ingredient] = [selected_prep[:-1]]
            # update_method_usage(selected_prep[:-1])
            select_option(ingredient, recipe["required_ingredients"], required_ingredients)

        # --- optional_ingredients ---
        optional_ingredients = {}
        num_optional = random.randint(*recipe["rules"]["optional"])
        available_optionals = list(recipe["optional_ingredients"].keys())
        random.shuffle(available_optionals)
        for ingredient in available_optionals:
            if len(optional_ingredients) >= num_optional:
                break
            # valid_options = [p for p in recipe["optional_ingredients"][ingredient] if method_available(p[:-1])]
            # st()
            # if not valid_options:
            #     continue
            # selected_prep = random.choice(valid_options)
            # optional_ingredients[ingredient] = [selected_prep[:-1]]
            # update_method_usage(selected_prep[:-1])
            select_option(ingredient, recipe["optional_ingredients"], optional_ingredients)


        # Special for sushi
        if dish == "sushi" and "during_cooking" in required_seasonings:
            has_chicken = "chicken" in required_ingredients
            has_beef = "beef" in required_ingredients
            if has_chicken and has_beef:
                to_remove = random.choice(["chicken", "beef"])
                del required_ingredients[to_remove]
            if not has_chicken and not has_beef:
                extra_protein = random.choice(["chicken", "beef"])
                select_option(extra_protein, recipe["required_ingredients"], required_ingredients)
                # required_ingredients[extra_protein] = RECIPES[dish]['required_ingredients'][extra_protein]

        # Assign locations
        ingredient_locations = allocate_ingredients(
            ingredient_locations, main_ingredients, required_ingredients, optional_ingredients, seasonings=required_seasonings, desired_in_farm=desired_in_farm
        )

        task["dishes"].append({
            "name": dish,
            "n_servings": n_servings,
            "flavor": selected_flavor,
            "main_ingredients": main_ingredients,
            "required_ingredients": required_ingredients,
            "optional_ingredients": optional_ingredients,
            "num_ingredients": len(main_ingredients) + len(required_ingredients) + len(optional_ingredients)
        })
        
    return task, ingredient_locations, desired_in_farm