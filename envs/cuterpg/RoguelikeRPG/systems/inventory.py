"""
Inventory system for the RougelikeRPG game.
"""
from typing import List, Dict, Optional, Tuple, Union
from envs.cuterpg.RoguelikeRPG.entities.item import Item, Material, Weapon
from envs.cuterpg.RoguelikeRPG.constants import INITIAL_INVENTORY_CAPACITY
from pdb import set_trace as st

class Inventory:
    """
    Manages the player's inventory, including items, weapons, and materials.
    Handles weight constraints and item organization.
    """
    
    def __init__(self, capacity: int = INITIAL_INVENTORY_CAPACITY):
        self.items: List[Item] = []
        self.capacity = capacity
        self.coins = 0
    
    @property
    def current_weight(self) -> int:
        """Calculate the current total weight of all items."""
        return sum(item.weight for item in self.items)
    
    @property
    def remaining_capacity(self) -> int:
        """Calculate remaining weight capacity."""
        return max(0, self.capacity - self.current_weight)
    
    @property
    def is_full(self) -> bool:
        """Check if the inventory is at full capacity."""
        return self.remaining_capacity == 0
    
    def get_items_by_type(self, item_type) -> List[Item]:
        """Get all items of a specific type."""
        return [item for item in self.items if isinstance(item, item_type)]
    
    @property
    def materials(self) -> List[Material]:
        """Get all materials in the inventory."""
        return self.get_items_by_type(Material)
    
    @property
    def weapons(self) -> List[Weapon]:
        """Get all weapons in the inventory."""
        return self.get_items_by_type(Weapon)
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        """Find an item by its internal name or display name."""
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
            if getattr(item, "display_name", "") and item.display_name.lower() == name.lower():
                return item
        return None
    
    
    def add_item(self, item: Item) -> Tuple[bool, str]:
        """
        Add an item to the inventory.
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        # Check if adding would exceed capacity
        if item.weight > self.remaining_capacity:
            return False, f"Cannot add {str(item)} - not enough inventory space (need {item.weight}, have {self.remaining_capacity})"
        
        # Check if we already have this item
        existing_item = self.get_item_by_name(item.name)
        if existing_item:
            # If it's stackable, just increase the count
            existing_item.count += item.count
            if getattr(existing_item, 'display_name', '') == '' and getattr(item, 'display_name', '') != '':
                existing_item.display_name = item.display_name
            return True, f"Added {str(item)} to inventory"
        
        # Otherwise, add as a new item
        self.items.append(item)
        return True, f"Added {str(item)} to inventory"
    
    
    def remove_item(self, item_name: str, count: int = 1) -> Tuple[bool, str]:
        """
        Remove an item from the inventory.
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        item = self.get_item_by_name(item_name)
        
        if not item:
            return False, f"Item '{item_name}' not found in inventory"
        
        if item.count < count:
            return False, f"Not enough {str(item)} in inventory (have {item.count}, need {count})"
        
        # Reduce count or remove completely
        if item.count > count:
            item.count -= count
            return True, f"Removed {count} {str(item)} from inventory"
        else:
            self.items.remove(item)
            return True, f"Removed {str(item)} from inventory"

    
    def has_items(self, required_items: List[Tuple[str, int]]) -> bool:
        """
        Check if inventory has all the required items.
        
        Args:
            required_items: List of (item_name, count) tuples
        
        Returns:
            bool: True if all items are present in sufficient quantities
        """
        for item_name, count in required_items:
            item = self.get_item_by_name(item_name)
            if not item or item.count < count:
                return False
        return True
    
    def increase_capacity(self, amount: int) -> None:
        """Increase the inventory capacity."""
        self.capacity += amount
    
    def __str__(self) -> str:
        """Generate a string representation of the inventory."""
        if not self.items:
            return "Inventory is empty"
        
        result = ''
        result += f"Coin(s): {self.coins}\n"
        result += f"Inventory (Weight: {self.current_weight}/{self.capacity}):\n"
        
        # Group by type
        weapons = self.weapons
        materials = self.materials
        
        if weapons:
            result += "Weapons:\n"
            for weapon in weapons:
                result += f"  - {weapon} ({weapon.element.value if weapon.element else 'No element'}, Dmg: {weapon.damage})\n"
        
        if materials:
            result += "Materials:\n"
            for material in materials:
                result += f"  - {material}\n"
        
        # result += f"You also have {self.coins} coin(s).\n"
        return result
    