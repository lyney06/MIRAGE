# RL_environment.py
import re
import copy
import random
from collections import Counter
from .map import GameMap
from .character import Character
from .recipe import generate_recipe_from_task, get_multi_step_ingredients
from .getCuterpgItem import getCuterpgItem
from .map import GameMap
from .character import Character
from .tasks import initialize_task
from .farm import Farm
from .kitchen import Kitchen
from .store import Store
from .fishing import Fishing
from .observation import Observation
from .task_converter import convert_task_to_text, convert_single_dish_to_text
from .actions import parse_put_action, parse_plate_action
from .utils import get_seasoning_target_map, storage_loss
from .constant import *

from pdb import set_trace as st

class Env:
    def __init__(self, 
                 mode,
                 crop_gone=False,
                 novice_mistake=False,
                 storage_loss=False,
                 n_servings=1):
        self.mode = mode
        self.crop_gone = crop_gone
        self.novice_mistake = novice_mistake
        # something at restaurant can be broken.
        self.storage_loss = storage_loss
        self.n_servings = n_servings
        self.itemFetcher = getCuterpgItem()

    def initialize_task(self):
        task, locations, desired_in_farm = initialize_task(self.mode,
                                                           self.n_servings)
        if self.crop_gone:
            # in this case, we only need task that requires something from the farm land
            while not desired_in_farm:
                task, locations, desired_in_farm = initialize_task(self.mode,
                                                                   self.n_servings)
        return task, locations, desired_in_farm
    
    def record_task(self, task_info):
        self.initial_task = copy.deepcopy(self.task)
        self.initial_locations = copy.deepcopy(self.locations)
        self.initial_desired = copy.deepcopy(self.desired_in_farm)
        self.initial_task_info = copy.deepcopy(task_info)
        return
    
    def rewind(self):
        self.task, self.locations = copy.deepcopy(self.initial_task), copy.deepcopy(self.initial_locations)
        self.horizon = self.get_horizon()
        self.desired_in_farm = self.desired_in_farm
        self.task_text = convert_task_to_text(self.task)
        
        self.map = GameMap(self.itemFetcher)
        self.character = Character(self.itemFetcher, self.task)
        self.farm = Farm(self.map, 
                         self.locations['farm'], 
                         self.crop_gone,
                         self.desired_in_farm)
        self.store = Store(self.locations['store'])
        self.fishing = Fishing(self.map, self.locations['fishing'])
        self.kitchen = Kitchen(self.character, 
                               self.task, 
                               self.locations['restaurant'],
                               novice_mistake=self.novice_mistake)
        self.obs_func = Observation(self.character, self.kitchen, self.farm, self.store, self.fishing)
        obs = self.obs_func.get_full_observation()
        task_info = self.initial_task_info
        obs = f"{task_info}\n{obs}"
        self.step_count = 0
        return obs


    def reset(self):
        task, locations, desired_in_farm = self.initialize_task()
        if self.storage_loss:
            locations = storage_loss(task, 
                                     locations,
                                     process_num=3 if self.mode=='easy' else 5)
            
        self.task, self.locations = task, locations
        self.horizon = self.get_horizon()
        self.desired_in_farm = desired_in_farm
        self.task_text = convert_task_to_text(task)
        
        self.map = GameMap(self.itemFetcher)
        self.character = Character(self.itemFetcher, task)
        self.farm = Farm(self.map, 
                         locations['farm'], 
                         self.crop_gone,
                         self.desired_in_farm)
        self.store = Store(locations['store'])
        self.fishing = Fishing(self.map, locations['fishing'])
        self.kitchen = Kitchen(self.character, 
                               task, 
                               locations['restaurant'],
                               novice_mistake=self.novice_mistake)
        self.obs_func = Observation(self.character, self.kitchen, self.farm, self.store, self.fishing)
        obs = self.obs_func.get_full_observation()
        n_dishes = sum(dish['n_servings'] for dish in self.task['dishes'])
        # task_info = f'Your task is to prepare {n_dishes} dishes: {self.task_text}'
        task_info = self.generate_task_intro(n_dishes, self.task_text)
        self.record_task(task_info)
        obs = f"{task_info}\n{obs}"
        self.step_count = 0
        return obs
    
    def goto_loc(self, location):
        invalid_info = ''
        action_success = True
        action_info = ""
        if location == self.character.position or (location == 'restaurant' and self.character.position=='kitchen'):
            invalid_info = f'You are already at the {location}.'
        elif location == 'restaurant':
            self.kitchen.visit_times += 1
            info = ''
            if self.kitchen.visit_times >= 1:
                info = self.kitchen.discard_precheck_loss()
            action_info = self.character.goto_kitchen(self.kitchen, info)
        elif location == 'farm':
            self.character.goto_farm()
        elif location == 'store':
            self.character.goto_store()
        elif location.startswith('harbor'):
            action_success, action_info = self.character.goto_harbor(location, self.fishing.position_status)
            if not action_success:
                invalid_info = action_info
        else:
            invalid_info = 'Invalid Action Format!'
        return action_success, action_info, invalid_info
        

    def take_action(self, action_text):
        action = action_text.strip().split(' ')
        action_info = ""
        invalid_info = ""
        done = False
        kitchen_action_lst = ['put', 'chop', 'plate', 'serve']

        if action[0] == 'goto':
            if len(action) == 2:
                location = action[-1]
                action_success, action_info, invalid_info = self.goto_loc(location)
            else:
                invalid_info = 'Invalid Action Format!'
                
        elif action[0] == 'status':
            next_obs = self.obs_func.get_full_observation(force=True)
            status_obs = f"{self.initial_task_info}\n{next_obs}"
            reward, done = self.compute_reward_and_done(done)
            return status_obs, reward, done, {}

        elif action[0] == 'harvest':
            action = [x for x in action if x != 'ripe']
            if len(action) == 2:
                crop = action[1]
                if crop[0] == '[':
                    invalid_info = "Invalid Action Format!"
                else:
                    action_success, action_info = self.farm.harvest(self.character, crop)
                if not action_success:
                    invalid_info = action_info
            else:
                invalid_info = 'Invalid Action Format!'

        elif action[0] == 'fish':
            if len(action) == 2:
                seafood = action[1]
                action_success, action_info = self.fishing.fishing(self.character, seafood)
                if not action_success:
                    invalid_info = action_info
            else:
                invalid_info = 'Invalid Action Format!'

        elif action[0] == 'buy':
            action_success, action_info = self.store.buy(self.character, ' '.join(action[1:]))
            if not action_success:
                invalid_info = action_info
                
        elif action[0] in kitchen_action_lst and self.character.position != 'kitchen':
            action_success, action_info = False, "You cannot do this action outside the restaurant kitchen."
            if not action_success:
                invalid_info = action_info
        
        elif action[0] == 'put':
            # put <ingredient> into <tool>
            try:
                ingredient, tool = parse_put_action(action_text)
                action_success, action_info = self.kitchen.put_ingredient_in_tool(ingredient, tool)
                if not action_success:
                    self.kitchen.undo_take()
                    invalid_info = action_info
            except ValueError as e:
                invalid_info = str(e)

        elif action[0] == 'chop':
            # chop <ingredient>
            # also valid: put <ing> on cuttinf_board, then chop <ing>
            if len(action) == 1:
                invalid_info = 'Invalid Action Format!'
            else:
                action_success, action_info = self.kitchen.chop_ingredient_with_knife(' '.join(action[1:]))
                if not action_success:
                    self.kitchen.undo_take()
                    invalid_info = action_info

        elif action[0] == 'wait':
            # otherwise we do nothing
            if len(action) == 1:
                action_success, action_info = self.kitchen.tick_all_tools(return_msg=True)
            else:
                action_success = False
                invalid_info = 'Invalid Action Format!'

        elif action[0] == 'plate':
            try:
                mode, source, plate_id = parse_plate_action(action_text)
                # plate from <tool> into <plate_id>
                if mode == "from_tool":
                    action_success, action_info = self.kitchen.plate_from_tool(source, plate_id)
                else:
                    action_success = False
                    action_info = "Invalid plate mode."

            except ValueError as e:
                action_success = False
                action_info = str(e)

            if not action_success:
                invalid_info = action_info
                
        elif action[0] == 'serve':
            if len(action) == 2:
                last_rew, _, prev_dish = self.compute_reward_and_done(done, True)
                action_success, action_info = self.kitchen.serve_plate(action[1])

                if action_success:
                    new_rew, _, new_dish = self.compute_reward_and_done(done, True)

                    if new_rew <= last_rew:
                        action_info += " However, this dish does not satisfy the requirement, so you receive no reward."
                    else:
                        # successfully serve a new dish, find out what it is
                        new_dish_name = None
                        for dish_name in new_dish:
                            prev_count = prev_dish.get(dish_name, 0)
                            new_count = new_dish[dish_name]
                            if new_count > prev_count:
                                new_dish_name = dish_name
                                break
                        
                        if new_dish_name:
                            action_info += f" This is a successful serving {new_dish_name[10:]}"
            else:
                action_success = False
                invalid_info = 'Invalid Action Format! You can only do: serve plate_<id>'

        elif action[0] == 'stop':
            done = True
            action_info = "You have chosen to stop the task."

        else:
            invalid_info = 'Invalid Action Format!'

        if action[0] != 'wait':
            _, wait_info = self.kitchen.tick_all_tools()
            action_info += f'\n{wait_info}'

        reward, done = self.compute_reward_and_done(done)
        # print(reward, done)
        info = {}
        next_obs = self.obs_func.get_full_observation()

        if invalid_info:
            next_obs = invalid_info
        else:
            next_obs = f"{action_info}\n{next_obs}"

        self.kitchen.print_kitchen_storage()
        next_obs = re.sub(r'\n{2,}', '\n', next_obs.strip())
        next_obs = next_obs.strip()
        return next_obs, reward, done, info
    
    def compute_reward_and_done(self, original_done, return_dish=False):
        task = self.task
        total_servings_required = sum(d['n_servings'] for d in task['dishes'])
        servings_done = 0
        used_plate_ids = set()

        dish_servings_done = {}  # the degree of completion of every dish

        for dish in task["dishes"]:
            matched = 0

            name = dish["name"]
            flavor = dish["flavor"]
            flavor_seasoning = FLAVOR_TO_SEASONINGS.get(flavor, {})

            # define seasoning type
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

            for plate_id in sorted(set(self.kitchen.served_plates) - used_plate_ids):
                plate = self.kitchen.served_plates[plate_id]
                ingredients = plate.get("ingredients", [])
                seasoning_parts = plate.get("seasonings", [])

                plate_combos = []
                for ing_entry, seasoning in zip(ingredients, seasoning_parts):
                    season_tuple = tuple(sorted(seasoning)) if seasoning else ()
                    for ing in ing_entry:
                        name = ing["name"]
                        states = tuple(sorted(ing.get("state", [])))
                        plate_combos.append((name, states, season_tuple))
                    if not ing_entry:
                        plate_combos.append(('', '', season_tuple))

                plate_counter = Counter(plate_combos)

                after_cooking_seasoning_order = True
                if "after_cooking" in flavor_seasoning and ingredients:
                    if not (len(ingredients[-1]) == 0 and set(seasoning_parts[-1]) == seasoning_set):
                        after_cooking_seasoning_order = False

                if (plate_counter == expected_counter) and after_cooking_seasoning_order:
                    matched += 1
                    used_plate_ids.add(plate_id)
                    if matched >= dish['n_servings']:
                        break

            servings_done += matched
            dish_descrip = copy.deepcopy(dish)
            dish_descrip['n_servings'] = 1
            dish_servings_done[convert_single_dish_to_text(dish_descrip)] = matched  # record number of servings of every dish

        reward = servings_done / total_servings_required
        done = servings_done >= total_servings_required
        self.step_count += 1
        if self.step_count >= self.get_horizon():
            done = True
            
        if return_dish:
            return reward, original_done or done, dish_servings_done
        else:
            return reward, original_done or done
        
    
    def get_manual(self, mode):
        manual = generate_recipe_from_task(self.kitchen, 
                                           self.fishing,
                                           self.task, 
                                           self.locations, 
                                           mode)
        return manual
    

    def simulate_env_variants(self):
        if self.crop_gone:
            self.farm.simulate_farm(self.locations, 
                                    self.store)
            
    def generate_task_intro(self, n_dishes, task_text):
        templates = [
            f"Your task is to prepare {n_dishes} dishes: {task_text}",
            f"You've received an order for {n_dishes} dishes: {task_text}",
            f"The restaurant has {n_dishes} new orders: {task_text}",
            f"Time to get to work — {n_dishes} dishes to prepare: {task_text}",
            f"Incoming order! Please make {n_dishes} dishes: {task_text}",
            f"Let's begin. You need to cook these {n_dishes} dishes: {task_text}"
        ]
        return random.choice(templates)
    

    def get_horizon(self):
        base = 40
        if self.crop_gone:
            base += 10
        if self.storage_loss:
            base += 15
        if self.novice_mistake:
            base += 15
        return (sum(d['n_servings'] for d in self.task['dishes'])-1) * 35 + base
