"""
Enemy entities for the RougelikeRPG game.
"""
import random
from typing import List, Tuple, Optional, Set
from collections import Counter
from envs.cuterpg.RoguelikeRPG.constants import *
from envs.cuterpg.RoguelikeRPG.entities.item import Item
from envs.cuterpg.RoguelikeRPG.constants import ELEMENT_EFFECTIVENESS
from pdb import set_trace as st

class Enemy:
    """
    Base class for enemies in the game.
    """
    
    def __init__(self, 
                 name: str, 
                 element: Element, 
                 hp_range: Tuple[int, int] = ENEMY_BASE_HP_RANGE,
                 drops: List[Item] = None):
        self.name = name
        self.element = element
        self.max_hp = random.randint(*hp_range)
        self.current_hp = self.max_hp
        self.drops = drops or []
        self.damage_high = ENEMY_DAMAGE_HIGH
        self.damage_low = ENEMY_DAMAGE_LOW
    
    @property
    def is_alive(self) -> bool:
        """Check if the enemy is still alive."""
        return self.current_hp > 0
    
    def take_damage(self, amount: int) -> int:
        """
        Apply damage to the enemy.
        
        Returns:
            int: The actual amount of damage taken
        """
        actual_damage = min(self.current_hp, amount)
        self.current_hp -= actual_damage
        return actual_damage
    
    def get_attack_damage(self) -> Tuple[int, str]:
        """
        Calculate the enemy's attack damage.
        
        Returns:
            Tuple[int, str]: Damage amount and a message describing the attack
        """
        base_damage = random.randint(self.damage_low, self.damage_high)
        return base_damage, f"{self.name} attacks and deals {base_damage} damage!"
    
    def get_weakness_elements(element: Element) -> Set[Element]:
        """
        Get the elements that are effective against this boss's element.
        
        Returns:
            Set[Element]: Set of elements that are effective
        """
        
        weaknesses = set()
        for attacker_elem, effectiveness_dict in ELEMENT_EFFECTIVENESS.items():
            if effectiveness_dict.get(element, 1.0) > 1.0:
                weaknesses.add(attacker_elem)
        
        return weaknesses
    
    def get_drop_items(self) -> List[Item]:
        """Get the items that this enemy drops when defeated."""
        return self.drops.copy()
    
    def __str__(self) -> str:
        """String representation of the enemy."""
        return f"{self.name} ({self.element.value}) - HP: {self.current_hp}/{self.max_hp}"
    

    def simulate_battle(self, weapons=[]) -> Tuple[int, int]:
        """
        Simulate a battle against this enemy using a list of weapons.
        Returns the best-case (minimal damage taken) scenario.

        Args:
            weapons (List[Weapon]): List of weapons to try.

        Returns:
            Tuple[int, int]: (turns_to_win, total_damage_taken)
        """

        def simulate_with_weapon(weapon) -> Tuple[int, int]:
            simulated_hp = self.current_hp
            turns = 0
            total_damage_taken = 0

            if weapon is None:
                weapon_damage = 5
            else:
                weapon_damage = max(weapon.get_damage_against(self.element),5)

            while simulated_hp > 0:
                turns += 1
                simulated_hp -= weapon_damage

                if simulated_hp <= 0:
                    break

                total_damage_taken += self.damage_high

            return turns, total_damage_taken

        # Try all weapon options, including no weapon
        candidates = list(weapons) + [None]

        best_result = None
        for weapon in candidates:
            result = simulate_with_weapon(weapon)
            if best_result is None or result[1] < best_result[1]:
                best_result = result

        return best_result
    
    def get_weapon_damge(self, weapon):
        return weapon.get_damage_against(self.element)

def generate_random_enemy(level: int = 1, 
                          element: Optional[Element] = None, 
                          drops: List[Item] = None) -> Enemy:
    """
    Generate a random enemy with the given parameters.
    
    Args:
        level: Enemy level (affects stats)
        element: Enemy element (random if None)
        drops: Items that the enemy drops
        
    Returns:
        Enemy: A randomly generated enemy
    """
    # Select a random element if none provided
    if element is None:
        element = Element.random()
    
    # Select a random enemy type for this element
    enemy_types = ENEMY_TYPES.get(element, ["Monster"])
    enemy_type = random.choice(enemy_types)
    
    # Add a random prefix
    prefix = random.choice(ENEMY_PREFIXES)
    
    # Construct the full name
    name = f"{prefix} {enemy_type}"
    
    # Calculate HP range based on level
    min_hp = ENEMY_BASE_HP_RANGE[0] + (level - 1) * 10
    max_hp = ENEMY_BASE_HP_RANGE[1] + (level - 1) * 10
    
    hp_range = (min_hp, max_hp)
    
    # Create the enemy
    return Enemy(name, element, hp_range, drops)


def generate_random_enemies(level: int = 1, 
                            elements: Optional[Element] = None, 
                            drops: List[Item] = None) -> Enemy:
    if elements is None:
        elements = Element.random()

    all_enemies = []

    element_counts = Counter(elements)
    for element, count in element_counts.items():
        # WARNINGS: we have only 3 types for each
        enemies = ENEMY_TYPES.get(element, ["Monster"])
        enemies = random.sample(enemies, k=count)
        for enemy in enemies:
            prefix = random.choice(ENEMY_PREFIXES)
            name = name = f"{prefix} {enemy}"
            # # Calculate HP range based on level
            min_hp = ENEMY_BASE_HP_RANGE[0] + (level - 1) * 10
            max_hp = ENEMY_BASE_HP_RANGE[1] + (level - 1) * 10
    
            hp_range = (min_hp, max_hp)
            enemy = Enemy(name, element, hp_range, drops)
            all_enemies.append(enemy)
            
    return all_enemies


    
    # # Select a random enemy type for this element
    # enemy_types = ENEMY_TYPES.get(element, ["Monster"])
    # enemy_type = random.choice(enemy_types)
    
    # # Add a random prefix
    # 
    
    # # Construct the full name
    # 
    
    