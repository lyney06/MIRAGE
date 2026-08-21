"""
Solution manager to ensure games are solvable with guaranteed paths to defeat bosses.
"""
import random
import copy
from collections import defaultdict
from typing import List
from envs.cuterpg.RoguelikeRPG.constants import Element, BASE_MATERIALS
from envs.cuterpg.RoguelikeRPG.entities.boss import Boss
from envs.cuterpg.RoguelikeRPG.entities.item import create_material
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.levels.growth_level import GrowthLevel
from envs.cuterpg.RoguelikeRPG.levels.combat_level import CombatLevel
from envs.cuterpg.RoguelikeRPG.levels.shop_level import ShopLevel
from envs.cuterpg.RoguelikeRPG.constants import ITEM_WEIGHT_MAP, ADVANCED_WEAPONS, CRAFTING_RECIPES
from ..systems.virtual_inventory import VirtualInventory


class UnsolvableGameError(RuntimeError):
    """Raised when required items cannot be placed in the generated layout."""

    pass


class SolutionManager:
    """
    Manages the solution path for the game, ensuring that players can
    obtain the necessary items to defeat bosses.
    """
    
    def __init__(self, 
                 levels: List[Level], 
                 boss_element: Element,
                 inventory):
        """
        Initialize the solution manager.
        
        Args:
            levels: The list of game levels
            boss_element: The primary element of the final boss
        """
        self.levels = levels
        self.boss_element = boss_element
        self.inventory = inventory
        self.solution_element = None
        self.required_items = {}
        self.shop_items = []
        
        # Determine the solution path
        self._determine_solution_path()
    
    def _determine_solution_path(self):
        """
        Determine an optimal solution path to defeat the boss.
        """
        # Get elements that are effective against the boss
        counter_elements = Boss.get_weakness_elements(self.boss_element)
        
        # Choose one counter element as the primary solution path
        if counter_elements:
            self.solution_element = random.choice(sorted(counter_elements, key=lambda e: e.name))
        else:
            # If no direct counters, choose a random element that isn't the boss element
            all_elements = [e for e in Element if e != self.boss_element]
            self.solution_element = random.choice(all_elements)
            
        # Determine the element material name for the solution element
        element_material_name = None
        for name, element in BASE_MATERIALS.items():
            if element == self.solution_element:
                element_material_name = name
                break
        
        if not element_material_name:
            # Fallback if element material not found
            element_material_name = f"{self.solution_element.name} Essence"

        self.expected_weapons = [[] for _ in range(len(self.levels))]
        self.expected_inv = [[] for _ in range(len(self.levels))]
        self.remaining_capcities = [0 for _ in range(len(self.levels))]

        self.recommended_weapon = self.get_recommended_weapon()

        # Define the required items for the solution
        self.required_items = {
            # Basic materials needed (3 of the solution element - 1 for weapon, 2 for enhancer)
            element_material_name: 3,
            "Weapon Prototype": 1,
            "Magic Catalyst": 1,
            "Enchanted Cloth": 1
        }

    def distribute_required_items(self):
        """
        Distribute required items into levels with inventory capacity constraint,
        allowing backtracking if no valid distribution is found.
        """
        print_info = True
        
        # Step 1: Start with a copy of required items
        needed_items = copy.deepcopy(self.required_items)
        virtual_inventory = VirtualInventory(capacity=self.inventory.capacity)

        # Step 2: Fill virtual_inventory with all existing items from inventory
        for item in self.inventory.items:
            virtual_inventory.add_item(copy.deepcopy(item))
            if item.name in needed_items:
                required_count = needed_items[item.name]
                add_count = min(item.count, required_count)
                needed_items[item.name] -= add_count
                if needed_items[item.name] == 0:
                    del needed_items[item.name]

        # Step 3: Account for required items already generated in levels
        self.pre_existing_collected = defaultdict(list)
        self.extra_shop_placed = defaultdict(list)
        for level in self.levels[:-1]:
            level_items = []
            if hasattr(level, "collectibles"):
                for name, info in level.collectibles.items():
                    item = info.get("item")
                    if item is not None and item.name in needed_items:
                        level_items.append(item.name)
            if hasattr(level, "containers"):
                for info in level.containers.values():
                    item = info.get("item")
                    if item is not None and item.name in needed_items:
                        level_items.append(item.name)
            enemies_to_check = []
            if hasattr(level, "enemies") and level.enemies:
                enemies_to_check.extend(level.enemies)
            if hasattr(level, "enemy") and level.enemy:
                enemies_to_check.append(level.enemy)
            for enemy in enemies_to_check:
                for drop in getattr(enemy, "drops", []):
                    drop_name = drop if isinstance(drop, str) else getattr(drop, "name", "")
                    if drop_name in needed_items:
                        level_items.append(drop_name)
            if hasattr(level, "for_sale"):
                for name in level.for_sale:
                    if name in needed_items:
                        level_items.append(name)

            for item_name in level_items:
                if item_name not in needed_items or needed_items[item_name] <= 0:
                    continue
                weight = ITEM_WEIGHT_MAP.get(item_name, 0)
                if weight and not virtual_inventory.can_add(weight):
                    continue
                needed_items[item_name] -= 1
                self.pre_existing_collected[level].append(item_name)

                # If the item is pre-existing in a shop, ensure its price items are handled
                if level.level_type == "shop":
                    shop_idx = self.levels.index(level)
                    valid_levels = [lvl for lvl in self.levels[:shop_idx] if lvl.level_type in ["growth", "combat"]]
                    
                    item_info = level.for_sale.get(item_name, {})
                    price_list = item_info.get("price", [])
                    
                    # Ensure shop prices never demand items required for the solution crafting chain
                    sanitized_price = []
                    for p_name, p_count in price_list:
                        if p_name in self.required_items or p_name == item_name:
                            sanitized_price.append(("coin", 1))
                        else:
                            sanitized_price.append((p_name, p_count))
                    
                    if item_name in level.for_sale:
                        level.for_sale[item_name]["price"] = sanitized_price
                    price_list = sanitized_price
                    for price_item_name, price_count in price_list:
                        # Find existing instances of price_item_name in levels before the shop
                        found_instances = []
                        for lvl in valid_levels:
                            # Check collectibles
                            if hasattr(lvl, 'collectibles'):
                                for name, info in lvl.collectibles.items():
                                    item = info.get("item")
                                    if item is not None and item.name == price_item_name:
                                        found_instances.append(lvl)
                            # Check containers
                            if hasattr(lvl, 'containers'):
                                for container_info in lvl.containers.values():
                                    item = container_info.get("item")
                                    if item is not None and item.name == price_item_name:
                                        found_instances.append(lvl)
                            # Check enemy drops
                            lvl_enemies = []
                            if hasattr(lvl, 'enemies') and lvl.enemies:
                                lvl_enemies.extend(lvl.enemies)
                            if hasattr(lvl, 'enemy') and lvl.enemy:
                                lvl_enemies.append(lvl.enemy)
                            for enemy in lvl_enemies:
                                for drop in getattr(enemy, "drops", []):
                                    drop_name = drop if isinstance(drop, str) else getattr(drop, "name", "")
                                    if drop_name == price_item_name:
                                        found_instances.append(lvl)
                        
                        # Use existing instances that are NOT reserved for required crafting materials or previous shop items
                        already_used = sum(1 for p_item, p_lvl in self.shop_items if p_item == price_item_name and p_lvl in found_instances)
                        needed_for_crafting = self.required_items.get(price_item_name, 0)
                        unreserved_count = max(0, len(found_instances) - needed_for_crafting - already_used)
                        use_count = min(unreserved_count, price_count)
                        unclaimed = [inst for inst in found_instances]
                        for p_item, p_lvl in self.shop_items:
                            if p_item == price_item_name and p_lvl in unclaimed:
                                unclaimed.remove(p_lvl)
                        for i in range(use_count):
                            if i < len(unclaimed):
                                self.shop_items.append((price_item_name, unclaimed[i]))
                        
                        # If we still need more, place them in valid levels as extra shop items
                        missing_count = price_count - use_count
                        if missing_count > 0:
                            if item_name in level.for_sale:
                                level.for_sale[item_name]["price"] = [("coin", 1)]

                if needed_items[item_name] == 0:
                    del needed_items[item_name]
                    
        placed = defaultdict(list)
        remaining = copy.deepcopy(needed_items)
            
        def backtrack(level_idx, placed, inv, remaining, trace):
            if level_idx < len(self.levels):
                self.expected_weapons[level_idx] = inv.get_all_weapons()
                self.expected_inv[level_idx] = copy.deepcopy(inv.items)
                self.remaining_capcities[level_idx] = inv.remaining_capacity
            if all(v <= 0 for v in remaining.values()):
                for future_idx in range(level_idx, len(self.levels)):
                    self.expected_weapons[future_idx] = inv.get_all_weapons()
                    self.expected_inv[future_idx] = copy.deepcopy(inv.items)
                    self.remaining_capcities[future_idx] = inv.remaining_capacity
                return True, "success"
            if level_idx >= len(self.levels):
                return False, {
                    "reason": "Ran out of levels before placing all required items.",
                    "level_idx": level_idx,
                    "remaining": {k: v for k, v in remaining.items() if v > 0},
                    "trace": trace,
                    "inventory": [f"{item.name} x{item.count}" for item in inv.items],
                    "remaining_capacity": inv.remaining_capacity,
                    "capacity": inv.capacity,
                }
            usable_left = sum(1 for level in self.levels[level_idx:] if level.level_type in ["growth", "combat", "shop"])
            items_left = sum(v for v in remaining.values() if v > 0)
            if usable_left < items_left:
                return False, {
                    "reason": f"Not enough usable levels left. usable_left={usable_left}, items_left={items_left}",
                    "level_idx": level_idx,
                    "remaining": {k: v for k, v in remaining.items() if v > 0},
                    "trace": trace,
                    "inventory": [f"{item.name} x{item.count}" for item in inv.items],
                    "remaining_capacity": inv.remaining_capacity,
                    "capacity": inv.capacity,
                }
            level = self.levels[level_idx]
            last_failure = None
            if level.level_type in ["growth", "combat", "shop"]:
                candidates = [item_name for item_name, count in remaining.items() if count > 0]
                candidates = sorted(candidates, key=lambda item_name: ITEM_WEIGHT_MAP.get(item_name, 0), reverse=True)
                for item_name in candidates:
                    weight = ITEM_WEIGHT_MAP.get(item_name)
                    if weight is None:
                        last_failure = {
                            "reason": f"Missing item weight for {item_name}.",
                            "level_idx": level_idx,
                            "remaining": {k: v for k, v in remaining.items() if v > 0},
                            "trace": trace + [(level_idx, item_name, "missing_weight")],
                            "inventory": [f"{item.name} x{item.count}" for item in inv.items],
                            "remaining_capacity": inv.remaining_capacity,
                            "capacity": inv.capacity,
                        }
                        continue
                    if not inv.can_add(weight):
                        last_failure = {
                            "reason": f"Capacity blocked. Cannot add {item_name} with weight {weight}.",
                            "level_idx": level_idx,
                            "remaining": {k: v for k, v in remaining.items() if v > 0},
                            "trace": trace + [(level_idx, item_name, "capacity_blocked")],
                            "inventory": [f"{item.name} x{item.count}" for item in inv.items],
                            "remaining_capacity": inv.remaining_capacity,
                            "capacity": inv.capacity,
                        }
                        continue
                    new_inv = copy.deepcopy(inv)
                    new_placed = defaultdict(list)
                    for existing_level, items in placed.items():
                        new_placed[existing_level] = items.copy()
                    new_remaining = copy.deepcopy(remaining)
                    new_inv.add_item(create_material(item_name, ""))
                    new_inv.try_all_possible_crafts(self.get_solution_crafting_recipes())
                    new_placed[level].append(item_name)
                    new_remaining[item_name] -= 1
                    self.expected_weapons[level_idx] = new_inv.get_all_weapons()
                    self.expected_inv[level_idx] = copy.deepcopy(new_inv.items)
                    self.remaining_capcities[level_idx] = new_inv.remaining_capacity
                    ok, result = backtrack(level_idx + 1, new_placed, new_inv, new_remaining, trace + [(level_idx, item_name, "placed")])
                    if ok:
                        placed.clear()
                        placed.update(new_placed)
                        return True, result
                    last_failure = result
            ok, result = backtrack(level_idx + 1, placed, inv, remaining, trace + [(level_idx, "SKIP", "skipped")])
            if ok:
                return True, result
            return False, last_failure or result
        
        found, reason = backtrack(
                0,
                placed,
                virtual_inventory,
                remaining,
                [])
        # self.expected_weapons[-1] = self.expected_weapons[-2]
        # however this is weapon after, not weapon before...
        # as we can't collect items in the combat level, we should consider something before this
        self.expected_weapons.insert(0, [])
        # self.expected_weapons = self.expected_weapons[:-1]
        self.remaining_capcities[-1] = self.remaining_capcities[-2]
        if not found:
            raise UnsolvableGameError(
                "SolutionManager.distribute_required_items: backtrack failed "
                "to find a valid placement for required items "
                f"({dict(self.required_items)}) given inventory capacity "
                f"{self.inventory.capacity}. Reason: {reason}"
            )
            
        self.required_placed = placed

        # Step 4: Commit placement
        for level, items in placed.items():
            for item_name in items:
                if level.level_type == "growth":
                    self._add_item_to_growth_level(level, item_name)
                elif level.level_type == "combat":
                    self._add_item_to_combat_level(level, item_name)
                elif level.level_type == "shop":
                    self._add_item_to_shop_level(level, item_name)

        self.full_required_items = set(self.required_items.keys())
        self._add_complementary_elements(print_info=print_info)

        if print_info:
            print("[Distribution] Final item (only required ones) placement:")
            for level, items in placed.items():
                print(f"  - Level {self.levels.index(level)+1} ({level.level_type}): {items}")

        return self.solution_element

    
    def _count_items_in_levels(self):
        """Count required items already present in procedurally generated levels."""
        counts = defaultdict(int)
        for level in self.levels[:-1]:
            if hasattr(level, "collectibles"):
                for info in level.collectibles.values():
                    item = info.get("item")
                    if item is not None and item.name in self.required_items:
                        counts[item.name] += 1
            if hasattr(level, "containers"):
                for info in level.containers.values():
                    item = info.get("item")
                    if item is not None and item.name in self.required_items:
                        counts[item.name] += 1
            enemies_to_check = []
            if hasattr(level, "enemies") and level.enemies:
                enemies_to_check.extend(level.enemies)
            if hasattr(level, "enemy") and level.enemy:
                enemies_to_check.append(level.enemy)
            for enemy in enemies_to_check:
                for drop in getattr(enemy, "drops", []):
                    drop_name = drop if isinstance(drop, str) else getattr(drop, "name", "")
                    if drop_name in self.required_items:
                        counts[drop_name] += 1
            if hasattr(level, "for_sale"):
                for name in level.for_sale:
                    if name in self.required_items:
                        counts[name] += 1
        return counts

    def _item_exists_in_growth_level(self, level: GrowthLevel, item_name: str) -> bool:
        if item_name in level.collectibles:
            return True
        return any(
            info.get("item") is not None and info["item"].name == item_name
            for info in level.containers.values()
        )

    def _add_item_to_growth_level(self, level: GrowthLevel, item_name: str):
        """
        Add an item to a growth level.
        
        Args:
            level: The growth level to add the item to
            item_name: The name of the item to add
        """
        if item_name in BASE_MATERIALS:
            element = BASE_MATERIALS[item_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        else:
            description = "A universal crafting material used in many recipes."
        
        item = create_material(item_name, description)
        
        # Ensure unique key name in level.collectibles
        key_name = item_name
        idx = 1
        while key_name in level.collectibles:
            key_name = f"{item_name}_{idx}"
            idx += 1

        # Determine if it should be a collectible or in a container
        if random.random() < 0.6:
            level.collectibles[key_name] = {
                "description": f"You see a {item_name} on the ground that seems important.",
                "item": item
            }
            level.interactions[key_name] = level.collectibles[key_name]
        else:
            # Create or select a container
            container_names = ["treasure chest", "wooden crate", "mysterious box", "ancient container"]
            available_containers = [c for c in container_names if c not in level.containers]
            if available_containers:
                container_name = random.choice(available_containers)
                level.containers[container_name] = {
                    "description": f"There's a {container_name} that might contain something useful.",
                    "opened": False,
                    "content_description": f"You found a {item_name} inside!",
                    "item": item
                }
                level.interactions[container_name] = level.containers[container_name]
            else:
                level.collectibles[key_name] = {
                    "description": f"You notice a {item_name} partially hidden in the environment.",
                    "item": item
                }
                level.interactions[key_name] = level.collectibles[key_name]
    
    def _add_item_to_combat_level(self, level: CombatLevel, item_name: str):
        """
        Add an item to a combat level's enemy drops.
        
        Args:
            level: The combat level to add the item to
            item_name: The name of the item to add
        """
        if not level.enemies:
            return
        
        # Create the item
        if item_name in BASE_MATERIALS:
            element = BASE_MATERIALS[item_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        else:
            description = "A universal crafting material used in many recipes."
        
        item = create_material(item_name, description)
        
        # Add to enemy drops (prefer enemy that doesn't already drop it)
        eligible_enemies = [
            enemy for enemy in level.enemies
            if not any(
                (drop if isinstance(drop, str) else drop.name) == item_name
                for drop in enemy.drops
            )
        ]
        if not eligible_enemies:
            eligible_enemies = level.enemies
        enemy = random.choice(eligible_enemies)
        enemy.drops.append(item)

    def find_valid_range_to_shop(self, 
                                 shop_idx=-2,
                                 min_capacity: int = 2):
        if len(self.remaining_capcities) < 2:
            return None

        abs_shop_idx = len(self.remaining_capcities) + shop_idx if shop_idx < 0 else shop_idx

        start_idx = abs_shop_idx
        while start_idx >= 0 and self.remaining_capcities[start_idx] >= min_capacity:
            start_idx -= 1

        # If we never found a valid entry
        if start_idx == abs_shop_idx:
            return None

        return (start_idx + 1, abs_shop_idx)
    
    def _add_item_to_shop_level(self, level: ShopLevel, item_name: str):
        # these only include the must-buys 
        """
        Add an item to a shop level's inventory.
        
        Args:
            level: The shop level to add the item to
            item_name: The name of the item to add
        """
        # Create the item
        if item_name in BASE_MATERIALS:
            element = BASE_MATERIALS[item_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        else:
            description = "A universal crafting material used in many recipes."
        
        item = create_material(item_name, description)
        
        # Set a reasonable price (trade requirements)
        # Make sure it's something different than the item itself
        
        if item_name in self.required_items:
            valid_range = self.find_valid_range_to_shop()
            if valid_range is None:
                price_item = 'coin'
                source_level = None  # No layer info
            else:
                all_items = []
                item_sources = []
                for idx, l in enumerate(self.levels[valid_range[0]:-2]):
                    level_index = valid_range[0] + idx
                    items = l.get_available_item_names()
                    items = [x for x in items if x not in self.required_items and x != item_name]

                    allocated = [shop_item for shop_item, lvl in self.shop_items if lvl == l]
                    allocated.extend(self.pre_existing_collected.get(l, []))
                    unallocated_items = []
                    for avail_item in items:
                        if avail_item in allocated:
                            allocated.remove(avail_item)
                        else:
                            unallocated_items.append(avail_item)
                    items = unallocated_items

                    all_items.extend(items)
                    item_sources.extend([level_index] * len(items))
                
                if all_items:
                    chosen_index = random.randrange(len(all_items))
                    price_item = all_items[chosen_index]
                    source_level = self.levels[item_sources[chosen_index]]
                else:
                    price_item = 'coin'
                    source_level = None
                
                self.shop_items.append((price_item, source_level))

        else:
            all_materials = [name for name in BASE_MATERIALS.keys() if name != item_name]
            if not all_materials:  # Safety check
                all_materials = [m for m in ["Weapon Prototype", "Magic Catalyst", "Enchanted Cloth"] if m != item_name]
            
            price_item = random.choice(all_materials)

        price = [(price_item, 1)]
        
        # Add to shop inventory
        level.for_sale[item_name] = {
            "item": item,
            "price": price,
            "description": f"A {item_name} that seems useful for crafting."
        }
    
    def _add_complementary_elements(self, print_info):
        materials_to_consider = {
            name: element
            for name, element in BASE_MATERIALS.items()
            if element is not None
        }

        used_items = set()

        for level in self.levels:
            if level == self.levels[-1]:
                continue

            if level.level_type in ["growth", "combat", "shop"]:
                num_items = random.randint(1, 2)

                if level.level_type == "combat":
                    num_items = level.enemy_num

                sample_pool = {
                    name: element
                    for name, element in materials_to_consider.items()
                    if name not in self.full_required_items
                    and name not in used_items
                }

                if not sample_pool:
                    continue

                selected_items = random.sample(
                    list(sample_pool.items()),
                    k=min(num_items, len(sample_pool))
                )

                for element_material_name, complementary_element in selected_items:
                    used_items.add(element_material_name)

                    if level.level_type == "growth":
                        self._add_complementary_to_growth(
                            level, element_material_name, complementary_element
                        )
                    elif level.level_type == "combat":
                        self._add_complementary_to_combat(
                            level, element_material_name, complementary_element
                        )
                    elif level.level_type == "shop":
                        self._add_complementary_to_shop(
                            level, element_material_name, complementary_element
                        )

                    if print_info:
                        print(
                            f"[Info] Added {element_material_name} "
                            f"({complementary_element.name}) to {level.level_type} level."
                        )
        
      
    def _add_complementary_to_growth(self, level: GrowthLevel, item_name: str, element: Element):
        """Add a complementary element item to a growth level."""
        # Check if the item already exists in the level
        if item_name in level.collectibles or any(c.get("item") and c.get("item").name == item_name for c in level.containers.values()):
            return
        
        description = f"A basic crafting material with {element.value} elemental properties."
        item = create_material(item_name, description, element)
        
        # Either add as collectible or in container
        if random.random() < 0.7:
            level.collectibles[item_name] = {
                "description": f"You see a {item_name} that might be useful.",
                "item": item
            }
            level.interactions[item_name] = level.collectibles[item_name]
        else:
            container_names = ["small pouch", "hidden cache", "natural formation", "abandoned pack"]
            container_name = random.choice(container_names)
            
            if container_name not in level.containers:
                level.containers[container_name] = {
                    "description": f"There's a {container_name} that might contain something.",
                    "opened": False,
                    "content_description": f"You found a {item_name} inside!",
                    "item": item
                }
                level.interactions[container_name] = level.containers[container_name]
    
    def _add_complementary_to_combat(self, level: CombatLevel, item_name: str, element: Element):
        """Add a complementary element item to a combat level's enemy drops."""
        if not level.enemies:
            return
            
        enemy = random.choice(level.enemies)
        # Check if the enemy already drops this item
        if any(drop.name == item_name for drop in enemy.drops if not isinstance(drop, str)):
            return
            
        description = f"A basic crafting material with {element.value} elemental properties."
        item = create_material(item_name, description, element)
        
        # Only add if the enemy doesn't already have too many drops
        if len(enemy.drops) < 3:
            enemy.drops.append(item)
    
    def _add_complementary_to_shop(self, level: ShopLevel, item_name: str, element: Element):
        """Add a complementary element item to a shop level's inventory."""
        # Check if the item is already in the shop
        if item_name in level.for_sale:
            return
            
        description = f"A basic crafting material with {element.value} elemental properties."
        item = create_material(item_name, description, element)
        
        # Set price
        all_materials = list(BASE_MATERIALS.keys())
        price_item = random.choice(all_materials)
        price = [(price_item, 1)]
        
        # Add to shop with a limited number of items
        if len(level.for_sale) < 6:
            level.for_sale[item_name] = {
                "item": item,
                "price": price,
                "description": f"A {item_name} with {element.value} properties."
            }

    def add_hints_about_boss(self, final_boss_level_index: int):
        """
        Add hints about the boss's weaknesses throughout the game.
        
        Args:
            final_boss_level_index: Index of the final boss level
        """
        # Create different types of hints
        hint_types = [
            f"The {self.boss_element.value} boss ahead is weak against {self.solution_element.value} attacks.",
            f"I've heard that {self.solution_element.value} weapons are effective against {self.boss_element.value} creatures.",
            f"To defeat a {self.boss_element.value} enemy, you'll want to use {self.solution_element.value} elemental weapons.",
            f"The ancient texts say that {self.boss_element.value} beings fear the power of {self.solution_element.value}."
        ]
        
        # Add hints to NPCs and readable objects in growth levels
        growth_levels = [level for level in self.levels if level.level_type == "growth" 
                        and self.levels.index(level) < final_boss_level_index]
        
        if not growth_levels:
            return
            
        # Choose up to 2 growth levels to add hints
        hint_levels = random.sample(growth_levels, min(2, len(growth_levels)))
        
        for level in hint_levels:
            hint = random.choice(hint_types)
            
            # Add to an NPC if available
            if level.npcs:
                npc_name = random.choice(list(level.npcs.keys()))
                level.npcs[npc_name]["dialog"] = f"\"Listen carefully, adventurer. {hint}\""
            
            # Or add to a readable object
            elif level.readables:
                readable_name = random.choice(list(level.readables.keys()))
                level.readables[readable_name]["content"] = f"The writing reveals: \"{hint}\""
            
            # If no NPCs or readables, create a new readable
            else:
                readable_name = random.choice(["ancient scroll", "mysterious tablet", "traveler's note", "forgotten tome"])
                level.readables[readable_name] = {
                    "description": f"There's a {readable_name} here with some writing on it.",
                    "content": f"The writing reveals: \"{hint}\""
                }
                level.interactions[readable_name] = level.readables[readable_name]
        
        # Also add a hint to the shopkeeper if a shop level exists
        shop_levels = [level for level in self.levels if level.level_type == "shop" 
                      and self.levels.index(level) < final_boss_level_index]
                      
        if shop_levels:
            shop_level = shop_levels[0]
            hint = random.choice(hint_types)
            
            # Add the hint as a potential shopkeeper dialog
            shop_dialogs = [
                f"\"A word of advice before you go further. {hint}\"",
                f"\"For a seasoned adventurer like you, this might be useful to know: {hint}\"",
                f"\"Between you and me? {hint} That'll be free advice, no charge.\""
            ]
            
            shop_hint = random.choice(shop_dialogs)
            shop_level._talk_to_shopkeeper = lambda: {"success": True, "message": f"{shop_level.shopkeeper_name} says: {shop_hint}"}


    def get_recommended_weapon(self):
        chosen_weakness = self.solution_element
        # Find a weapon matching the weakness
        possible_weapons = []
        # we can only fight them with advanced weapons
        for weapon_name, element in ADVANCED_WEAPONS.items():
            if element == chosen_weakness:
                possible_weapons.append(weapon_name)

        if not possible_weapons:
            return f"Warning: No available weapons matching the weakness {chosen_weakness.name} were found."

        recommended_weapon = possible_weapons[-1]
        return recommended_weapon

    def get_solution_crafting_recipes(self):
        """
        Recursively find all recipe names required to craft the recommended weapon.
        """
        rec_weapon = self.recommended_weapon
        needed = set()
        def build_chain(item):
            if item in CRAFTING_RECIPES:
                needed.add(item)
                for mat, qty in CRAFTING_RECIPES[item]:
                    build_chain(mat)
        build_chain(rec_weapon)
        return needed
            
    def _simulate_level_inventory_progression(self):
        """
        Simulate sequential forward progression of player inventory level by level.
        Returns:
            Tuple[List[List[Item]], List[List[Weapon]]]: 
                (expected_inv, expected_weapons_before_combat)
        """
        allowed_recipes = self.get_solution_crafting_recipes()
        req_materials_set = set(self.required_items.keys())
        sim_inv = VirtualInventory(capacity=self.inventory.capacity)

        def add_material_smart(item_name: str):
            mat = create_material(item_name, "")
            if not sim_inv.can_add(mat.weight):
                for existing in list(sim_inv.items):
                    if existing.name not in req_materials_set and existing.name not in allowed_recipes:
                        sim_inv.remove_item(existing.name, existing.count)
                        if sim_inv.can_add(mat.weight):
                            break
            if not sim_inv.can_add(mat.weight):
                # If a weapon has already been crafted, extra Weapon Prototypes are redundant and can be discarded
                if len(sim_inv.get_all_weapons()) > 0:
                    for existing in list(sim_inv.items):
                        if existing.name == 'Weapon Prototype':
                            sim_inv.remove_item(existing.name, existing.count)
                            if sim_inv.can_add(mat.weight):
                                break
            sim_inv.add_item(mat)

        for item in self.inventory.items:
            if item.name in req_materials_set or item.name in allowed_recipes:
                sim_inv.add_item(copy.deepcopy(item))
        sim_inv.try_all_possible_crafts(allowed_recipes)

        expected_inv = []
        expected_weapons_before_combat = []

        # Find items sourced for shop purchases per level
        shop_price_items_by_source = defaultdict(list)
        for p_name, src_lvl in getattr(self, "shop_items", []):
            if src_lvl is not None:
                shop_price_items_by_source[src_lvl].append(p_name)

        for level_idx, level in enumerate(self.levels):
            # Weapons available BEFORE combat or interactions in this level
            expected_weapons_before_combat.append(sim_inv.get_all_weapons())

            if level.level_type != "shop":
                # Collect items obtained in non-shop level
                if hasattr(self, "pre_existing_collected"):
                    for item_name in self.pre_existing_collected.get(level, []):
                        add_material_smart(item_name)

                if hasattr(self, "required_placed"):
                    for item_name in self.required_placed.get(level, []):
                        add_material_smart(item_name)

                if hasattr(self, "extra_shop_placed"):
                    for item_name in self.extra_shop_placed.get(level, []):
                        add_material_smart(item_name)

                # Add shop price items sourced from this level that weren't already added above
                already_added = (
                    self.pre_existing_collected.get(level, []).copy()
                    + self.required_placed.get(level, []).copy()
                    + self.extra_shop_placed.get(level, []).copy()
                )
                for p_name in shop_price_items_by_source.get(level, []):
                    if p_name in already_added:
                        already_added.remove(p_name)
                    else:
                        add_material_smart(p_name)
            else:
                # Handle shop level purchases
                shop_items_in_level = (
                    self.pre_existing_collected.get(level, [])
                    + self.required_placed.get(level, [])
                )
                for shop_item_name in shop_items_in_level:
                    item_info = getattr(level, "for_sale", {}).get(shop_item_name, {})
                    price_list = item_info.get("price", [])
                    for p_name, p_count in price_list:
                        sim_inv.remove_item(p_name, p_count)
                    add_material_smart(shop_item_name)

            sim_inv.try_all_possible_crafts(allowed_recipes)
            expected_inv.append(copy.deepcopy(sim_inv.items))

        expected_weapons_before_combat.append(sim_inv.get_all_weapons())
        return expected_inv, expected_weapons_before_combat

    def _get_level_to_items(self):
        """
        Get mapping of level -> {item_name: count} required for solution,
        eliminating double-counting across required_placed, pre_existing_collected, 
        extra_shop_placed, and shop_items.
        """
        level_to_items = defaultdict(lambda: defaultdict(int))
        accounted = defaultdict(lambda: defaultdict(int))

        if hasattr(self, "required_placed"):
            for level, items in self.required_placed.items():
                for item_name in items:
                    level_to_items[level][item_name] += 1

        if hasattr(self, "pre_existing_collected"):
            for level, items in self.pre_existing_collected.items():
                for item_name in items:
                    level_to_items[level][item_name] += 1
                    accounted[level][item_name] += 1

        if hasattr(self, "extra_shop_placed"):
            for level, items in self.extra_shop_placed.items():
                for item_name in items:
                    level_to_items[level][item_name] += 1
                    accounted[level][item_name] += 1

        for item_name, level in getattr(self, "shop_items", []):
            if level is not None:
                if accounted[level][item_name] > 0:
                    accounted[level][item_name] -= 1
                else:
                    level_to_items[level][item_name] += 1

        return level_to_items

    def get_solution_path(self, manual_type) -> str:
        """
        Return the full solution path: boss info, weakness, recommended weapon, and full crafting steps in natural English.
        
        Returns:
            str
        """
        if not self.solution_element:
            raise ValueError("Solution path not initialized. Call distribute_required_items() first.")

        boss_element = self.boss_element
        chosen_weakness = self.solution_element
        recommended_weapon = self.recommended_weapon

        # Recursively expand crafting steps
        crafting_steps = self.expand_crafting_chain(recommended_weapon, manual_type)

        if manual_type is None or str(manual_type).lower() == 'none':
            return ""

        # Build the natural language description
        lines = []
        lines.append(f"You will face a {boss_element.name}-element boss on the final floor.")
        lines.append(f"To counter it effectively, we recommend using a {chosen_weakness.name}-element weapon: {recommended_weapon}.")
        lines.append("")
        lines.append(f"To craft {recommended_weapon}, follow these steps:")

        for step in crafting_steps:
            lines.append(f"- {step}")

        lines.append("")
        
        if manual_type == 0:
            lines.append("Make sure that you have the following items in your inventory when you leave each of the levels:")

            expected_inv, expected_weapons_before_combat = self._simulate_level_inventory_progression()

            for level_id, items in enumerate(expected_inv[:-1]):
                lines.append(f"  Level {self.levels[level_id].level_number} ({self.levels[level_id].level_type}):")

                for item in items:
                    lines.append(f"    - {item.name} ×{item.count}")

            lines.append("")
            lines.append(f"To fight the enemies, make sure to:")
            for level_id_ori, level in enumerate(self.levels):
                if level.level_type in ['combat', 'boss']:
                    weapons = expected_weapons_before_combat[level_id_ori]
                    if level.level_type == 'boss' or len(level.enemies) == 1:
                        lines.append(
                            f"Level {self.levels[level_id_ori].level_number} ({level.level_type}): Arm yourself with the most powerful weapon against the enemies.")
                    else:
                        lines.append(
                            f"Level {self.levels[level_id_ori].level_number} ({level.level_type}): Arm yourself with the most powerful weapon against the enemies. You should beat at least one of the enemies to be able to proceed."
                        )
                    all_enemies = level.enemies if level.level_type == 'combat' else [level.enemy]

                    for enemy in all_enemies:
                        if weapons:
                            best_weapon = max(weapons, key=lambda w: enemy.get_weapon_damge(w))
                            damage = enemy.get_weapon_damge(best_weapon)
                            weapon_name = "your bare hands" if damage < 5 else best_weapon.name
                        else:
                            weapon_name = "your bare hands"

                        lines.append(
                            f" - To fight {enemy.name} ({enemy.element.value}), use {weapon_name}."
                        )
                    
        elif manual_type == 1:
            lines.append("You will need to prepare the following materials:")
            all_needed = defaultdict(int)
            for material, qty in self.required_items.items():
                all_needed[material] += qty

            level_to_items = self._get_level_to_items()
            for level, item_counts in level_to_items.items():
                for item, count in item_counts.items():
                    if item not in self.required_items:
                        all_needed[item] += count

            for material, qty in all_needed.items():
                lines.append(f"- {material} ×{qty}")

            # lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")

        elif manual_type in [2, 3, 4, 5]:
            level_to_items = self._get_level_to_items()

            if manual_type == 2:
                lines.append("You will need to collect items from the following levels:")
                for level in sorted(level_to_items.keys(), key=lambda l: l.level_number):
                    header = f"Level {level.level_number} ({level.level_type}):"
                    lines.append(header)
                    item_counts = level_to_items[level]
                    for item, count in item_counts.items():
                        lines.append(f" - {item} ×{count}")

                # lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")

            elif manual_type in [3, 5]:
                lines.append("You will need to collect items from the following levels:")
                for level in sorted(level_to_items.keys(), key=lambda l: l.level_number):
                    header = f"Level {level.level_number} ({level.level_type}):"
                    lines.append(header)

                    item_counts = level_to_items[level]
                    for item, count in item_counts.items():
                        sources = self.get_item_sources(level, item, count)
                        if sources:
                            source_info = ', '.join(sources)
                            if len(sources) > count:
                                source_info += f". You only need to collect {count} of them."
                            lines.append(f" - {item} ×{count} ({source_info})")
                        else:
                            lines.append(f" - {item} ×{count}")

                # lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")

            elif manual_type == 4:
                lines.append("Make sure to collect items when you are at these levels:")
                num_to_sample = max(1, len(level_to_items) // 2) if level_to_items else 0
                sampled_keys = set(random.sample(list(level_to_items.keys()), k=num_to_sample))

                for level in sorted(level_to_items.keys(), key=lambda l: l.level_number):
                    if level in sampled_keys:
                        header = f"Level {level.level_number} ({level.level_type}):"
                        lines.append(header)

                        item_counts = level_to_items[level]
                        for item, count in item_counts.items():
                            sources = self.get_item_sources(level, item, count)
                            if sources:
                                source_info = ', '.join(sources)
                                if len(sources) > count:
                                    source_info += f". You only need to collect {count} of them."
                                lines.append(f" - {item} ×{count} ({source_info})")
                            else:
                                lines.append(f" - {item} ×{count}")

                # lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")
                        
        # self.print_layout()
        return "\n".join(lines)
    
    def get_item_sources(self, level, item_name: str, count: int = 1) -> List[str]:
        sources = []

        # Check collectibles
        if hasattr(level, "collectibles"):
            for name, info in level.collectibles.items():
                item = info.get("item")
                if item and item.name == item_name:
                    sources.append("on the ground")
                elif name == item_name:
                    sources.append("on the ground")

        # Check containers
        if hasattr(level, "containers"):
            for container_name, info in level.containers.items():
                if info.get("item") and info["item"].name == item_name:
                    sources.append(f"in the {container_name}")

        # Check enemy drops
        enemies_to_check = []
        if hasattr(level, 'enemies') and level.enemies:
            enemies_to_check.extend(level.enemies)
        if hasattr(level, 'enemy') and level.enemy:
            enemies_to_check.append(level.enemy)
        for enemy in enemies_to_check:
            for drop in getattr(enemy, "drops", []):
                drop_name = drop if isinstance(drop, str) else getattr(drop, "name", "")
                if drop_name == item_name:
                    sources.append(f"from defeating {enemy.name}")

        # Check shop
        if hasattr(level, "for_sale") and item_name in level.for_sale:
            sources.append("in the shop")

        if len(sources) < count and "on the ground" in sources:
            while len(sources) < count:
                sources.append("on the ground")
            
        formatted_sources = []
        for src in sources:
            if src.startswith("on ") or src.startswith("in "):
                formatted_sources.append(f"one {src}")
            else:
                formatted_sources.append(src)
        return formatted_sources

    def expand_crafting_chain(self, item_name, manual_type, corruption_state=None):
        """
        Recursively expand the crafting steps needed to make item_name, 
        introducing at most 1-2 recipe errors across the entire chain if manual_type==5.

        Args:
            item_name (str): The item to craft.
            manual_type (int): Manual version (5 allows corruptions).
            corruption_state (dict): Tracks which items have been corrupted.

        Returns:
            List[str]: Step-by-step crafting instructions.
        """
        if corruption_state is None:
            corruption_state = {
                "corrupted_items": set(),
                "max_corruptions": 2,
                "remaining_corruptions": 2
            }

        steps = []
        recipe = CRAFTING_RECIPES.get(item_name)

        # First, expand children recursively
        for material, qty in recipe:
            if material in CRAFTING_RECIPES:
                steps += self.expand_crafting_chain(material, manual_type, corruption_state)

        # Decide whether to corrupt this recipe
        corrupt_this = False
        if manual_type == 5 and corruption_state["remaining_corruptions"] > 0:
            # Corrupt this step with probability:
            if len(recipe) > 1 or corruption_state["remaining_corruptions"] == corruption_state["max_corruptions"]:
                # Strong bias to ensure at least one is corrupted
                corrupt_this = True
                corruption_state["remaining_corruptions"] -= 1
                corruption_state["corrupted_items"].add(item_name)

        # Possibly corrupted recipe
        if corrupt_this:
            fake_recipe = recipe.copy()
            num_to_replace = 1
            if len(fake_recipe) > 1 and corruption_state["remaining_corruptions"] > 0 and random.random() < 0.1:
                num_to_replace = 2
                corruption_state["remaining_corruptions"] -= 1

            existing_materials = [mat for mat, _ in fake_recipe]
            replacement_candidates = [m for m in BASE_MATERIALS if m not in existing_materials]
            indices = random.sample(range(len(fake_recipe)), num_to_replace)

            for i in indices:
                if replacement_candidates:
                    fake_mat = random.choice(replacement_candidates)
                    fake_recipe[i] = (fake_mat, fake_recipe[i][1])

            recipe_for_display = fake_recipe
        else:
            recipe_for_display = recipe

        # material_list = ', '.join([f"{qty} {material}" for material, qty in recipe_for_display])
        material_list = ', '.join([pluralize(material, qty) for material, qty in recipe_for_display])
        steps.append(f"Craft {item_name} using {material_list}")

        return steps
    
    def print_layout(self):
        """
        Print the layout of all levels: type, and available items with sources.
        """
        print("\n=== GAME LEVEL LAYOUT ===\n")
        for idx, level in enumerate(self.levels):
            header = f"Level {idx + 1} ({level.level_type})"
            print(header)
            print("-" * len(header))

            found_any = False

            # 1. Ground items
            if hasattr(level, "collectibles") and level.collectibles:
                for item_name, info in level.collectibles.items():
                    if "item" in info:
                        print(f"- {item_name} (on the ground)")
                        found_any = True

            # 2. Containers
            if hasattr(level, "containers") and level.containers:
                for container_name, info in level.containers.items():
                    item = info.get("item")
                    if item:
                        print(f"- {item.name} (in the {container_name})")
                        found_any = True

            # 3. Enemy drops
            enemies_to_check = []
            if hasattr(level, "enemies") and level.enemies:
                enemies_to_check.extend(level.enemies)
            if hasattr(level, "enemy") and level.enemy:
                enemies_to_check.append(level.enemy)
            for enemy in enemies_to_check:
                for drop in getattr(enemy, "drops", []):
                    if isinstance(drop, str):
                        print(f"- {drop} (from defeating {enemy.name})")
                    else:
                        print(f"- {drop.name} (from defeating {enemy.name})")
                    found_any = True

            # 4. Shop items
            if hasattr(level, "for_sale") and level.for_sale:
                for item_name in level.for_sale:
                    print(f"- {item_name} (in the shop)")
                    found_any = True

            if not found_any:
                print("  (No obtainable items found in this level.)")

            print("")  # Add blank line between levels



def pluralize(name: str, qty: int) -> str:
    return f"{qty} {name if qty == 1 else name + 's'}"