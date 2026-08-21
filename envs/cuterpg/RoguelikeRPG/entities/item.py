"""
Item classes for the RougelikeRPG game.
"""
from dataclasses import dataclass
from envs.cuterpg.RoguelikeRPG.constants import Element, ItemTier, ITEM_WEIGHTS
from envs.cuterpg.RoguelikeRPG.constants import ELEMENT_EFFECTIVENESS
from pdb import set_trace as st

@dataclass
class Item:
    """Base class for all items in the game."""
    name: str
    description: str
    tier: ItemTier
    element: Element = None
    count: int = 1
    display_name: str=''
    
    @property
    def weight(self):
        """Calculate the total weight of this item stack."""
        return ITEM_WEIGHTS[self.tier] * self.count
    
    @property
    def is_weapon(self):
        """Determine if this item is a weapon."""
        return isinstance(self, Weapon)
    
    @property
    def is_material(self):
        """Determine if this item is a crafting material."""
        return isinstance(self, Material)
    
    # def __str__(self):
    #     """String representation of the item."""
    #     # element_str = f" ({self.element.value})" if self.element else ""
    #     element_str = ""
    #     count_str = f" x{self.count}" if self.count > 1 else ""
    #     return f"{self.name}{element_str}{count_str}"

    def __str__(self):
        """String representation of the item (uses display_name if available)."""
        if self.display_name == '':
            name_to_show = self.name
        else:
            name_to_show = self.display_name
        element_str = ""
        count_str = f" x{self.count}" if self.count > 1 else ""
        return f"{name_to_show}{element_str}{count_str}"


@dataclass
class Material(Item):
    """Crafting materials used to create weapons."""
    
    def __init__(self, name, description, element=None, count=1):
        super().__init__(name, description, ItemTier.BASIC, element, count)
        
    def __str__(self):
        """String representation of the item."""
        if self.display_name == '':
            name_to_show = self.name
        else:
            name_to_show = self.display_name
        element_str = ""
        count_str = f" x{self.count}" if self.count > 1 else ""
        return f"{name_to_show}{element_str}{count_str}"


@dataclass
class Weapon(Item):
    """Weapons that can be used in combat."""
    damage: int = 10
    
    def __init__(self, name, description, tier, element, damage=10, count=1):
        super().__init__(name, description, tier, element, count)
        self.damage = damage
    
    def get_damage_against(self, target_element):
        """Calculate damage against a specific element."""
        
        if not self.element or not target_element:
            return self.damage
        
        effectiveness = ELEMENT_EFFECTIVENESS.get(self.element, {}).get(target_element, 1.0)
        calculated_damage = int(self.damage * effectiveness)
        return calculated_damage


# Factory functions to create items
def create_material(name, description, element=None, count=1):
    """Create a material item."""
    return Material(name, description, element, count)


def create_weapon(name, description, tier, element, damage=10, count=1):
    """Create a weapon item."""
    return Weapon(name, description, tier, element, damage, count)