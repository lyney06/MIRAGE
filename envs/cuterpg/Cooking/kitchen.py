# kitchen.py

import re
import copy
import random
from collections import defaultdict
from .constant import *
from .utils import singularize, pluralize, ingredient_to_phrase, parse_ingredient_phrase, describe_plate
from pdb import set_trace as st


class Kitchen:
    def __init__(self, character, 
                       task,
                       restaurantItems,
                       num_suites=2, #assume that we have 2 sets of everything
                       novice_mistake=False,
                       ):
        
        self.character = character
        self.cooking_tools = {}
        self.tasks = task
        for i in range(num_suites):
            self.cooking_tools.update({f"{key}_{i}": {'seasonings': []} for key in COOKING_TOOLS})
        needed_methods = defaultdict(int)
        for dish in task["dishes"]:
            for group in ["main_ingredients", "required_ingredients", "optional_ingredients"]:
                ing_group = dish[group]
                for ing_name, prep_list in ing_group.items():
                    for prep in prep_list:
                        for state in prep:
                            # Check if the state is the result of some cooking method
                            for method, result_state in COOKING_METHOD_TO_STATE.items():
                                if result_state == state:
                                    needed_methods[method] += 1

        # Find corresponding tools for the cooking method
        needed_tools = set()
        for tool, methods in COOKING_TOOLS.items():
            if methods in needed_methods:
                needed_tools.add(tool)

        # Initialize all cooking tools
        self.cooking_tools = {}
        for tool in sorted(needed_tools):
            for i in range(num_suites):
                cap = 1
                if tool in ["pan", "oven"]:
                    cap = max(needed_methods[COOKING_TOOLS[tool]], 4)
                if tool == 'cutting_board':
                    # we only have one cutting board
                    self.cooking_tools[f"{tool}"] = {'capacity': cap,
                                                     'ingredients': []}
                else:
                    self.cooking_tools[f"{tool}_{i}"] = {'capacity': cap,
                                                         'seasonings': [],
                                                         'ingredients': []}
                
        self.plates = self.initialize_plates(task)
        self.served_plates = {}

        # Initialize kitchen storage
        self.fridge_ingredients = {}
        self.cabinet_ingredients = {}
        self.ingredients = {}
        self.all_locs = {'fridge': self.fridge_ingredients,
                         'cabinet': self.cabinet_ingredients}

        for ingredient in restaurantItems:
            if isinstance(ingredient, str):
                if ingredient in SEASONINGS:
                    self.put_item_to_loc({f'{ingredient}': {'name': ingredient, 
                                                            'state': ['standard'],
                                                            'serving': 100}})
                else:
                    self.put_item_to_loc({f'raw {ingredient}': {'name': ingredient, 
                                                                'state': ['raw'],
                                                                'serving': 100}})
            elif isinstance(ingredient, tuple):
                ingredient, loss_type, reason, discovered = ingredient
                # precheck_loss can be used at kitchen at the beginning
                # on_demand_loss cannot be used even at the beginning
                if ingredient in SEASONINGS:
                    self.put_item_to_loc({f'{ingredient}': {'name': ingredient, 
                                                            'state': ['standard', loss_type],
                                                            'reason': reason,
                                                            'has_good_copy': (False, 0),
                                                            'serving': 100}})
                else:
                    self.put_item_to_loc({f'raw {ingredient}': {'name': ingredient, 
                                                                'state': ['raw', loss_type],
                                                                'reason': reason,
                                                                'has_good_copy': (False, 0), 
                                                                'serving': 100}})
                

        self.working_tools = {tool: 0 for tool in self.cooking_tools if tool != "cutting_board"}

        self.novice_mistake = novice_mistake
        if self.novice_mistake:
            self.max_novice_mistakes = 1  # At most 1 mistake in one round
            self.mistakes_made = 0
            
        self.seasoning_count = 0
        self.visit_times = 0
        self.storage_loss_info = ''
        
        
    def serve_plate(self, plate):
        if plate in self.served_plates:
            return False, 'This plate is already served.'

        if plate not in self.plates:
            return False, 'This plate does not exist in the kitchen.'

        if not self.plates[plate]:
            return False, 'This plate is empty.'

        self.served_plates[plate] = self.plates[plate]
        del self.plates[plate]
        return True, f'Successfully served {plate}.'


    def discard_item(self, ing, source=None, num=None):
        info = []

        # update serving in storage
        if num is None:
            #  discard everything
             num = self.ingredients[ing]["serving"]

        self.ingredients[ing]["serving"] -= num
        if source is None:
            for loc in ['fridge', 'cabinet']:
                if ing in self.all_locs[loc]:
                    self.all_locs[loc][ing]["serving"] -= num
        else:
            source[ing]["serving"] -= num

        # Clear inventories who has 0 servings
        if self.ingredients[ing]["serving"] <= 0:
            if 'precheck_loss' in self.ingredients[ing]['state']:
                reason = self.ingredients[ing]['reason']
                # specifically for discard_precheck_loss
                info.append((reason, ing))
            else:
                info.append(f'All the {pluralize(ing)} are discarded. ')
            del self.ingredients[ing]

            for loc in ['fridge', 'cabinet']:
                if ing in self.all_locs[loc]:
                    del self.all_locs[loc][ing]

        return info


    def discard_precheck_loss(self):
        # info = []
        merged = defaultdict(list)
        for ing_full_name in list(self.ingredients.keys()):
            if 'precheck_loss' in self.ingredients[ing_full_name]['state']:
                for reason, ing in self.discard_item(ing_full_name):
                    merged[reason].append(ing)

        if merged:
            # Merge info from `merged`
            merged_lines = []
            for template, ings in merged.items():
                if len(ings) == 1:
                    merged_lines.append(template.replace("{ing}", ings[0]))
                elif len(ings) == 2:
                    merged_ings = f"{ings[0]} and {ings[1]}"
                    merged_lines.append(template.replace("{ing}", merged_ings))
                else:
                    merged_ings = ", ".join(ings[:-1]) + f", and {ings[-1]}"
                    merged_lines.append(template.replace("{ing}", merged_ings))
                    
            if merged_lines:
                merged_sentence = "; ".join(merged_lines)
                info = f"Oops! While you were away, {merged_sentence}. "

        else:
            info = ''

        return info

    def initialize_plates(self, 
                          task, 
                          max_plate_limit=10, 
                          default_plate_capacity=10, 
                          ):
        """
        Initialize plates according to the task.
        
        Args:
            task (dict): include list 'dishes', every element has 'n_servings'
            max_plate_limit (int): have such number of plates even the number needed for the task is less
            default_plate_capacity (int): number of ingredients a single plate can hold
        
        Returns:
            dict: {'plate_0': {...}, 'plate_1': {...}, ...}
        """
        total_servings = sum(d['n_servings'] for d in task.get('dishes', []))
        num_plates = max(total_servings, max_plate_limit)

        plates = {}
        for i in range(num_plates):
            plate_id = f"plate_{i}"
            plates[plate_id] = {
                'id': plate_id,
                'ingredients': [],
                'seasonings': [],
                'capacity': default_plate_capacity
            }

        return plates


    def get_ing_from_kitchen(self, ing, loc):
        info = ""
        if self.character.carrying:
            return False, f"You can carry only one item at a time. You're holding 1 serving of {self.character.carrying_info()[0]}."
        
        ing = singularize(ing)
        if ing not in self.ingredients:
            # Check all cooking tools
            found_in_tool = False
            target_state, target_name = parse_ingredient_phrase(ing)
            for tool_name, tool_content in self.cooking_tools.items():
                for item in tool_content.get('ingredients', []):
                    item_name = item.get('name')
                    item_states = item.get('state', [])
                    # if target_name == 'crab' and tool_name == 'pot_0':
                    #     st()

                    if item_name == target_name and set(item_states) == set(target_state):
                        found_in_tool = True
                        break
                    
                if found_in_tool:
                    break
                
            if not found_in_tool:
                info = f"There is no {ing} available in the kitchen or in any tool. The only available ingredients are {list(self.ingredients.keys())}."
                return False, info
            
        else:
            if 'on_demand_loss' in self.ingredients[ing]['state']:
                has_good_copy, good_servings = self.ingredients[ing]['has_good_copy']
                reason, reason_type = self.ingredients[ing]['reason']
                curr_info = reason.format(ing=ing)
                if not has_good_copy:
                    if reason_type == 'empty': # remove this from kitchen
                        self.discard_item(ing)
                    elif reason_type == 'spoiled':
                        for source_dict in [self.ingredients, self.all_locs['fridge'], self.all_locs['cabinet']]:
                            if ing in source_dict:
                                source_dict[f"spoiled, {ing}"] = source_dict.pop(ing)
                    else:
                        assert False, 'invalid storage loss type'
                    
                    curr_info = f"{curr_info}."
                    self.storage_loss_info = curr_info
                    return False, curr_info
                else:
                    if reason_type == 'empty':
                        for source_dict in [self.ingredients, self.all_locs['fridge'], self.all_locs['cabinet']]:
                            if ing in source_dict:
                                # source_dict[ing]['state'].remove('on_demand_loss')
                                source_dict[ing]['state'] = [s for s in source_dict[ing]['state'] if s != 'on_demand_loss']
                                source_dict[ing]['serving'] = source_dict[ing]['has_good_copy'][1]
                                del source_dict[ing]['reason']
                                del source_dict[ing]['has_good_copy']
                    elif reason_type == 'spoiled':
                        for source_dict in [self.ingredients, self.all_locs['fridge'], self.all_locs['cabinet']]:
                            if ing in source_dict:
                                source_dict[f"spoiled, {ing}"] = source_dict.pop(ing)
                                source_dict[f"spoiled, {ing}"]['has_good_copy'] = (False, 0)
                                source_dict[ing] = {'name': source_dict[f"spoiled, {ing}"]['name'],
                                               'state': [x for x in source_dict[f"spoiled, {ing}"]['state'] if x != 'on_demand_loss'],
                                               'serving': good_servings}
                        self.storage_loss_info = f"Some of {curr_info} went bad. Don't worry — there are still good servings."

        source_dict = None
        if loc == 'fridge':
            if ing not in self.fridge_ingredients:
                # return False, f"There is no {ing} available in the fridge."
                # now we don't have the take action, so need to change this
                return False, f"There is no {ing} available in the kitchen."
            source_dict = self.fridge_ingredients
            info = f"You take 1 serving of {ing} out of the fridge."
        elif loc == 'cabinet':
            if ing not in self.cabinet_ingredients:
                # return False, f"There is no {ing} available in the cabinet."
                return False, f"There is no {ing} available in the kitchen."
            source_dict = self.cabinet_ingredients
            info = f"You take 1 serving of {ing} out of the cabinet."
        
        elif loc in self.cooking_tools:
            
            # tool ingredients is a list of dicts, where each dict is an instance of ingredient.
            target_state, target_name = parse_ingredient_phrase(ing)
            matched_idx = None
            for idx, item in enumerate(self.cooking_tools[loc]['ingredients']):
                if item['name'] == target_name and set(item['state']) == set(target_state):
                    matched_idx = idx
                    break

            if matched_idx is None:
                return False, f"There is no {ing} available in {loc}."
            
            # Find the ingredient: take it out from the tool
            selected_item = self.cooking_tools[loc]['ingredients'].pop(matched_idx)
            self.character.carrying = {
                "full_name": ing,
                "name": selected_item["name"],
                "state": selected_item["state"],
                "serving": 1
            }
            return True, f"You take 1 serving of {ing} out of the {loc}."

        else:
            return False, "Wrong action format. You can only take ingredients out of the fridge, cabinet, or a cooking tool."
        # Take one serving out
        if ing in SEASONINGS:
            self.character.carrying = {
                "full_name": ing, #this if the full name
                "name": ing,
                "state": self.ingredients[ing]["state"][:],  # deep copy list
                "serving": 1
            }
        else:
            self.character.carrying = {
                "full_name": ing, #this if the full name
                "name": ing.split(' ')[-1],
                "state": self.ingredients[ing]["state"][:],  # deep copy list
                "serving": 1
            }

        self.discard_item(ing, source_dict, 1)

        return True, info
    
    def put_to_fridge(self, ingredient_dict):
        for key, new_info in ingredient_dict.items():
            if key in self.fridge_ingredients:
                self.fridge_ingredients[key]['serving'] += new_info['serving']
            else:
                self.fridge_ingredients[key] = new_info.copy()

            if key in self.ingredients:
                self.ingredients[key]['serving'] += new_info['serving']
            else:
                self.ingredients[key] = new_info.copy()

    def put_to_cabinet(self, ingredient_dict):
        for key, new_info in ingredient_dict.items():
            if key in self.cabinet_ingredients:
                self.cabinet_ingredients[key]['serving'] += new_info['serving']
            else:
                self.cabinet_ingredients[key] = new_info.copy()

            if key in self.ingredients:
                self.ingredients[key]['serving'] += new_info['serving']
            else:
                self.ingredients[key] = new_info.copy()

    def put_item_to_loc(self, ingredient, loc=None):
        if isinstance(ingredient, str):
            ingredient = singularize(ingredient)
            states, ingredient_name = parse_ingredient_phrase(ingredient)
            full_name = ingredient  # already like "raw cucumber"
            existing_serving = self.ingredients.get(full_name, {}).get('serving', 0)

            new_dict = {
                full_name: {
                    'name': ingredient_name,
                    'state': states,
                    'serving': existing_serving + 1
                }
            }

        # case 2: if it's a dict like {"raw cucumber": {...}}
        elif isinstance(ingredient, dict):
            new_dict = {}
            for full_name, info in ingredient.items(): # this only works for size 1
                if full_name in self.ingredients and 'on_demand_loss' in self.ingredients[full_name]['state']:
                    _, servings = self.ingredients[full_name]['has_good_copy']
                    self.ingredients[full_name]['has_good_copy'] = (True, servings + info['serving'])
                else:
                    new_dict[full_name] = copy.deepcopy(ingredient[full_name])
                    if 'serving' not in info:
                        st()
                    new_dict[full_name]['serving'] = info['serving']
                break
            
        # Assign them into cabinet or fridge
        if not loc:
            full_name = list(ingredient.keys())[0]
            ing_data = ingredient[full_name]
            name = ing_data.get('name', '')
            if name in PLANTABLE_INGREDIENTS+FISHABLE_INGREDIENTS+ADDITIONAL_SEAFOOD+MEATS:
                loc = 'fridge'
            elif name in BASE_SEASONINGS+CABINET_INGREDIENTS+SPECIAL_SEASONINGS:
                loc = 'cabinet'
            else:
                # fridge by default
                loc = 'fridge'

        if loc == 'fridge':
            self.put_to_fridge(new_dict)
        elif loc == 'cabinet':
            self.put_to_cabinet(new_dict)
        return loc

    
    def smart_take(self, full_ing_name):
        if full_ing_name in self.ingredients:
            for location in ['fridge', 'cabinet']:
                action_success, action_info = self.get_ing_from_kitchen(full_ing_name, location)
                if action_success:
                    break
            else:
                if self.storage_loss_info:
                    info = self.storage_loss_info
                    self.storage_loss_info = ''
                    return False, info
                return False, action_info
        else:
            # Check all tools
            for location in sorted(set(self.cooking_tools.keys()) | set(self.plates.keys())):
                # only consider cooked ones
                if location in self.working_tools and self.working_tools[location]:
                    continue
                action_success, action_info = self.get_ing_from_kitchen(full_ing_name, location)
                if action_success:
                    break
            else:
                return False, f'There is no {full_ing_name} in the kitchen.'
        return True, ''
    
    def get_cutting_board_msg(self):
        tool_data = self.cooking_tools["cutting_board"]
        items_on_board = []
        for item in tool_data["ingredients"]:
            items_on_board.append(ingredient_to_phrase(item))
            

        board_summary = "cutting board now holds: " + ", ".join(items_on_board) + "."
        return board_summary
        

    
    def chop_ingredient_with_knife(self, ingredient=None):
        NONCHOPPABLE_INGREDIENTS = {
            "rice", "flour", "milk", "cheese", "cream", "butter", "sour cream",
            "croutons", "spinach", "sesame seeds", "egg", "beans",
            "tortilla", "pea",
            "crab", "lobster", "scallop", "anchovy", "clams", "oyster"
        }
        ingredient = singularize(ingredient)

        cutting_board = self.cooking_tools.get("cutting_board")
        if not cutting_board:
            return False, "Cutting board does not exist."

        board_ingredients = cutting_board.get("ingredients", [])

        # If there's already sth on the cutting_board, you cannot chop sth else.
        if board_ingredients:
            first_item = board_ingredients[0]
            curr_ing = ingredient_to_phrase(first_item)
            if curr_ing != ingredient:
                return False, f"The cutting board already has {curr_ing}, please put it somewhere else."

            # The target is already on the cutting_board.
            if "chopped" in first_item["state"]:
                return False, f"{ingredient.capitalize()} on the cutting board is already chopped."
            
            # Add state 'chopped'.
            first_item["state"].append("chopped")
            first_item["state"] = list(dict.fromkeys(first_item["state"]))
            board_summary = self.get_cutting_board_msg()

            return True, f"You chopped the {pluralize(ingredient)} on the cutting board. {board_summary}"
        
        _, ingredient_name = parse_ingredient_phrase(ingredient)

        if ingredient_name in SEASONINGS or ingredient_name in NONCHOPPABLE_INGREDIENTS:
            return False, f"You can't chop {ingredient_name}."

        action_success, action_info = self.smart_take(ingredient)
        if not action_success:
            return False, action_info

        carrying = self.character.carrying

        if "chopped" in carrying["state"]:
            return False, f"You have already chopped this serving of {ingredient_name}."

        # Put ingredient on the cutting_board, and add 'chopped' state.
        entry = {
            "name": ingredient_name,
            "state": list(dict.fromkeys(carrying["state"] + ["chopped"]))
        }
        cutting_board["ingredients"].append(entry)
        self.character.carrying = {}
        board_summary = self.get_cutting_board_msg()

        msg = f"You chopped the {pluralize(ingredient_name)} on the cutting board. {board_summary}"
        if self.storage_loss_info:
            msg = f'{self.storage_loss_info}\n{msg}'
            self.storage_loss_info = ''
        return True, msg
    
    def maybe_overseason(self):
        if self.mistakes_made < self.max_novice_mistakes:
            if random.random() < 0.5:  # 50% chance of mistake
                self.mistakes_made += 1
                return 2  # duplicate once
            if self.seasoning_count >= 3: # At least one mistake
                self.mistakes_made += 1
                return 2  # duplicate once
        return 1
    
    def undo_take(self):
        # is the put action or chop action fails, we need to undo take
        if self.character.carrying:
            self.put_item_to_loc({self.character.carrying['full_name']: self.character.carrying})
        self.character.carrying = {}
        return
    
    def put_ingredient_in_tool(self, full_ing_name, tool):
        full_ing_name = singularize(full_ing_name)
        valid_locations = ['fridge', 'cabinet'] + list(self.cooking_tools) + list(self.plates)

        if tool not in valid_locations:
            return False, f"{tool} is not a valid location to put the item."
        
        states, ingredient_name = parse_ingredient_phrase(full_ing_name)
        if tool in self.cooking_tools:
            # cutting_board
            tool_data = self.cooking_tools[tool]
            capacity = tool_data['capacity']
            ingredients_in_tool = tool_data['ingredients']
        
            if tool == "cutting_board":
                if len(ingredients_in_tool) >= capacity:
                    return False, f"{tool} is already full."
            else:
                # if tool in self.cooking_tools:
                if ingredient_name not in SEASONINGS:
                    if len(ingredients_in_tool) >= capacity:
                        return False, f"{tool} is already full of ingredients."
                else:
                    if len(tool_data['seasonings']) >= capacity:
                        return False, f"{tool} already has too many seasonings."

        # Get ingredient through smart_take
        full_ing_name = singularize(full_ing_name)
        action_success, action_info = self.smart_take(full_ing_name)
        if not action_success:
            return action_success, action_info

        # Store into fridge / cabinet
        if tool in ['fridge', 'cabinet']:
            self.put_item_to_loc(full_ing_name, tool)
            self.character.carrying = {}
            return True, f'You put {full_ing_name} in {tool}.'
        
        # the followings are a part of cooking
        if full_ing_name in SEASONINGS and self.novice_mistake:
            amount_put = self.maybe_overseason()
        else:
            amount_put = 1
            
        # Put into plate
        if tool in self.plates:
            plate = self.plates[tool]
            if full_ing_name in SEASONINGS:
                self.seasoning_count += 1
                for _ in range(amount_put):
                    if plate["ingredients"] and plate["ingredients"][-1] == []:
                        plate['seasonings'][-1].append(full_ing_name)
                    else:
                        plate["ingredients"].append([])
                        plate['seasonings'].append([full_ing_name])
            else:
                if len(plate["ingredients"]) >= plate["capacity"]:
                    return False, f"{tool} is already full."
                # states, ingredient_name = parse_ingredient_phrase(full_ing_name)
                plate["ingredients"].append([{
                    "name": ingredient_name,
                    "state": states
                }])
                plate['seasonings'].append([])  # Every ingredient group has a seasoning slot

            self.character.carrying = {}
            summary = describe_plate(plate, self.tasks)
            if amount_put == 2:
                return True, f"Oops! You accidentally added an extra serving of {full_ing_name}. You plated 2 servings of {full_ing_name} into {tool}. {summary}"
            return True, f"You plated {full_ing_name} into {tool}. {summary}"

        if tool == "cutting_board":
            # Not processing self.working_tools. Directly add the ingredient to cutting_board.
            tool_data["ingredients"].append({
                "name": ingredient_name,
                "state": states
            })
            self.character.carrying = {}
            return True, f"You placed {full_ing_name} on the cutting board."
        
        
        # Heating tools (including working_tools)
        if ingredient_name not in SEASONINGS:
            # Check full or not
            
            tool_data['ingredients'].append({
                "name": ingredient_name,
                "state": states
            })
        else:
            self.seasoning_count += 1
            for _ in range(amount_put):
                tool_data['seasonings'].append(ingredient_name)

        # Start timing or add to the cooking time
        if self.working_tools[tool] == 0:
            self.working_tools[tool] = 2 if capacity == 1 else 3
            self.working_tools[tool] += 1  # longer cooking time
        else:
            self.working_tools[tool] += 1

        self.character.carrying = {}

        msg = ''
        if amount_put == 2:
            msg = f"Oops! You accidentally added an extra serving of {full_ing_name}."
            full_ing_name = f"2 servings of {full_ing_name}"
        msg += f"You put {full_ing_name} into the {tool}. Please wait for {self.working_tools[tool]-1} timesteps for it to be cooked."
        if self.storage_loss_info:
            msg = f'{self.storage_loss_info}\n{msg}'
            self.storage_loss_info = ''
        return True, msg


    def tick_all_tools(self, return_msg=False):
        """Reduce cooking time of tools at every timestep. If a tool finishes cooking, update the states and return natural language hints."""
        all_messages = []
        cooking_messages = []

        for tool, time_left in self.working_tools.items():
            if time_left > 0:
                self.working_tools[tool] -= 1
                new_time = self.working_tools[tool]

                cooked_method = COOKING_TOOLS[tool.split('_')[0]]
                cooked_state = COOKING_METHOD_TO_STATE[cooked_method]

                if new_time == 0:
                    # Cooking finished. Update state.
                    updated_names = []

                    for entry in self.cooking_tools[tool]['ingredients']:
                        entry['state'] = [s for s in entry['state'] if s != 'raw']
                        if cooked_state not in entry['state']:
                            entry['state'].append(cooked_state)
                        updated_names.append(ingredient_to_phrase(entry))

                    if updated_names:
                        cooked_items = ", ".join(sorted(set(updated_names)))
                        msg = f"{tool} finished cooking your one serving of {cooked_items}."
                        all_messages.append(msg)
                        cooking_messages.append(msg)
                else:
                    msg = f"In {tool}, your dish will be ready in {new_time} timestep(s)."
                    all_messages.append(msg)

        if return_msg:
            return True, " ".join(all_messages) if all_messages else "1 timestep has passed."
        else:
            return True, " ".join(cooking_messages)
        
    def plate_from_tool(self, tool, plate_id):
        if plate_id in self.served_plates:
            return False, "This plate has already been served and can no longer be used."
        if plate_id not in self.plates:
            return False, f"Plate {plate_id} does not exist."
        if tool not in self.cooking_tools:
            return False, f"{tool} is not a valid cooking tool."

        if self.working_tools.get(tool, 0) > 0:
            return False, f"{tool} is still cooking. Wait until the food is ready before plating."

        plate = self.plates[plate_id]
        tool_content = self.cooking_tools[tool]

        ingredients = tool_content.get("ingredients", [])
        if not ingredients:
            return False, f"There is nothing in {tool} to plate."

        if len(plate['ingredients']) + len(ingredients) > plate['capacity']:
            return False, f"Plate {plate_id} doesn't have enough space for all ingredients from {tool}."
        
        plate['ingredients'].append(ingredients)
        plate['seasonings'].append(tool_content.get("seasonings", []))

        # clear tool content
        tool_content['ingredients'] = []
        tool_content['seasonings'] = []

        summary = describe_plate(plate, self.tasks)
        return True, f"You plated all cooked ingredients from {tool} into {plate_id}. {summary}"

    
    def get_kitchen_observation(self):
        observation = []

        # Current location
        observation.append("You are now in the kitchen of your restaurant.")

        # Ingredients in the fridge
        if self.fridge_ingredients:
            fridge_list = [f"{pluralize(name)}" for name in self.fridge_ingredients]
            fridge_line = "In the fridge, you see: " + "; ".join(fridge_list) + "."
        else:
            fridge_line = "The fridge is empty."

        # Ingredients in the cabinet
        if self.cabinet_ingredients:
            cabinet_list = [f"{pluralize(name)}" for name in self.cabinet_ingredients]
            cabinet_line = "In the cabinet, you see: " + "; ".join(cabinet_list) + "."
        else:
            cabinet_line = "The cabinet is empty."

        observation.append(fridge_line)
        observation.append(cabinet_line)

        # Tools
        tool_lines = []
        empty_tool_groups = {}  # key: (capacity, has_seasoning), value: [tool names]
        detailed_tools = []

        for tool_name, tool_data in self.cooking_tools.items():
            ingredients = tool_data.get('ingredients', [])
            seasonings = tool_data.get('seasonings', [])
            capacity = tool_data.get('capacity', 0)
            used = len(ingredients)

            if not ingredients and (tool_name == 'cutting_board' or not seasonings):
                key = (capacity, False)
            elif not ingredients and not seasonings:
                key = (capacity, False)
            else:
                key = None

            if key and used == 0:
                empty_tool_groups.setdefault(key, []).append(tool_name)
            else:
                parts = []

                if ingredients:
                    ing_list = []
                    for entry in ingredients:
                        name = entry["name"]
                        states = entry.get("state", [])
                        state_str = ", ".join(states)
                        ing_list.append(f"{state_str} {pluralize(name)}")
                    parts.append(f"{', '.join(ing_list)}")
                else:
                    parts.append("no ingredients")

                if tool_name != 'cutting_board':
                    if seasonings:
                        parts.append(f"with seasonings: {', '.join(seasonings)}")
                    else:
                        parts.append("no seasonings")

                detailed_tools.append(f"{tool_name} holds {', '.join(parts)}. Capacity: {used}/{capacity}.")

        # Print empty tools
        for (cap, _), tool_list in empty_tool_groups.items():
            names = ", ".join(sorted(tool_list))
            if len(tool_list) == 1:
                tool_lines.append(f"{names} is empty. Capacity: 0/{cap}.")
            elif len(tool_list) == 2:
                tool_lines.append(f"{names} are both empty. Capacity: 0/{cap}.")
            else:
                tool_lines.append(f"{names} are all empty. Capacity: 0/{cap}.")

        # Print tool states
        tool_lines.extend(detailed_tools)

        if tool_lines:
            observation.append(f"There are {len(self.cooking_tools)} cooking tools in the environment:")
            for line in tool_lines:
                observation.append(f"- {line}")
                
        # active_plates = list(self.plates.keys())
        # filled = []
        # empty = []

        # # Classify plates
        # for plate in active_plates:
        #     content = self.plates[plate]
        #     ingredients = content.get('ingredients', [])
        #     if ingredients:
        #         filled.append(plate)
        #     else:
        #         empty.append(plate)

        # # Build messages
        # # served = self.served_plates
        # # if served:
        # #     parts.append(f"{', '.join(served)} {'is' if len(served)==1 else 'are'} served and not usable now.")

        # for plate in filled:
        #     desc = describe_plate(self.plates[plate], self.tasks)
        #     observation.append(f"{plate} contains {desc}")

        # if empty:
        #     observation.append(f"{', '.join(empty)} {'is' if len(empty)==1 else 'are'} empty.")

        return re.sub(r'\n{2,}', '\n', "\n".join(observation).strip())


    def print_kitchen_storage(self):
        # For debugging
        def color_text(text, color_code):
            return f"\033[{color_code}m{text}\033[0m"
        
        print_fridge = False
        print_cabinet = False
        print_storage = False
        print_tools = False 
        print_plate = False

        # Fridge
        if print_fridge:
            print(color_text("===== 🧊 Fridge Ingredients =====", "96"))  # Light Cyan
            if self.fridge_ingredients:
                for name, details in self.fridge_ingredients.items():
                    state = ", ".join(details.get("state", []))
                    serving = details.get("serving", 0)
                    print(f"  - {color_text(name, '94')} ({state}) — {serving} serving(s)")
            else:
                print("  (empty)")

        # Cabinet
        if print_cabinet:
            print(color_text("\n===== 🧺 Cabinet Ingredients =====", "93"))  # Yellow
            if self.cabinet_ingredients:
                for name, details in self.cabinet_ingredients.items():
                    state = ", ".join(details.get("state", []))
                    serving = details.get("serving", 0)
                    print(f"  - {color_text(name, '33')} ({state}) — {serving} serving(s)")
            else:
                print("  (empty)")

        # All ingredients
        if print_storage:
            print(color_text("\n===== 🍽️ All Ingredients (Global View) =====", "92"))  # Light Green
            if self.ingredients:
                for name, details in self.ingredients.items():
                    state = ", ".join(details.get("state", []))
                    serving = details.get("serving", 0)
                    print(f"  - {color_text(name, '32')} ({state}) — {serving} serving(s)")
            else:
                print("  (empty)")

        # State of every cooking_tool
        if print_tools:
            print(color_text("\n===== 🔥 Cooking Tools =====", "95"))  # Light Magenta
            if self.cooking_tools:
                for tool, content in self.cooking_tools.items():
                    print(color_text(f"\n🔧 {tool} (capacity: {content['capacity']})", "95"))
                    ingredients = content.get('ingredients', [])
                    if ingredients:
                        for ing in ingredients:
                            name = ing['name']
                            states = ", ".join(ing['state'])
                            print(f"  - Ingredient: {color_text(name, '35')} ({states})")
                    else:
                        print("  - No ingredients inside.")

                    seasonings = content.get('seasonings', [])
                    if seasonings:
                        print(f"  - Seasonings: {', '.join(seasonings)}")
                    else:
                        print("  - No seasonings added.")

                    remaining = self.working_tools.get(tool, 0)
                    if remaining > 0:
                        print(f"  - Cooking... {remaining} timestep(s) remaining")
                    else:
                        print("  - Not currently cooking.")
            else:
                print("  (no tools initialized)")

        if print_plate:
            print(color_text("\n===== 🥘 Plates =====", "95"))  # Light Magenta
            if self.plates:
                for tool, content in self.plates.items():
                    print(color_text(f"\n🔧 {tool} (capacity: {content['capacity']})", "95"))
                    ingredients = content.get('ingredients', [])
                    if ingredients:
                        for ing in ingredients:
                            name = ing['name']
                            states = ", ".join(ing['state'])
                            print(f"  - Ingredient: {color_text(name, '35')} ({states})")
                    else:
                        print("  - No ingredients inside.")

                    seasonings = content.get('seasonings', [])
                    if seasonings:
                        print(f"  - Seasonings: {', '.join(seasonings)}")
                    else:
                        print("  - No seasonings added.")

                    remaining = self.working_tools.get(tool, 0)
                    if remaining > 0:
                        print(f"  - Cooking... {remaining} timestep(s) remaining")
                    else:
                        print("  - Not currently cooking.")
            else:
                print("  (no tools initialized)")