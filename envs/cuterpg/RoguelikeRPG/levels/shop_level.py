"""
Shop level for the RougelikeRPG game.
"""
import random
from typing import List, Dict, Any, Tuple, Optional
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.item import Item, create_material, create_weapon
from envs.cuterpg.RoguelikeRPG.constants import Element, ItemTier, BASE_MATERIALS, STANDARD_WEAPONS
from envs.cuterpg.RoguelikeRPG.systems.crafting import CraftingSystem
from pdb import set_trace as st

class ShopLevel(Level):
    """
    A level where the player can trade or purchase items.
    """
    
    def __init__(self, 
                 level_number: int, 
                 next_enemy_hint: Optional[str] = None,
                 reversible=False):
        super().__init__(level_number, "shop", reversible=reversible)
        self.available_actions = [
            "buy",      # Buy an item
            # "sell",     # Sell an item (not implemented in this MVP)
            "talk",     # Talk to the shopkeeper
        ] + self._get_common_actions()
        
        self.next_enemy_hint = next_enemy_hint
        self.shopkeeper_name = self._generate_shopkeeper_name()
        self.shop_type = self._generate_shop_type()
        self.for_sale = {}  # Items that can be purchased
        self.shopkeeper_dialog = None
        
        # Generate shop inventory
        self._generate_shop_inventory()
    
    def _generate_shopkeeper_name(self) -> str:
        """Generate a random name for the shopkeeper."""
        first_names = [
            "Gregor", "Eliza", "Thorne", "Seraphina", "Malachi", "Isolde", 
            "Orrin", "Lyra", "Flint", "Nessa", "Zephyr", "Briar"
        ]
        titles = [
            "the Merchant", "the Trader", "the Collector", "the Artificer",
            "the Mystic", "the Wanderer", "the Sage", "the Crafter"
        ]
        
        return f"{random.choice(first_names)} {random.choice(titles)}"
    
    def _generate_shop_type(self) -> str:
        """Generate a random type for the shop."""
        shop_types = [
            "General Store", "Weapons Emporium", "Magic Shop", "Traveling Caravan",
            "Artifact Collection", "Elemental Exchange", "Adventurer's Outfitter"
        ]
        return random.choice(shop_types)
    
    def _generate_shop_inventory(self):
        """Generate items for sale in the shop."""
        # Determine how many items to sell (3-6)
        num_items = random.randint(3, 6)
        
        # Chance distribution for different item types
        item_categories = [
            ("basic_material", 0.4),    # 40% basic materials
            ("standard_weapon", 0.3),   # 30% standard weapons
            ("special_item", 0.3)       # 30% special items
        ]
        
        # Generate items
        for _ in range(num_items):
            # Choose item category
            category = random.choices(
                [cat[0] for cat in item_categories],
                weights=[cat[1] for cat in item_categories],
                k=1
            )[0]
            
            if category == "basic_material":
                self._add_basic_material()
            elif category == "standard_weapon":
                self._add_standard_weapon()
            elif category == "special_item":
                self._add_special_item()
    
    def _add_basic_material(self):
        """Add a basic crafting material to the shop."""
        material_name = random.choice(list(BASE_MATERIALS.keys()))
        element = BASE_MATERIALS[material_name]
        
        # Check if we already have this material
        if material_name in self.for_sale:
            return
        
        description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        item = create_material(material_name, description, element)
        
        # Set price (trade requirements)
        price_material = random.choice([m for m in BASE_MATERIALS.keys() if m != material_name])
        price = [(price_material, 1)]
        
        self.for_sale[material_name] = {
            "item": item,
            "price": price,
            "description": f"A {material_name} for crafting."
        }
    
    def _add_standard_weapon(self):
        """Add a standard weapon to the shop."""
        weapon_name = random.choice(list(STANDARD_WEAPONS.keys()))
        element = STANDARD_WEAPONS[weapon_name]
        
        # Check if we already have this weapon
        if weapon_name in self.for_sale:
            return
        
        description = f"A standard {element.value if element else ''} weapon."
        item = create_weapon(weapon_name, description, ItemTier.STANDARD, element, damage=15)
        
        # Set price (trade requirements) - weapons cost more
        price = [
            (random.choice(list(BASE_MATERIALS.keys())), 1),
            ("Weapon Prototype", 1)
        ]
        
        self.for_sale[weapon_name] = {
            "item": item,
            "price": price,
            "description": f"A {weapon_name} that deals damage of type {element.value if element else 'neutral'}."
        }
    
    def _add_special_item(self):
        """Add a special or rare item to the shop."""
        special_items = ["Weapon Prototype", "Magic Catalyst", "Enchanted Cloth"]
        item_name = random.choice(special_items)
        
        # Check if we already have this item
        if item_name in self.for_sale:
            return
        
        description = "A universal crafting material used in many recipes."
        item = create_material(item_name, description)
        
        # Set price (trade requirements)
        price_material = random.choice([m for m in BASE_MATERIALS.keys() if m != item_name])
        price = [(price_material, 2)]  # Costs 2 of a material
        
        self.for_sale[item_name] = {
            "item": item,
            "price": price,
            "description": f"A special crafting material that's useful for advanced recipes."
        }
    
    def _generate_description(self) -> str:
        """Generate a description for the shop level."""
        descriptions = {
            "General Store": f"You enter a well-stocked general store. {self.shopkeeper_name} greets you from behind the counter, surrounded by a variety of goods.",
            "Weapons Emporium": f"The weapons emporium is lined with all manner of arms and armor. {self.shopkeeper_name} polishes a blade as you enter.",
            "Magic Shop": f"Mysterious items and glowing crystals fill the shelves of this magic shop. {self.shopkeeper_name} watches you with knowing eyes.",
            "Traveling Caravan": f"A colorful traveling caravan has set up shop here. {self.shopkeeper_name} beckons you to examine the exotic wares.",
            "Artifact Collection": f"Ancient and powerful artifacts are displayed carefully in this shop. {self.shopkeeper_name} appears to know the history of each one.",
            "Elemental Exchange": f"Elements in their purest form are contained in bottles and crystals throughout this shop. {self.shopkeeper_name} manipulates a floating orb of energy.",
            "Adventurer's Outfitter": f"Everything an adventurer could need is available in this outfitter's shop. {self.shopkeeper_name} sizes you up as you enter."
        }
        
        base_description = descriptions.get(self.shop_type, f"You enter a shop run by {self.shopkeeper_name}. Various items are available for trade.")
        
        # Add hint about next enemy if provided
        hint = ""
        if self.next_enemy_hint:
            hint = f" The shopkeeper mentions rumors of a {self.next_enemy_hint} in the area ahead."
        
        return f"{base_description}{hint} What would you like to do?"
    
# Updated shop_level.py with improved enter method

    def enter(self, player: Player) -> str:
        """
        Called when the player enters this shop level.
        
        Args:
            player: The player entering the level
            
        Returns:
            str: A description of the shop
        """
        self.description = self._generate_description()
        
        # Get a description of available items in this level
        available_items = self.get_available_items_description()
        
        # Combine the level description with the available items
        full_description = f"{self.description}{available_items}"
        
        return full_description
    
    def get_curr_obs(self):
        self.description = self._generate_description()
        
        # Get a description of available items in this level
        available_items = self.get_available_items_description()
        
        # Combine the level description with the available items
        full_description = f"{self.description}{available_items}"
        
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
        if action == "buy":
            if len(args) == 0:
                return {"success": False, "message": "Buy what? Try 'buy [item name]'"}
            
            item_name = args[0]
            return self._buy_item(player, item_name)
        
        elif action == "talk":
            return self._talk_to_shopkeeper()
        
        else:
            return {"success": False, "message": f"Invalid action: {action}."}

    def get_available_actions(self, player: Player) -> List[str]:
        actions = []
        for key, info in self.for_sale.items():
            if isinstance(info, dict) and 'item' in info:
                actions.append(f"buy {self._action_item_name(info['item'], key)}")
        actions.append("talk")
        return list(dict.fromkeys(actions + super().get_available_actions(player)))

    def _buy_item(self, player: Player, item_name: str) -> Dict[str, Any]:
        """
        Process a player buying an item.
        
        Args:
            player: The player
            item_name: The name of the item to buy
            
        Returns:
            Dict[str, Any]: The result of the action
        """
        # Check if the item is available
        # if item_name not in self.for_sale:
        #     return {"success": False, "message": f"{self.shopkeeper_name} says: \"I don't have any {item_name} for sale.\""}
        if item_name in self.renamed_items:
            return {"success": False, "message": f"{self.shopkeeper_name} says: \"I don't have any {item_name} for sale.\""}
        if item_name not in self.for_sale:
            matched_key = False
            for name, entry in self.for_sale.items():
                item = entry.get("item") if isinstance(entry, dict) else entry
                if item and item.display_name == item_name:
                    item_name = name
                    matched_key = True
                    break

            if not matched_key:
                return {"success": False, "message": f"{self.shopkeeper_name} says: \"I don't have any {item_name} for sale.\""}
        
        item_info = self.for_sale[item_name]
        price = item_info["price"]
        
        # Check if the player has the required items for trade
        if price[0][0] == 'coin':
            num = price[0][1]
            if player.inventory.coins < num:
                return {"success": False, "message": f"{self.shopkeeper_name} says: \"You don't have enough coins to buy this.\""}
            player.inventory.coins -= num
        else:
            if not player.inventory.has_items(price):
                missing = []
                for ing_name, count in price:
                    item = player.inventory.get_item_by_name(ing_name)
                    if not item or item.count < count:
                        missing.append(f"{ing_name} (need {count}, have {item.count if item else 0})")
                
                return {"success": False, "message": f"{self.shopkeeper_name} says: \"You don't have enough to trade for that. You're missing {', '.join(missing)}.\""}
                
            # Remove the trade items from inventory
            for trade_item, count in price:
                success, _ = player.inventory.remove_item(trade_item, count)
                if not success:
                    # This shouldn't happen if has_items returned True, but just in case
                    return {"success": False, "message": f"Error removing {trade_item} from your inventory."}
        
        # Add the purchased item to inventory
        success, message = player.add_to_inventory(item_info["item"])
        
        if not success:
            # If adding fails (e.g., due to weight), return the trade items
            for trade_item, count in price:
                # Create a temporary item to add back
                item = player.inventory.get_item_by_name(trade_item)
                if item:
                    item.count += count
            
            return {"success": False, "message": f"{self.shopkeeper_name} says: \"Hmm, seems like you can't carry that. {message}\""}
        
        # Remove the item from sale
        del self.for_sale[item_name]
        
        shown_name = self._action_item_name(item_info["item"], item_name)
        return {"success": True, "message": f"{self.shopkeeper_name} says: \"A fine choice! The {shown_name} is yours.\" You've added it to your inventory."}
    
    def _talk_to_shopkeeper(self) -> Dict[str, Any]:
        """Talk to the shopkeeper for information."""
        if self.shopkeeper_dialog is not None:
            return {"success": True, "message": f"{self.shopkeeper_name} says: {self.shopkeeper_dialog}"}
        # Possible shopkeeper dialogs
        dialogs = [
            f"\"Welcome to my {self.shop_type}! Feel free to browse my wares.\"",
            "\"Looking for something specific? I might be able to help.\"",
            "\"A seasoned adventurer like you must have some interesting stories!\"",
            "\"Quality items for quality adventurers, that's my motto.\"",
        ]
        
        # Add hint about next enemy if available
        if self.next_enemy_hint:
            dialogs.append(f"\"Be careful if you're heading out. I've heard rumors of a {self.next_enemy_hint} lurking in the area. Nasty creatures, those.\"")
            dialogs.append(f"\"You might want to prepare yourself. A traveler came through earlier saying they barely escaped a {self.next_enemy_hint}.\"")
        
        # Add hint about elements and crafting
        dialogs.append("\"Smart adventurers know that different elements are effective against different enemies. Fire melts ice, water douses fire - that sort of thing.\"")
        dialogs.append("\"If you find a Weapon Prototype, you can combine it with elemental materials to craft a weapon. Very useful for tackling specific enemies.\"")
        
        dialog = random.choice(dialogs)
        
        return {"success": True, "message": f"{self.shopkeeper_name} says: {dialog}"}
    
    def can_exit(self, player: Player) -> Tuple[bool, str]:
        """
        Check if the player can exit this level.
        
        Args:
            player: The player
            
        Returns:
            Tuple[bool, str]: Whether the player can exit and a message
        """
        # Players can always exit a shop
        return True, f"{self.shopkeeper_name} waves as you prepare to leave. \"Safe travels!\""