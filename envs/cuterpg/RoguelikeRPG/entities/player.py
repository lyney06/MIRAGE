"""
Player class for the RougelikeRPG game.
"""
from typing import Optional, List, Tuple, Dict
from envs.cuterpg.RoguelikeRPG.systems.inventory import Inventory
from envs.cuterpg.RoguelikeRPG.entities.item import Item, Weapon
from pdb import set_trace as st

class Player:
    """
    Represents the player character in the game.
    Handles inventory, health, equipped weapons, and player actions.
    """
    
    def __init__(self, name: str = "Adventurer"):
        self.name = name
        self.max_hp = None
        self.current_hp = self.max_hp
        self.inventory = Inventory()
        self.equipped_weapon: Optional[Weapon] = None
        self.known_info: Dict[str, str] = {}  # Store information gathered about the game

    @property
    def is_alive(self) -> bool:
        """Check if the player is still alive."""
        return self.current_hp > 0
    
    def set_max_hp(self, hp):
        self.max_hp = hp

    def equip_weapon(self, weapon_name: str) -> Tuple[bool, str]:
        """
        Equip a weapon from the inventory.
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        weapon = self.inventory.get_item_by_name(weapon_name)
        
        if not weapon:
            return False, f"You don't have {weapon_name} in your inventory"
        
        if not weapon.is_weapon:
            return False, f"{weapon_name} is not a weapon and cannot be equipped"
        
        self.equipped_weapon = weapon
        display = getattr(weapon, "display_name", "") or weapon.name
        return True, f"Equipped {display}"
    
    def unequip_weapon(self) -> Tuple[bool, str]:
        """
        Unequip the currently equipped weapon.
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        if not self.equipped_weapon:
            return False, "You have no weapon equipped"
        
        weapon_name = getattr(self.equipped_weapon, "display_name", "") or self.equipped_weapon.name
        self.equipped_weapon = None
        return True, f"Unequipped {weapon_name}"
    
    def add_to_inventory(self, item: Item) -> Tuple[bool, str]:
        """Add an item to the player's inventory."""
        return self.inventory.add_item(item)
    
    def take_damage(self, amount: int) -> int:
        """
        Apply damage to the player.
        
        Returns:
            int: The actual amount of damage taken
        """
        actual_damage = min(self.current_hp, amount)
        self.current_hp -= actual_damage
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Heal the player.
        
        Returns:
            int: The actual amount healed
        """
        missing_hp = self.max_hp - self.current_hp
        actual_heal = min(missing_hp, amount)
        self.current_hp += actual_heal
        return actual_heal
    
    def learn_info(self, key: str, info: str) -> None:
        """Store information the player has learned during the game."""
        self.known_info[key] = info
    
    def get_info(self, key: str) -> Optional[str]:
        """Retrieve information the player has learned."""
        return self.known_info.get(key)

    def get_attack_damage(self, target_element) -> Tuple[int, str]:
        """
        Calculate attack damage against a specific element.
        
        Returns:
            Tuple[int, str]: Damage amount and a message describing the attack
        """
        if not self.equipped_weapon:
            damage = 5
            return damage, f"You attack with your bare hands and deal {damage} damage."

        damage = self.equipped_weapon.get_damage_against(target_element)
        
        effectiveness_msg = ""
        if target_element:
            if damage > self.equipped_weapon.damage:
                effectiveness_msg = " It's super effective!"
            elif damage < self.equipped_weapon.damage:
                effectiveness_msg = " It's not very effective..."
        
        w_name = getattr(self.equipped_weapon, "display_name", "") or self.equipped_weapon.name
        return damage, f"You attack with {w_name} and deal {damage} damage.{effectiveness_msg}"
        
    def __str__(self) -> str:
        """String representation of the player."""
        status = f"{self.name} - HP: {self.current_hp}/{self.max_hp}\n"
        if self.equipped_weapon:
            status += f"Equipped: {self.equipped_weapon}\n"
        else:
            status += "No weapon equipped\n"
        
        status += str(self.inventory)
        return status