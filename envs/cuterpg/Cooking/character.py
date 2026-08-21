# character.py

import re
import itertools
from .config import GRID_SIZE, CHARACTER_WIDTH, CHARACTER_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT
from .constant import FLAVOR_TO_SEASONINGS, SEASONINGS
from .utils import pluralize, describe_plate
from pdb import set_trace as st

class Character:
    def __init__(self, itemFetcher, task):
        self.image = itemFetcher.get_sprite(0, 0, CHARACTER_WIDTH, CHARACTER_HEIGHT)
        self.potential_positions = {
            "kitchen": (WINDOW_WIDTH // 2 - (18 + 10) * GRID_SIZE, WINDOW_HEIGHT // 2 - (6 + 8) * GRID_SIZE),
            "farm": (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 6 * GRID_SIZE),
            "store": (WINDOW_WIDTH // 2 + (18 + 8) * GRID_SIZE, WINDOW_HEIGHT // 2 - 6 * GRID_SIZE),
            "harbor": [(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2 + 12 * GRID_SIZE),
                       (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 12 * GRID_SIZE),
                       (WINDOW_WIDTH // 4 * 3, WINDOW_HEIGHT // 2 + 12 * GRID_SIZE)]
        }
        self.task = task
        self.position = 'kitchen'
        self.coordinate = self.potential_positions['kitchen']
        self.ingredients = {}   # {full_ingredient_name: {'name': [], 'state': [], 'weight': ""}}
        self.carrying = {} # this is only valid when you are in the kitchen
        self.finished_dishes = []


    def draw(self, screen):
        x, y = self.coordinate
        screen.blit(self.image, (x, y))


    def goto_kitchen(self, kitchen, precheck_info=''):
        self.position = 'kitchen'
        self.coordinate = self.potential_positions['kitchen']
        info = self.place_items_to_kitchen(kitchen, precheck_info)
        return info

    def place_items_to_kitchen(self, kitchen, precheck_info=''):
        loc_info = {'fridge': [], 'cabinet': []}
        for ingredient_full, info in self.ingredients.items():
            if 'standard' in info['state']:
                full_name = pluralize(info['name'])
            else:
                full_name = f"{','.join(info['state'])} {pluralize(info['name'])}"
            loc = kitchen.put_item_to_loc({ingredient_full: info})
            loc_info[loc].append(full_name)

        info = 'You are now in the kitchen of your restaurant. '
        if precheck_info:
            info += f'\n{precheck_info}\n'

        for loc in loc_info:
            if loc_info[loc]:
                # You restock the fridge with raw shrimps, raw octopuses, and raw lobsters.
                info += f"You restock the {loc} with {'; '.join(loc_info[loc])}. \n"
        self.ingredients = {}
        return info
    
    def goto_farm(self):
        self.position = 'farm'
        self.coordinate = self.potential_positions['farm']

    def goto_store(self):
        self.position = 'store'
        self.coordinate = self.potential_positions['store']


    def goto_harbor(self, location, position_status):
        # parse the number in harbor_x
        info = ''
        try:
            spot_idx = int(location.split('_')[-1]) - 1
            assert 0 <= spot_idx < len(position_status)
        except:
            info = f"'{location}' is not a valid fishing location."
            return False, info

        if position_status[spot_idx] == 'occupied':
            info = f"Fishing spot {location} is currently taken by other people."
            return False, info

        self.position = 'harbor'
        self.coordinate = self.potential_positions['harbor'][spot_idx]
        info = f"You walk to {location}. The spot is free, and you can get ready to fish here."
        return True, info


    def get_ingredient(self, ingredient):
        for full_name, info in ingredient.items():
            if full_name in self.ingredients:
                # accumulate number of servings
                self.ingredients[full_name]['serving'] += info.get('serving', 1)
            else:
                # if no such ingredient, add it
                self.ingredients[full_name] = {
                    'name': info['name'],
                    'state': info.get('state', []),
                    'serving': info.get('serving', 1)
                }


    def after_cook_tool(self, cooked_ingredients):
        self.ingredients.update(cooked_ingredients)


    def add_seasoning_to_plated_dish(self, dish, seasoning):
        self.finished_dishes[dish].append(seasoning)

    def carrying_info(self):
        if not self.carrying:
            return "nothing"
        ing_name = self.carrying["full_name"]
        
        if ing_name in SEASONINGS:
            return [ing_name]
        
        def generate_all_combinations(ing_name):
            parts = ing_name.strip().split()
            if not parts:
                return []

            ingredient = parts[-1]
            states_raw = " ".join(parts[:-1])
            states = [s.strip() for s in states_raw.split(",") if s.strip()]

            if not states:
                return [ing_name]

            # original order
            original = ", ".join(states) + f" {ingredient}"

            # all combinations (no duplicates, except original order)
            all_perms = set(itertools.permutations(states))
            all_perms.discard(tuple(states))  # discard original order

            others = [", ".join(p) + f" {ingredient}" for p in sorted(all_perms)]
            return [original] + others
        
        result = [pluralize(x) for x in generate_all_combinations(ing_name)]
        return result

    def get_self_observation(self):
        lines = []

        if self.ingredients:
            ing_obs = []
            for full_name, info in self.ingredients.items():
                if 'standard' in info['state']:
                    ing_obs.append(pluralize(info['name']))
                else:
                    ing_obs.append(f"{','.join(info['state'])} {pluralize(info['name'])}")
            lines.append("You have some: " + ', '.join(ing_obs) + " with you.")
        else:
            lines.append("You're not carrying anything right now.")
        
        return '\n'.join(lines)

