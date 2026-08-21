"""
Enhanced verification system to test if all combat encounters in the game are solvable.
"""
import random
from typing import Dict, List
from envs.cuterpg.RoguelikeRPG.constants import GameMode, BASE_MATERIALS, STANDARD_WEAPONS, ADVANCED_WEAPONS
from envs.cuterpg.RoguelikeRPG.game import Game
from envs.cuterpg.RoguelikeRPG.entities.boss import Boss
from envs.cuterpg.RoguelikeRPG.entities.enemy import Enemy
from pdb import set_trace as st

class EnhancedGameVerification:
    """
    An enhanced utility class to verify that games are solvable by ensuring that
    the necessary items to defeat all enemies, including the boss, can be obtained.
    """
    
    @staticmethod
    def verify_game_solvability(game: Game) -> Dict[str, any]:
        """
        Verify that a game is solvable by checking if the necessary items
        to defeat all enemies including the boss can be obtained.
        
        Args:
            game: The game to verify
            
        Returns:
            Dict: Results of the verification
        """
        # First, get the final boss level verification
        boss_verification = EnhancedGameVerification._verify_boss_solvability(game)
        
        # If the boss is not solvable, no need to check further
        if not boss_verification["solvable"]:
            return boss_verification
        
        # Check all combat levels in sequence
        combat_verifications = []
        current_collectible_items = {}  # Track what items are available at each point
        
        # Initialize with player's starting inventory
        for item in game.player.inventory.items:
            current_collectible_items[item.name] = current_collectible_items.get(item.name, 0) + item.count
        
        # Check each level in sequence
        for level_idx, level in enumerate(game.levels):
            # Skip the final boss level initially - we've already verified it
            if level_idx == len(game.levels) - 1 and level.level_type == "boss":
                continue
                
            # For combat/miniboss levels, verify they are solvable
            if level.level_type in ["combat", "miniboss"]:
                # Collect items available up to this point
                for pre_level_idx in range(level_idx):
                    pre_level = game.levels[pre_level_idx]
                    level_items = EnhancedGameVerification._get_level_collectible_items(pre_level)
                    
                    # Update the running total of available items
                    for item_name, count in level_items.items():
                        current_collectible_items[item_name] = current_collectible_items.get(item_name, 0) + count
                
                # Verify this combat level with the items available so far
                combat_verification = EnhancedGameVerification._verify_combat_level_solvability(
                    level, current_collectible_items, level_idx)
                
                combat_verifications.append(combat_verification)
                
                # If the level is not solvable, fail early
                if not combat_verification["solvable"]:
                    return {
                        "solvable": False,
                        "reason": f"Combat level {level_idx + 1} is not solvable: {combat_verification['reason']}",
                        "combat_verifications": combat_verifications,
                        "boss_verification": boss_verification
                    }
                
                # Add items from the level itself to our running total
                level_items = EnhancedGameVerification._get_level_collectible_items(level)
                for item_name, count in level_items.items():
                    current_collectible_items[item_name] = current_collectible_items.get(item_name, 0) + count
            else:
                # For non-combat levels, just collect items
                level_items = EnhancedGameVerification._get_level_collectible_items(level)
                for item_name, count in level_items.items():
                    current_collectible_items[item_name] = current_collectible_items.get(item_name, 0) + count
        
        # All checks passed, the game is solvable!
        # Include boss_element and solution_element at the top level for backward compatibility
        result = {
            "solvable": True,
            "boss_verification": boss_verification,
            "combat_verifications": combat_verifications,
            "total_collectible_items": current_collectible_items
        }
        
        # Add top-level fields for backward compatibility
        if "boss_element" in boss_verification:
            result["boss_element"] = boss_verification["boss_element"]
        if "solution_element" in boss_verification:
            result["solution_element"] = boss_verification["solution_element"]
        if "effective_against_boss" in boss_verification:
            result["effective_against_boss"] = boss_verification["effective_against_boss"]
        if "standard_weapon" in boss_verification:
            result["standard_weapon"] = boss_verification["standard_weapon"]
        if "advanced_weapon" in boss_verification:
            result["advanced_weapon"] = boss_verification["advanced_weapon"]
        if "solution_path" in boss_verification:
            result["solution_path"] = boss_verification["solution_path"]
        if "collectible_items" in boss_verification:
            result["collectible_items"] = boss_verification["collectible_items"]
        if "item_locations" in boss_verification:
            result["item_locations"] = boss_verification["item_locations"]
        
        return result
    
    @staticmethod
    def _verify_boss_solvability(game: Game) -> Dict[str, any]:
        """
        Verify that the final boss can be defeated with items obtainable in the game.
        
        Args:
            game: The game to verify
            
        Returns:
            Dict: Results of the verification
        """
        # Get the final boss level
        final_level = game.levels[-1]
        
        # Check if it's actually a boss level
        if final_level.level_type != "boss":
            return {
                "solvable": False,
                "reason": "Final level is not a boss level"
            }
        
        # Get the boss and its element
        boss = final_level.enemy
        boss_element = boss.element
        
        # Check if we have a solution element
        if not hasattr(game, "solution_element") or not game.solution_element:
            return {
                "solvable": False,
                "reason": "No solution element defined"
            }
        
        solution_element = game.solution_element
        
        # Determine if the solution element is effective against the boss
        weakness_elements = Boss.get_weakness_elements(boss_element)
        effective_against_boss = solution_element in weakness_elements
        
        # Check if all required items can be collected in the game
        collectible_items = EnhancedGameVerification._get_all_collectible_items(game)
        
        # Determine what items we need for our solution
        element_material_name = None
        for name, element in BASE_MATERIALS.items():
            if element == solution_element:
                element_material_name = name
                break
        
        if not element_material_name:
            return {
                "solvable": False,
                "reason": f"Could not find material name for solution element {solution_element}"
            }
        
        # Check if we can craft the necessary weapons
        standard_weapon_name = None
        for name, element in STANDARD_WEAPONS.items():
            if element == solution_element:
                standard_weapon_name = name
                break
        
        if not standard_weapon_name:
            return {
                "solvable": False,
                "reason": f"Could not find standard weapon for solution element {solution_element}"
            }
        
        # Check if the required items are available
        required_items = {
            element_material_name: 3,  # Need 3 total (1 for weapon, 2 for enhancer)
            "Weapon Prototype": 1,
            "Magic Catalyst": 1,
            "Enchanted Cloth": 1
        }
        
        # Check if we can collect enough of each required item
        missing_items = []
        for item_name, required_count in required_items.items():
            available_count = collectible_items.get(item_name, 0)
            if available_count < required_count:
                missing_items.append(f"{item_name} (need {required_count}, have {available_count})")
        
        if missing_items:
            return {
                "solvable": False,
                "reason": f"Missing required items: {', '.join(missing_items)}"
            }
        
        # Find the location of required items
        item_locations = EnhancedGameVerification._find_item_locations(game, required_items)
        
        # If we have all required items, check if we can craft the weapon
        advanced_weapon_name = None
        for name, element in ADVANCED_WEAPONS.items():
            if element == solution_element:
                advanced_weapon_name = name
                break
        
        if not advanced_weapon_name:
            return {
                "solvable": False,
                "reason": f"Could not find advanced weapon for solution element {solution_element}"
            }
        
        # Create detailed solution path
        solution_path = EnhancedGameVerification._create_solution_path(
            game, 
            boss_element, 
            solution_element,
            element_material_name,
            standard_weapon_name,
            advanced_weapon_name,
            item_locations
        )
        
        # All checks passed, the boss is beatable!
        return {
            "solvable": True,
            "boss_element": boss_element.name,
            "solution_element": solution_element.name,
            "effective_against_boss": effective_against_boss,
            "standard_weapon": standard_weapon_name,
            "advanced_weapon": advanced_weapon_name,
            "collectible_items": collectible_items,
            "item_locations": item_locations,
            "solution_path": solution_path
        }
    
    @staticmethod
    def _verify_combat_level_solvability(level, available_items, level_idx) -> Dict[str, any]:
        """
        Verify that a specific combat level can be beaten with the available items.
        
        Args:
            level: The level to verify
            available_items: Items available to the player at this point
            level_idx: Index of the level
            
        Returns:
            Dict: Results of the verification
        """
        # Make sure it's a combat level
        if level.level_type not in ["combat", "miniboss"]:
            return {
                "solvable": True,  # Non-combat levels are always "solvable"
                "level_type": level.level_type,
                "level_number": level.level_number
            }
        
        # Get the enemy element
        for enemy in level.enemies:
            enemy_element = enemy.element
            
            # Find the best weapon we can create with available materials
            best_weapon = EnhancedGameVerification._find_best_possible_weapon(available_items, enemy_element)

            if not best_weapon:
                return {
                    "solvable": False,
                    "reason": f"Unable to create any weapon to defeat the {enemy_element.name} enemy",
                    "level_type": level.level_type,
                    "level_number": level.level_number,
                    "enemy_element": enemy_element.name,
                    "available_items": available_items
                }
        
        # Different requirements for different level types:
        # 1. For regular combat levels, any standard weapon is sufficient
        # 2. For minibosses, we require either elemental advantage or an advanced weapon
        if level.level_type == "miniboss":
            weakness_elements = Enemy.get_weakness_elements(enemy_element)
            
            if best_weapon["element"] not in weakness_elements and best_weapon["tier"] != "advanced":
                return {
                    "solvable": False,
                    "reason": f"The best available weapon ({best_weapon['name']}) is not effective against the {enemy_element.name} miniboss",
                    "level_type": level.level_type,
                    "level_number": level.level_number,
                    "enemy_element": enemy_element.name,
                    "best_weapon": best_weapon,
                    "available_items": available_items
                }
        else:  # Regular combat level
            # For regular combat, ANY standard or above weapon is sufficient
            if best_weapon["tier"] not in ["standard", "advanced"]:
                return {
                    "solvable": False,
                    "reason": f"No standard or advanced weapon available for the regular combat level",
                    "level_type": level.level_type,
                    "level_number": level.level_number,
                    "enemy_element": enemy_element.name,
                    "best_weapon": best_weapon,
                    "available_items": available_items
                }
        
        # If we pass all checks, the level is solvable
        return {
            "solvable": True,
            "level_type": level.level_type,
            "level_number": level.level_number,
            "enemy_element": enemy_element.name,
            "best_weapon": best_weapon
        }
    
    @staticmethod
    def _find_best_possible_weapon(available_items, enemy_element) -> Dict[str, any]:
        """
        Find the best weapon that can be created with the available items.
        
        Args:
            available_items: Dictionary of available items and their counts
            enemy_element: The enemy's element
            
        Returns:
            Dict: Information about the best possible weapon, or None if no weapon can be created
        """
        # First, check if we can craft an advanced weapon with counter element
        for weapon_name, element in ADVANCED_WEAPONS.items():
            if element in Enemy.get_weakness_elements(enemy_element):
                # Check if we have the materials for this advanced weapon
                element_material_name = None
                for name, mat_element in BASE_MATERIALS.items():
                    if mat_element == element:
                        element_material_name = name
                        break
                
                if element_material_name and available_items.get(element_material_name, 0) >= 3 and \
                   available_items.get("Weapon Prototype", 0) >= 1 and \
                   available_items.get("Magic Catalyst", 0) >= 1 and \
                   available_items.get("Enchanted Cloth", 0) >= 1:
                    return {
                        "name": weapon_name,
                        "element": element,
                        "tier": "advanced",
                        "effective_against": enemy_element
                    }
        
        # Next, check if we can craft a standard weapon with counter element
        for weapon_name, element in STANDARD_WEAPONS.items():
            if element in Enemy.get_weakness_elements(enemy_element):
                # Check if we have the materials for this standard weapon
                element_material_name = None
                for name, mat_element in BASE_MATERIALS.items():
                    if mat_element == element:
                        element_material_name = name
                        break
                
                if element_material_name and available_items.get(element_material_name, 0) >= 1 and \
                   available_items.get("Weapon Prototype", 0) >= 1:
                    return {
                        "name": weapon_name,
                        "element": element,
                        "tier": "standard",
                        "effective_against": enemy_element
                    }
        
        # Next, check if we can craft any advanced weapon
        for weapon_name, element in ADVANCED_WEAPONS.items():
            element_material_name = None
            for name, mat_element in BASE_MATERIALS.items():
                if mat_element == element:
                    element_material_name = name
                    break
            
            if element_material_name and available_items.get(element_material_name, 0) >= 3 and \
               available_items.get("Weapon Prototype", 0) >= 1 and \
               available_items.get("Magic Catalyst", 0) >= 1 and \
               available_items.get("Enchanted Cloth", 0) >= 1:
                return {
                    "name": weapon_name,
                    "element": element,
                    "tier": "advanced",
                    "effective_against": enemy_element if element in Enemy.get_weakness_elements(enemy_element) else None
                }
        
        # Next, check if we can craft any standard weapon
        for weapon_name, element in STANDARD_WEAPONS.items():
            element_material_name = None
            for name, mat_element in BASE_MATERIALS.items():
                if mat_element == element:
                    element_material_name = name
                    break
            
            if element_material_name and available_items.get(element_material_name, 0) >= 1 and \
               available_items.get("Weapon Prototype", 0) >= 1:
                return {
                    "name": weapon_name,
                    "element": element,
                    "tier": "standard",
                    "effective_against": enemy_element if element in Enemy.get_weakness_elements(enemy_element) else None
                }
        
        # If we can't craft any weapon, we may have a basic weapon in inventory
        # (Not implemented in this version, but could check for weapons directly in inventory)
        
        # No weapon can be created
        return None
    
    @staticmethod
    def _get_level_collectible_items(level) -> Dict[str, int]:
        """
        Get all items that can be collected in a specific level.
        
        Args:
            level: The level to check
            
        Returns:
            Dict[str, int]: Dictionary of item names and their counts
        """
        collectible_items = {}
        
        # Check level type and collect appropriate items
        if level.level_type == "growth":
            # Check collectibles
            if hasattr(level, 'collectibles'):
                for item_name, item_info in level.collectibles.items():
                    if "item" in item_info:
                        item = item_info["item"]
                        collectible_items[item.name] = collectible_items.get(item.name, 0) + item.count
            
            # Check containers
            if hasattr(level, 'containers'):
                for container_info in level.containers.values():
                    if "item" in container_info and container_info["item"]:
                        item = container_info["item"]
                        collectible_items[item.name] = collectible_items.get(item.name, 0) + item.count
        
        # Check combat/miniboss levels (enemy drops)
        elif level.level_type in ["combat", "miniboss"]:
            if hasattr(level, 'enemy') and level.enemy and hasattr(level.enemy, 'drops'):
                for item in level.enemy.drops:
                    if not isinstance(item, str):
                        collectible_items[item.name] = collectible_items.get(item.name, 0) + item.count
            if hasattr(level, 'enemies') and level.enemies:
                for enemy in level.enemies:
                    if hasattr(enemy, 'drops') and enemy.drops:
                        for item in enemy.drops:
                            if not isinstance(item, str):
                                collectible_items[item.name] = collectible_items.get(item.name, 0) + item.count
        
        # Check shop levels
        elif level.level_type == "shop":
            # We can only count items as "collectible" if we can reasonably expect
            # to have the resources to purchase them
            if hasattr(level, 'for_sale'):
                for item_name, item_info in level.for_sale.items():
                    # Simple heuristic: if the price is just up to 2 of any basic material, it's obtainable
                    if "price" in item_info and "item" in item_info and \
                        len(item_info["price"]) == 1 and item_info["price"][0][1] <= 2:
                        item = item_info["item"]
                        collectible_items[item.name] = collectible_items.get(item.name, 0) + item.count
        
        return collectible_items
    
    @staticmethod
    def _get_all_collectible_items(game: Game) -> Dict[str, int]:
        """
        Get all items that can be collected in the game.
        
        Args:
            game: The game to check
            
        Returns:
            Dict[str, int]: Dictionary of item names and their counts
        """
        collectible_items = {}
        
        # First, add player's starting inventory
        for item in game.player.inventory.items:
            collectible_items[item.name] = collectible_items.get(item.name, 0) + item.count
        
        # Check each level for collectible items
        for level in game.levels:
            # Skip the final boss level
            if level == game.levels[-1] and level.level_type == "boss":
                continue
            
            level_items = EnhancedGameVerification._get_level_collectible_items(level)
            for item_name, count in level_items.items():
                collectible_items[item_name] = collectible_items.get(item_name, 0) + count
        
        return collectible_items
    
    @staticmethod
    def _find_item_locations(game: Game, required_items: Dict[str, int]) -> Dict[str, List[str]]:
        """
        Find where all the required items are located in the game.
        
        Args:
            game: The game to check
            required_items: Dictionary of required items and their counts
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping item names to their locations
        """
        item_locations = {}
        
        # Check if any items are in the player's starting inventory
        for item in game.player.inventory.items:
            if item.name in required_items:
                if item.name not in item_locations:
                    item_locations[item.name] = []
                item_locations[item.name].append(f"Starting Inventory: {item.name} x{item.count}")
        
        # Initialize locations for each required item that wasn't in starting inventory
        for item_name in required_items:
            if item_name not in item_locations:
                item_locations[item_name] = []
        
        # Go through each level looking for these items
        for level_idx, level in enumerate(game.levels):
            level_name = f"Level {level.level_number} ({level.level_type})"
            
            # Check growth levels
            if level.level_type == "growth":
                # Check collectibles
                if hasattr(level, 'collectibles'):
                    for item_name, item_info in level.collectibles.items():
                        if "item" in item_info and item_info["item"].name in required_items:
                            item_locations[item_info["item"].name].append(f"{level_name}: Collectible")
                
                # Check containers
                if hasattr(level, 'containers'):
                    for container_name, container_info in level.containers.items():
                        if "item" in container_info and container_info["item"]:
                            item = container_info["item"]
                            if item.name in required_items:
                                item_locations[item.name].append(f"{level_name}: Inside {container_name}")
            
            # Check combat levels (enemy drops)
            elif level.level_type in ["combat", "miniboss"]:
                if hasattr(level, 'enemy') and level.enemy and hasattr(level.enemy, 'drops'):
                    for item in level.enemy.drops:
                        if not isinstance(item, str) and item.name in required_items:
                            item_locations[item.name].append(f"{level_name}: Enemy drop from {level.enemy.name}")
            
            # Check shop levels
            elif level.level_type == "shop":
                if hasattr(level, 'for_sale'):
                    for item_name, item_info in level.for_sale.items():
                        if item_name in required_items and "price" in item_info:
                            price_str = ", ".join([f"{count} {name}" for name, count in item_info["price"]])
                            item_locations[item_name].append(f"{level_name}: Available for purchase (costs {price_str})")
        
        return item_locations
    
    @staticmethod
    def _create_solution_path(game: Game, 
                             boss_element, 
                             solution_element,
                             element_material_name,
                             standard_weapon_name,
                             advanced_weapon_name,
                             item_locations) -> str:
        """
        Create a detailed solution path showing how to beat all enemies including the boss.
        
        Args:
            game: The game to solve
            boss_element: The element of the boss
            solution_element: The element that counters the boss
            element_material_name: The name of the elemental material
            standard_weapon_name: The name of the standard weapon
            advanced_weapon_name: The name of the advanced weapon
            item_locations: Dictionary of where items can be found
            
        Returns:
            str: Detailed solution path
        """
        enhancer_name = f"{solution_element.name} Enhancer"
        
        solution = []
        
        # Introduction
        solution.append(f"## DETAILED SOLUTION PATH")
        solution.append(f"\nThis game is solvable! Here's how to defeat all enemies and the final boss:")
        
        # Game Structure Info
        solution.append(f"\n### 1. Game Structure")
        level_sequence = " → ".join([f"{level.level_number}:{level.level_type}" for level in game.levels])
        solution.append(f"Game Mode: {game.mode.name}")
        solution.append(f"Level Sequence: {level_sequence}")
        
        # Required Items
        solution.append(f"\n### 2. Required Items")
        solution.append(f"To complete the game, you need to collect the following items:")
        solution.append(f"- {element_material_name} x3 (1 for standard weapon, 2 for enhancer)")
        solution.append(f"- Weapon Prototype x1")
        solution.append(f"- Magic Catalyst x1")
        solution.append(f"- Enchanted Cloth x1")
        
        # Item Locations
        solution.append(f"\n### 3. Item Locations")
        for item_name, locations in item_locations.items():
            solution.append(f"\n{item_name} can be found at:")
            for location in locations:
                solution.append(f"- {location}")
        
        # Crafting Path
        solution.append(f"\n### 4. Crafting Strategy")
        solution.append(f"1. Craft {standard_weapon_name} as soon as possible:")
        solution.append(f"   - Combine: {element_material_name} + Weapon Prototype")
        solution.append(f"   - This will be useful for regular combat levels")
        
        solution.append(f"\n2. Craft {enhancer_name} when you get the materials:")
        solution.append(f"   - Combine: {element_material_name} (2) + Magic Catalyst")
        
        solution.append(f"\n3. Craft {advanced_weapon_name} before the final boss:")
        solution.append(f"   - Combine: {standard_weapon_name} + {enhancer_name} + Enchanted Cloth")
        solution.append(f"   - This is your ultimate weapon for the final boss")
        
        # Combat Levels Analysis
        solution.append(f"\n### 5. Combat Level Strategy")
        solution.append(f"Here's how to approach each combat level:")
        
        for level_idx, level in enumerate(game.levels):
            if level.level_type in ["combat", "miniboss"]:
                for enemy in level.enemies:
                    solution.append(f"\n#### Level {level.level_number}: {enemy.name} ({enemy.element.name} Element)")
                    
                    # Find the weakness elements
                    weakness_elements = [e.name for e in Boss.get_weakness_elements(enemy.element)]
                    solution.append(f"- Weakness: {', '.join(weakness_elements)}")
                    
                    # Weapon recommendations based on level type
                    if level.level_type == "combat":
                        solution.append(f"- **Strategy**: For this regular enemy, any standard weapon is sufficient.")
                        
                        # Add specific element suggestions if they exist
                        if weakness_elements:
                            best_elements = []
                            for element_name in weakness_elements:
                                for weapon_name, element in STANDARD_WEAPONS.items():
                                    if element.name == element_name:
                                        best_elements.append(f"{weapon_name} ({element_name} element)")
                                        break
                            
                            if best_elements:
                                solution.append(f"- **Optimal Weapons**: {', '.join(best_elements)} would be most effective")
                        
                        solution.append(f"- If you haven't found elements that are strong against {enemy.element.name}, " +
                                        f"any standard weapon will still work, but the battle may take longer.")
                        
                    else:  # miniboss
                        solution.append(f"- **Strategy**: This is a stronger enemy. You should either:")
                        solution.append(f"  1. Use a weapon with elemental advantage ({', '.join(weakness_elements)} element)")
                        solution.append(f"  2. OR use an advanced weapon if available")
                        
                        # Suggestion based on game progression
                        if level_idx < len(game.levels) - 2:  # Not close to the end
                            solution.append(f"- At this point in the game, focus on finding a weapon with elemental advantage " +
                                        f"since crafting an advanced weapon may not be possible yet.")
                        else:  # Near the end
                            solution.append(f"- Since this miniboss appears late in the game, you should have materials " +
                                        f"to craft an advanced weapon if needed.")
            
        # Final Boss Analysis
        solution.append(f"\n### 6. Final Boss Strategy")
        solution.append(f"- Boss Element: {boss_element.name} ({boss_element.value})")
        solution.append(f"- Weakness: {solution_element.name} ({solution_element.value})")
        solution.append(f"- Required Weapon: {advanced_weapon_name}")
        
        solution.append(f"\n**Combat Steps:**")
        solution.append(f"1. Make sure you have crafted {advanced_weapon_name} before entering the boss level")
        solution.append(f"2. Equip {advanced_weapon_name} before the battle")
        solution.append(f"3. Use the 'analyze' action to confirm the boss's weakness")
        solution.append(f"4. Attack with your {advanced_weapon_name} to deal maximum damage")
        
        if solution_element in Boss.get_weakness_elements(boss_element):
            solution.append(f"5. Your {solution_element.value} attacks will deal DOUBLE damage against the {boss_element.value} boss!")
        else:
            solution.append(f"5. While not maximally effective, your {solution_element.value} attacks should be sufficient to defeat the boss.")
        
        # Final Tips
        solution.append(f"\n### 7. General Tips")
        solution.append(f"- Always explore growth levels thoroughly to find all collectible items")
        solution.append(f"- Check all containers as they may hide essential crafting materials")
        solution.append(f"- In shop levels, prioritize buying the materials listed above if you're missing any")
        solution.append(f"- Craft the standard weapon early to make regular combat levels easier")
        solution.append(f"- Save at least 2 {element_material_name} for crafting the enhancer later")
        
        return "\n".join(solution)
    
    @staticmethod
    def batch_test_games(num_games: int = 100, mode: GameMode = GameMode.EASY) -> Dict[str, any]:
        """
        Create and test multiple games to verify solvability.
        
        Args:
            num_games: Number of games to test
            mode: Game mode to test
            
        Returns:
            Dict: Results of the batch test
        """
        results = {
            "total_games": num_games,
            "solvable_games": 0,
            "unsolvable_games": 0,
            "unsolvable_reasons": {},
            "element_distributions": {},
            "solution_distributions": {},
            "combat_level_failures": 0,  # Track how many games had combat level failures
            "boss_level_failures": 0     # Track how many games had boss level failures
        }
        
        for i in range(num_games):
            # Create a new game with a specific seed for reproducibility
            seed = i + 1000  # Just to have a predictable but varied seed
            game = Game(mode=mode, seed=seed)
            
            # Verify solvability
            verification = EnhancedGameVerification.verify_game_solvability(game)
            
            if verification["solvable"]:
                results["solvable_games"] += 1
                
                # Track element distributions
                boss_element = verification["boss_verification"]["boss_element"]
                solution_element = verification["boss_verification"]["solution_element"]
                
                results["element_distributions"][boss_element] = results["element_distributions"].get(boss_element, 0) + 1
                results["solution_distributions"][solution_element] = results["solution_distributions"].get(solution_element, 0) + 1
            else:
                results["unsolvable_games"] += 1
                reason = verification.get("reason", "Unknown")
                results["unsolvable_reasons"][reason] = results["unsolvable_reasons"].get(reason, 0) + 1
                
                # Categorize failures
                if "combat" in reason.lower():
                    results["combat_level_failures"] += 1
                elif "boss" in reason.lower() or not verification.get("boss_verification", {}).get("solvable", False):
                    results["boss_level_failures"] += 1
        
        # Calculate percentages
        results["solvable_percentage"] = (results["solvable_games"] / num_games) * 100
        
        return results
    
    @staticmethod
    def run_verification_report():
        """
        Run a comprehensive verification report for both game modes.
        
        Returns:
            Dict: Comprehensive verification results
        """
        report = {
            "easy_mode": EnhancedGameVerification.batch_test_games(50, GameMode.EASY),
            "hard_mode": EnhancedGameVerification.batch_test_games(50, GameMode.HARD),
            "overall_solvability": 0.0
        }
        
        # Calculate overall solvability
        total_games = report["easy_mode"]["total_games"] + report["hard_mode"]["total_games"]
        total_solvable = report["easy_mode"]["solvable_games"] + report["hard_mode"]["solvable_games"]
        report["overall_solvability"] = (total_solvable / total_games) * 100
        
        # Track the main types of failures
        report["combat_level_failures_percentage"] = ((report["easy_mode"]["combat_level_failures"] + 
                                                    report["hard_mode"]["combat_level_failures"]) / total_games) * 100
        report["boss_level_failures_percentage"] = ((report["easy_mode"]["boss_level_failures"] + 
                                                  report["hard_mode"]["boss_level_failures"]) / total_games) * 100
        
        return report