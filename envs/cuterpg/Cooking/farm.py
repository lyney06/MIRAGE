# farm.py
import random
import pygame
from .utils import pluralize, singularize, ingredient_to_phrase
from .config import ASSETS_PATH, WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE
from pdb import set_trace as st

class Farm:
    def __init__(self, 
                 map, 
                 farm_ingredients,
                 crop_gone=False,
                 desired_in_farm=[]):
        self.map = map
        self.crop_gone = crop_gone
        self.desired_in_farm = desired_in_farm
        self.crops = {}
        total_spot = 24
        for crop in farm_ingredients:
            self.crops[crop] = total_spot // len(farm_ingredients)

        self.images = {
            "carrot": pygame.image.load(f"{ASSETS_PATH}crops/carrot.png").convert_alpha(),
            "corn": pygame.image.load(f"{ASSETS_PATH}crops/corn.png").convert_alpha(),
            "cucumber": pygame.image.load(f"{ASSETS_PATH}crops/cucumber.png").convert_alpha(),
            "lettuce": pygame.image.load(f"{ASSETS_PATH}crops/lettuce.png").convert_alpha(),
            "potato": pygame.image.load(f"{ASSETS_PATH}crops/potato.png").convert_alpha(),
            "tomato": pygame.image.load(f"{ASSETS_PATH}crops/tomato.png").convert_alpha()
        }
        self.plant_positions = {}   # coordinate: state
        for row in range(WINDOW_WIDTH // 2 - (3 * 6 - 1) * GRID_SIZE, WINDOW_WIDTH // 2 + 3 * 6 * GRID_SIZE, 4 * GRID_SIZE):
            for col in range(WINDOW_HEIGHT // 2 - (3 + 1) * 6 * GRID_SIZE, WINDOW_HEIGHT // 2 - 6 * GRID_SIZE, 6 * GRID_SIZE):
                self.plant_positions[(row, col)] = None
        self.assign_pos_to_crops()
        self.farm_info = ''


    def assign_pos_to_crops(self):
        for i in self.plant_positions:
            self.plant_positions[i] = None

        available_positions = sorted(self.plant_positions.keys())

        pos_idx = 0
        for crop, count in self.crops.items():
            for _ in range(count):
                if pos_idx >= len(available_positions):
                    print(f"⚠️ Not enough positions to plant all crops.")
                    return
                self.plant_positions[available_positions[pos_idx]] = crop
                pos_idx += 1


    def simulate_farm(self, locations, store):
        # Due to various reasons, some crops disappear!
        # Now they will be available in the store.
        # Singular form (for a single crop)
        singular_reasons = [
            "turkeys have trampled over the {crop} beds",
            "squirrels have stolen all the {crop}",
            "a family of rabbits ate the young {crop} leaves",
            "birds pecked all the {crop} sprouts clean",
            "gophers tunneled under and uprooted the {crop}",
            "{crop} didn't sprout this season",
            "late frost stunted the {crop} growth",
            "{crop} seeds were defective",
            "too little sun this week for {crop} to mature",
            "heavy rain washed away the {crop} seeds",
            "{crop} was affected by root rot",
            "{crop} is not yet mature enough to harvest",
            "{crop} needs a few more days to ripen",
            "the {crop} hasn't reached harvesting stage",
        ]

        # Plural form (for multiple crops)
        plural_reasons = [
            "turkeys have trampled over the {crop} beds",
            "squirrels have stolen all the {crop}",
            "animals destroyed the {crop} patches overnight",
            "flooding ruined the {crop} fields",
            "none of the {crop} sprouted this season",
            "a sudden frost damaged all the {crop}",
            "bugs infested the {crop} crops",
            "the {crop} were accidentally uprooted",
            "the {crop} are not yet mature enough to harvest",
            "the {crop} need more time to grow",
            "none of the {crop} are ready for harvest yet",
        ]

        random.shuffle(self.desired_in_farm)
        removed = self.desired_in_farm[:2]
        for crop in removed:
            self.remove_crop(crop)

            # make sure we have something in stock
            if crop not in store.valid_phrases:
                store.restock(crop)
            if crop not in locations['store']:
                locations['store'].append(crop)

        if len(removed) == 1:
            crop_info = removed[0]
            reason_template = random.choice(singular_reasons)
        else:
            crop_info = f"{removed[0]} and {removed[1]}"
            reason_template = random.choice(plural_reasons)

        # self.farm_info = reason_template.format(crop=crop_info)
        crop_text = f"{removed[0]} and {removed[1]}" if len(removed) == 2 else removed[0]
        self.farm_info = f"{reason_template.format(crop=crop_info)}. As a result, {crop_text} cannot be harvested now."
        return
    

    def remove_crop(self, crop):
        self.crops.pop(crop, None)

        for pos in self.plant_positions:
            if self.plant_positions[pos] == crop:
                self.plant_positions[pos] = None


    def harvest(self, character, ingredient_name):
        ingredient_name = singularize(ingredient_name)
        if character.position != 'farm':
            return False, "You cannot harvest crops outside the farm."

        if ingredient_name not in self.crops:
            return False, f"There is no {ingredient_name} left to harvest."

        # harvest all that crop
        full_name = f"raw {ingredient_name}"
        character.get_ingredient({full_name: {'name': ingredient_name,
                                              'state': ['raw'], 
                                              'serving': 100}})
        
        self.remove_crop(ingredient_name)
        return True, f"You harvested all the {pluralize(ingredient_name)}!"


    def get_farm_observation(self):
        if not self.crops:
            if self.farm_info:
                return f'You are at the farm. However, {self.farm_info}'
            else:
                return "The farm looks bare — nothing is growing at the moment."

        crop_names = list(self.crops.keys())

        info = 'You are at the farm. '

        if len(crop_names) == 1:
            info += f"In the farm, you see some ripe {pluralize(crop_names[0])}."

        elif len(crop_names) == 2:
            info += f"In the farm, you see ripe {pluralize(crop_names[0])} and {pluralize(crop_names[1])}."

        else:
            crop_str = ", ".join([pluralize(c) for c in crop_names[:-1]]) + f", and {pluralize(crop_names[-1])}"
            info += f"In the farm, you see ripe {crop_str}."
        
        if self.farm_info:
            info += f'However, {self.farm_info}'
        return info

    def draw(self, screen):
        for position in self.plant_positions:
            if self.plant_positions[position]:
                if self.plant_positions[position] not in self.images:
                    print(f"No image of {position['occupied_by']}")
                else:
                    screen.blit(self.images[self.plant_positions[position]], position)

