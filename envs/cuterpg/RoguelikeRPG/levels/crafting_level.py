"""
Crafting level for the RougelikeRPG game.
"""
import random
from typing import List, Dict, Any, Tuple, Optional
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.systems.crafting import CraftingSystem

class CraftingLevel(Level):
    """
    A level focused on crafting items.
    
    Players can craft new weapons and items from materials
    they've collected.
    """
    
    def __init__(self, 
                 level_number: int, 
                 level_type, 
                 next_enemy_hint: Optional[str] = None,
                 reversible=False):
        super().__init__(level_number, level_type, reversible=reversible)
        self.available_actions = [
            # "craft",    # Craft an item
            # "recipes",  # View available recipes
        ] + self._get_common_actions()
        
        self.next_enemy_hint = next_enemy_hint
        self.environment_descriptions = [
            "A well-equipped workshop with a variety of tools and a blazing forge.",
            "An ancient crafting altar, surrounded by mysterious symbols and an aura of power.",
            "A serene clearing with a crafting table made from an enormous tree stump.",
            "A small cave converted into a cozy workshop, with crystals providing natural light.",
            "An abandoned blacksmith's shop, the tools still in good condition despite the dust.",
            "A magical crafting chamber where elements seem to dance in the air, ready to be shaped.",
            "A humble tent with surprisingly sophisticated crafting equipment inside."
        ]
        
        # Generate the level description
        # self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """Generate a description for the crafting level."""
        base_description = random.choice(self.environment_descriptions)
        
        hint = ""
        if self.next_enemy_hint:
            hint = f" There are signs warning about a {self.next_enemy_hint} beyond this point. Perhaps crafting something effective against it would be wise."
        
        return f"{base_description}{hint} This is the perfect place to craft new items before facing the challenges ahead."
    
# Updated crafting_level.py with improved enter method

    def enter(self, player: Player) -> str:
        """
        Called when the player enters this level.
        
        Args:
            player: The player entering the level
            
        Returns:
            str: A description of the level
        """
        # Update available recipes based on the player's current inventory
        self.available_recipes = CraftingSystem.get_available_recipes(player.inventory)
        
        # Get a description of available items in this level
        available_items = self.get_available_items_description()
        
        # Create a description of craftable items
        craftable_items = []
        if self.available_recipes:
            craftable_items.append("\nCraftable Items:")
            for item_name, ingredients in self.available_recipes.items():
                ingredients_str = ", ".join([f"{count} {name}" for name, count in ingredients])
                craftable_items.append(f"- {item_name}: Requires {ingredients_str}")
        
        # Combine all descriptions
        craftable_desc = "\n" + "\n".join(craftable_items) if craftable_items else ""
        full_description = f"{self.description}{available_items}{craftable_desc}"
        
        return full_description
    
    
    def process_action(self, player: Player, action: str, *args) -> Dict[str, Any]:
        """
        Process a player action in this level.
        
        Args:
            player: The player
            action: The action being taken
            args: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the action
        """
        action = action.lower()

        if action in self._get_common_actions():
            return self.process_general_action(player, action, *args)
        
        # Handle common actions
        if action == "craft":
            if len(args) == 0:
                return {"success": False, "message": "Craft what? Try 'craft [item name]'"}
            
            item_name = args[0]
            return self._craft_item(player, item_name)

        elif action == "recipes":
            return self._view_recipes(player)
        
        else:
            return {"success": False, "message": f"Invalid action: {action}."}
    
    def _craft_item(self, player: Player, item_name: str) -> Dict[str, Any]:
        """
        Craft an item using the player's materials.
        
        Args:
            player: The player
            item_name: The name of the item to craft
            
        Returns:
            Dict[str, Any]: The result of the action
        """
        # Update available recipes
        self.available_recipes = CraftingSystem.get_available_recipes(player.inventory)
        
        # Attempt to craft the item
        success, message, crafted_item = CraftingSystem.craft_item(player.inventory, item_name)
        
        if success:
            # Add some flavor text
            flavor_texts = [
                "The materials combine perfectly, forming ",
                "With skillful crafting, you create ",
                "The elements respond to your touch, becoming ",
                "After careful work, you've successfully crafted ",
                "The crafting process goes smoothly, resulting in "
            ]
            
            flavor = random.choice(flavor_texts)
            return {"success": True, "message": f"{flavor}{item_name}! {message}"}
        else:
            return {"success": False, "message": message}
    
    def _view_recipes(self, player: Player) -> Dict[str, Any]:
        """
        View all available crafting recipes.
        
        Args:
            player: The player
            
        Returns:
            Dict[str, Any]: The result of the action
        """
        # Get all recipes
        all_recipes = CraftingSystem.get_all_recipes()
        
        # Update available recipes
        self.available_recipes = CraftingSystem.get_available_recipes(player.inventory)
        
        # Create a formatted list of recipes
        recipes_by_category = {
            "Weapons": [],
            "Enhancers": [],
            "Advanced Weapons": []
        }
        
        for item_name, recipe_desc in all_recipes.items():
            # Categorize the recipe
            if "Enhancer" in item_name:
                category = "Enhancers"
            elif any(advanced in item_name for advanced in ["Inferno", "Tsunami", "Gaia", "Divine", "Void", "Storm", "Glacier", "Mountain"]):
                category = "Advanced Weapons"
            else:
                category = "Weapons"
            
            # Check if it's available
            available = item_name in self.available_recipes
            status = "[Available]" if available else "[Missing materials]"
            
            recipes_by_category[category].append(f"- {item_name}: {recipe_desc} {status}")
        
        # Format the complete recipe book
        content = "# Crafting Recipe Book\n\n"
        
        for category, recipes in recipes_by_category.items():
            if recipes:
                content += f"## {category}\n"
                content += "\n".join(recipes)
                content += "\n\n"
        
        return {
            "success": True,
            "message": "You review the crafting recipes you know...",
            "content": content
        }
    
    def can_exit(self, player: Player) -> Tuple[bool, str]:
        """
        Check if the player can exit this level.
        
        Args:
            player: The player
            
        Returns:
            Tuple[bool, str]: Whether the player can exit and a message
        """
        # Players can always exit a crafting level
        return True, "You can leave the crafting area and move on."