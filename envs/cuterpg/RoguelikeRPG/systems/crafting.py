"""
Crafting system for the RougelikeRPG game.
"""
from typing import List, Tuple, Dict, Optional
from envs.cuterpg.RoguelikeRPG.constants import CRAFTING_RECIPES, ItemTier, Element
from envs.cuterpg.RoguelikeRPG.entities.item import Item, Material, Weapon, create_weapon
from envs.cuterpg.RoguelikeRPG.systems.inventory import Inventory

class CraftingSystem:
    """
    Handles item crafting logic, allowing players to combine items
    to create new weapons and items.
    """
    
    @staticmethod
    def get_available_recipes(inventory: Inventory) -> Dict[str, List[Tuple[str, int]]]:
        """
        Get all recipes that can be crafted with the current inventory.
        
        Args:
            inventory: The player's inventory
            
        Returns:
            Dict[str, List[Tuple[str, int]]]: Dictionary of craftable item names and their recipes
        """
        available_recipes = {}
        
        for item_name, ingredients in CRAFTING_RECIPES.items():
            if inventory.has_items(ingredients):
                available_recipes[item_name] = ingredients
        
        return available_recipes
    
    @staticmethod
    def craft_item(inventory: Inventory, item_name: str) -> Tuple[bool, str, Optional[Item]]:
        """
        Attempt to craft an item using the player's inventory.
        
        Args:
            inventory: The player's inventory
            item_name: The name of the item to craft
            
        Returns:
            Tuple[bool, str, Optional[Item]]: Success status, message, and the crafted item if successful
        """
        # Check if the recipe exists
        if item_name not in CRAFTING_RECIPES:
            return False, f"No recipe found for {item_name}", None
        
        # Get the required ingredients
        ingredients = CRAFTING_RECIPES[item_name]
        
        # Check if the player has all the ingredients
        if not inventory.has_items(ingredients):
            missing = []
            for ing_name, count in ingredients:
                item = inventory.get_item_by_name(ing_name)
                if not item or item.count < count:
                    missing.append(f"{ing_name} (need {count}, have {item.count if item else 0})")
            
            return False, f"Missing ingredients: {', '.join(missing)}", None
        
        # Remove the ingredients from the inventory
        for ing_name, count in ingredients:
            success, msg = inventory.remove_item(ing_name, count)
            if not success:
                # This shouldn't happen if has_items returned True, but just in case
                return False, f"Error removing {ing_name}: {msg}", None
        
        # Create the new item
        crafted_item = CraftingSystem._create_item_from_recipe(item_name)
        if not crafted_item:
            return False, f"Error creating {item_name}", None
        
        # Add the new item to the inventory
        success, msg = inventory.add_item(crafted_item)
        if not success:
            # If adding fails (e.g., due to weight), return the ingredients
            for ing_name, count in ingredients:
                # Create a temporary item to add back
                item = inventory.get_item_by_name(ing_name)
                if item:
                    item.count += count
            
            return False, f"Cannot add {item_name} to inventory: {msg}", None
        
        # return True, f"Successfully crafted {item_name}!", crafted_item
        return True, '', crafted_item
    
    @staticmethod
    def _create_item_from_recipe(item_name: str) -> Optional[Item]:
        """
        Create an item instance based on a recipe name.
        
        Args:
            item_name: The name of the item to create
            
        Returns:
            Optional[Item]: The created item, or None if it couldn't be created
        """
        from envs.cuterpg.RoguelikeRPG.constants import (
            STANDARD_WEAPONS, ADVANCED_WEAPONS, BASE_MATERIALS,
            ItemTier
        )
        
        # Determine the item type and properties
        if item_name in STANDARD_WEAPONS:
            element = STANDARD_WEAPONS[item_name]
            tier = ItemTier.STANDARD
            damage = 15
            description = f"A standard {element.value if element else ''} weapon."
            
            return create_weapon(item_name, description, tier, element, damage)
            
        elif item_name in ADVANCED_WEAPONS:
            element = ADVANCED_WEAPONS[item_name]
            tier = ItemTier.ADVANCED
            damage = 25
            description = f"An advanced {element.value if element else ''} weapon."
            
            return create_weapon(item_name, description, tier, element, damage)
            
        elif "Enhancer" in item_name:
            # Extract element from the name
            element_name = item_name.split(" ")[0]
            element = next((e for e in Element if e.name.upper() == element_name.upper()), None)
            
            description = f"An item that enhances the power of {element_name} weapons."
            return Material(item_name, description, element)
            
        elif item_name in BASE_MATERIALS:
            element = BASE_MATERIALS[item_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
            
            return Material(item_name, description, element)
        
        # If we don't recognize this item
        return None
    
    @staticmethod
    def get_recipe_description(item_name: str) -> str:
        """
        Get a human-readable description of a recipe.
        
        Args:
            item_name: The name of the item
            
        Returns:
            str: A description of the recipe
        """
        if item_name not in CRAFTING_RECIPES:
            return f"No recipe found for {item_name}"
        
        ingredients = CRAFTING_RECIPES[item_name]
        ingredients_str = ", ".join([f"{count} {name}" for name, count in ingredients])
        
        return f"Recipe for {item_name}: {ingredients_str}"
    
    @staticmethod
    def get_all_recipes() -> Dict[str, str]:
        """
        Get descriptions of all available recipes.
        
        Returns:
            Dict[str, str]: Dictionary of item names and their recipe descriptions
        """
        return {
            item_name: CraftingSystem.get_recipe_description(item_name)
            for item_name in CRAFTING_RECIPES
        }