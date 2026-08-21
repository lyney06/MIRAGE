import random
from collections import defaultdict
from envs.cuterpg.RoguelikeRPG.constants import STANDARD_WEAPONS, ADVANCED_WEAPONS, CRAFTING_RECIPES
from pdb import set_trace as st

def expand_crafting_tree(target_item: str):
    """
    Expand only the base materials (non-craftable) needed to craft a target item.

    Args:
        target_item (str): Final item to be crafted
        recipes (dict): Crafting recipe dictionary

    Returns:
        Dict[str, int]: Base material name -> required count
    """
    required = defaultdict(int)

    def recurse(item_name: str, multiplier: int):
        if item_name in CRAFTING_RECIPES:
            for sub_item, qty in CRAFTING_RECIPES[item_name]:
                recurse(sub_item, qty * multiplier)
        else:
            required[item_name] += multiplier

    recurse(target_item, 1)
    return dict(required)




def _get_item_key(item):
    if item is None:
        return None
    if isinstance(item, str):
        return item
    if hasattr(item, "name"):
        return item.name
    return item


def derangement(original_list):
    """Return a random derangement (no item stays in its original slot).

    Attempts a value-based derangement first (no item of the same name/type in the same slot).
    Falls back to slot-index-based derangement, and finally simple shuffle.
    """
    if len(original_list) <= 1:
        return list(original_list)
        
    tagged = [(item, i) for i, item in enumerate(original_list)]
    keys = [_get_item_key(item) for item in original_list]
    
    # 1. Try value-based derangement
    for _ in range(100):
        shuffled = tagged[:]
        random.shuffle(shuffled)
        if all(_get_item_key(shuffled[i][0]) != keys[i] for i in range(len(original_list))):
            return [item for item, _ in shuffled]
            
    # 2. Try slot-index-based derangement
    for _ in range(100):
        shuffled = tagged[:]
        random.shuffle(shuffled)
        if all(o[1] != s[1] for o, s in zip(tagged, shuffled)):
            return [item for item, _ in shuffled]
            
    # 3. Simple random shuffle fallback
    shuffled = list(original_list)
    random.shuffle(shuffled)
    return shuffled