"""
Boss entities for the RougelikeRPG game.
"""
import random
from typing import List, Tuple, Dict, Set, Optional
from envs.cuterpg.RoguelikeRPG.constants import Element, BOSS_NAMES, MINIBOSS_HP_RANGE, BOSS_HP_RANGE, ADVANCED_WEAPONS
from envs.cuterpg.RoguelikeRPG.entities.enemy import Enemy
from envs.cuterpg.RoguelikeRPG.entities.item import Item, Weapon
from envs.cuterpg.RoguelikeRPG.constants import ELEMENT_EFFECTIVENESS

class Boss(Enemy):
    """
    Boss class representing more powerful enemies with special abilities.
    """
    
    def __init__(self, 
                 name: str, 
                 element: Element,
                 hp_range: Tuple[int, int],
                 secondary_elements: List[Element] = None,
                 drops: List[Item] = None,
                 is_final_boss: bool = False):
        super().__init__(name, element, hp_range, drops)
        self.secondary_elements = secondary_elements or []
        self.is_final_boss = is_final_boss
        self.attack_pattern = self._generate_attack_pattern()
        self.current_attack_index = 0
        
    def _generate_attack_pattern(self, 
                                 max_possible=False) -> List[Tuple[str, Element, int]]:
        """
        Generate a sequence of attacks the boss will use.
        
        Returns:
            List[Tuple[str, Element, int]]: List of (attack_name, element, base_damage)
        """
        all_elements = [self.element] + self.secondary_elements
        
        # Create attack pattern based on primary and secondary elements
        pattern = []
        
        # Primary element strong attacks
        if max_possible:
            pattern.append((
                f"{self.element.value} Blast", 
                self.element, 
                25,
            ))
            
            # Add attacks for each secondary element
            for elem in self.secondary_elements:
                pattern.append((
                    f"{elem.value} Strike", 
                    elem, 
                    20,
                ))
            
            # Add a powerful combined attack if there are secondary elements
            if self.secondary_elements:
                combined_name = " & ".join([e.value for e in all_elements])
                pattern.append((
                    f"Combined {combined_name} Devastation", 
                    self.element, 
                    30,
                ))
        else:
            pattern.append((
                f"{self.element.value} Blast", 
                self.element, 
                random.randint(20, 25)
            ))
            
            # Add attacks for each secondary element
            for elem in self.secondary_elements:
                pattern.append((
                    f"{elem.value} Strike", 
                    elem, 
                    random.randint(15, 20)
                ))
            
            # Add a powerful combined attack if there are secondary elements
            if self.secondary_elements:
                combined_name = " & ".join([e.value for e in all_elements])
                pattern.append((
                    f"Combined {combined_name} Devastation", 
                    self.element, 
                    random.randint(25, 30)
                ))
        
        return pattern
    
    def get_attack_damage(self) -> Tuple[int, str]:
        """
        Get the boss's next attack based on its attack pattern.
        
        Returns:
            Tuple[int, str]: Damage and attack description
        """
        if not self.attack_pattern:
            return super().get_attack_damage()
        
        # Get the next attack in the pattern
        attack_name, element, base_damage = self.attack_pattern[self.current_attack_index]
        
        # Update the attack index for next time
        self.current_attack_index = (self.current_attack_index + 1) % len(self.attack_pattern)
        
        # Add some randomness to the damage
        actual_damage = base_damage + random.randint(-3, 3)
        
        return actual_damage, f"{self.name} uses {attack_name}!"
    
    @staticmethod
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
    
    @property
    def weakness_description(self) -> str:
        """Get a description of the boss's weaknesses."""
        weaknesses = self.get_weakness_elements(self.element)
        
        if not weaknesses:
            return f"{self.name} doesn't seem to have any obvious weaknesses."
        
        weakness_str = ", ".join([elem.value for elem in weaknesses])
        return f"{self.name} appears weak to: {weakness_str}"
    
    @staticmethod
    def get_optimal_weapons(element: Element) -> List[str]:
        """
        Get the names of weapons that would be most effective against this boss.
        
        Returns:
            List[str]: Names of effective weapons
        """
        weaknesses = Boss.get_weakness_elements(element)
        
        optimal_weapons = []
        for weapon_name, weapon_element in ADVANCED_WEAPONS.items():
            if weapon_element in weaknesses:
                optimal_weapons.append(weapon_name)
        
        return optimal_weapons
    
    def simulate_battle(self, weapons: List[Weapon] = []) -> Tuple[int, int]:
        """
        Simulate a battle against this boss using a list of weapons.
        Returns the best-case (minimal damage taken) scenario.

        Args:
            weapons (List[Weapon]): List of weapons to try.

        Returns:
            Tuple[int, int]: (turns_to_win, total_damage_taken)
        """

        attack_patterns = self._generate_attack_pattern(max_possible=True)

        def simulate_with_weapon(weapon: Optional[Weapon]) -> Tuple[int, int]:
            simulated_hp = self.current_hp
            turns = 0
            total_damage_taken = 0
            attack_index = 0

            if weapon is None:
                weapon_damage = 5
            else:
                weapon_damage = weapon.get_damage_against(self.element)

            if weapon_damage <= 0:
                return (float('inf'), float('inf'))

            while simulated_hp > 0:
                turns += 1
                simulated_hp -= weapon_damage

                if simulated_hp <= 0:
                    break

                # Boss counterattacks with rotating attack pattern
                damage = attack_patterns[attack_index][-1]
                damage = damage + 3
                total_damage_taken += damage
                attack_index = (attack_index + 1) % len(attack_patterns)

            return turns, total_damage_taken

        candidates = list(weapons) + [None]
        best_result = None

        for weapon in candidates:
            result = simulate_with_weapon(weapon)
            if best_result is None or result[1] < best_result[1]:
                best_result = result

        return best_result
    
    def __str__(self) -> str:
        """String representation of the boss."""
        boss_type = "FINAL BOSS" if self.is_final_boss else "MINI-BOSS"
        elements_str = f" ({self.element.value}"
        
        if self.secondary_elements:
            elements_str += ", " + ", ".join([e.value for e in self.secondary_elements])
        elements_str += ")"
        
        return f"{boss_type}: {self.name}{elements_str} - HP: {self.current_hp}/{self.max_hp}"


def generate_miniboss(element: Optional[Element] = None, 
                      drops: List[Item] = None) -> Boss:
    """Generate a mini-boss with the given parameters."""
    if element is None:
        element = Element.random()
    
    # Get a secondary element different from the primary
    all_elements = list(Element)
    secondary_elements = [e for e in all_elements if e != element]
    secondary = random.choice(secondary_elements)
    
    # Use a generic name based on the element
    name = f"{element.value} Champion"
    
    return Boss(
        name=name,
        element=element,
        hp_range=MINIBOSS_HP_RANGE,
        secondary_elements=[secondary],
        drops=drops,
        is_final_boss=False
    )


def generate_final_boss(element: Optional[Element] = None,
                        drops: List[Item] = None) -> Boss:
    """Generate a final boss with the given parameters."""
    if element is None:
        element = Element.random()
    
    # Get the predefined name for this element
    name = BOSS_NAMES.get(element, f"Ancient {element.value} Destroyer")
    
    # Get two secondary elements
    all_elements = list(Element)
    secondary_elements = [e for e in all_elements if e != element]
    secondary = random.sample(secondary_elements, 2)
    
    return Boss(
        name=name,
        element=element,
        hp_range=BOSS_HP_RANGE,
        secondary_elements=secondary,
        drops=drops,
        is_final_boss=True
    )