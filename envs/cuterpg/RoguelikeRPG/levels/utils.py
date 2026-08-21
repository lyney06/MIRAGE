import random
from typing import List, Dict, Any, Tuple, Optional, Set
from envs.cuterpg.RoguelikeRPG.levels.crafting_level import CraftingLevel
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.item import Item, Material, create_material
from envs.cuterpg.RoguelikeRPG.constants import Element, BASE_MATERIALS
from envs.cuterpg.RoguelikeRPG.systems.crafting import CraftingSystem
from pdb import set_trace as st


def add_item(item_name, 
             collectibles, 
             theme='forest',
             display_name=''):
    key_name = item_name
    idx = 1
    while key_name in collectibles:
        key_name = f"{item_name}_{idx}"
        idx += 1

    if item_name in BASE_MATERIALS:
        element = BASE_MATERIALS[item_name]
        description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        item = create_material(item_name, description, element)
        if display_name:
            item.display_name = display_name
        
        # Add to collectibles with a description of where it is
        locations = [
            f"on the ground",
            f"partially hidden under some debris",
            f"glowing faintly in a corner",
            f"tucked away in a crevice",
            f"just lying there in plain sight"
        ]
        collectibles[key_name] = {
            "description": f"You see a {display_name or item_name} {random.choice(locations)}.",
            "item": item
        }
    else:
        # It's a themed collectible
        description = f"A {item_name} from the {theme}."
        
        # Randomly determine if it's a crafting material
        if random.random() < 0.3:  # 30% chance to be a material
            element = random.choice(list(Element) + [None])
            item = create_material(item_name, description, element)
        else:
            # Just a flavorful item with no game mechanic value
            item = create_material(item_name, description)
        
        if display_name:
            item.display_name = display_name
            
        collectibles[key_name] = {
            "description": f"You notice a {display_name or item_name} partially hidden in the environment.",
            "item": item
        }