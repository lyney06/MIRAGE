"""
Inventory system for the RougelikeRPG game.
"""
from .inventory import Inventory
from collections import defaultdict
from envs.cuterpg.RoguelikeRPG.constants import CRAFTING_RECIPES, ITEM_INFO_MAP, STANDARD_WEAPONS, ADVANCED_WEAPONS
from envs.cuterpg.RoguelikeRPG.entities.item import create_material, create_weapon
from .crafting import CraftingSystem
from pdb import set_trace as st

class VirtualInventory(Inventory):
    """
    Manages the player's inventory, including items, weapons, and materials.
    Handles weight constraints and item organization.
    """
    
    def __init__(self, capacity):
        super().__init__(capacity)
    
    def can_add(self, item_weight: int):
        return self.current_weight + item_weight <= self.capacity
    
    def breakdown(self):
        """
        Break down all craftable items into their base components.
        NOTE: We assume no loops in recipes.
        """
        # Keep trying to break down until nothing left can be broken
        changed = True
        while changed:
            changed = False
            for item in self.items:
                if item.name in CRAFTING_RECIPES:
                    for _ in range(item.count):
                        # Remove 1 crafted item
                        self.remove_item(item.name, 1)
                        # print(f'break down {item.name}')

                        # Add back its components
                        for sub_item, qty in CRAFTING_RECIPES[item.name]:
                            for _ in range(qty):
                                self.add_item(self.name_to_item(sub_item))
                    changed = True
    
    def try_all_possible_crafts(self, allowed_recipes=None):
        """
        Try crafting all possible items until no more can be crafted.
        If allowed_recipes is specified, only craft recipes present in allowed_recipes.
        Do not craft duplicate copies of the same recipe item when 1 already exists.
        """
        crafted = True
        while crafted:
            crafted = False
            for result_item in CRAFTING_RECIPES:
                if allowed_recipes is not None and result_item not in allowed_recipes:
                    continue
                existing = [i for i in self.items if i.name == result_item]
                if existing and existing[0].count >= 1:
                    continue
                if self.can_craft(result_item):
                    self.craft(result_item)
                    crafted = True

                    
    def can_craft(self, result_item: str) -> bool:
        if result_item not in CRAFTING_RECIPES:
            return False

        inventory_counts = defaultdict(int)
        for item in self.items:
            inventory_counts[item.name] += item.count

        for sub_item, qty in CRAFTING_RECIPES[result_item]:
            if inventory_counts[sub_item] < qty:
                return False

        return True

    def craft(self, result_item):
        """Consume components and add result item"""
        if not self.can_craft(result_item):
            return False

        for sub_item, qty in CRAFTING_RECIPES[result_item]:
            for _ in range(qty):
                self.remove_item(sub_item, 1)
                
        item = self.get_item_by_name(result_item) or self.name_to_item(result_item)
        self.add_item(item)
        # print(f'crafted {item.name}')
        # print([(x.name, x.count) for x in self.items])
        
        
    def name_to_item(self, item_name):
        if item_name.endswith('Enhancer'):
            item = create_material(item_name, '')
        elif item_name in CRAFTING_RECIPES:
            # info = ITEM_INFO_MAP[item_name]
            # item = create_weapon(item_name, description='', tier=info['tier'], element=info['element'])
            item = CraftingSystem._create_item_from_recipe(item_name)
        else:
            item = create_material(item_name, '')
        return item
    

    def get_all_weapons(self):
        res = []
        for item in self.items:
            if item.name in list(STANDARD_WEAPONS.keys()) + list(ADVANCED_WEAPONS.keys()):
                res.append(item)
        return res
