"""
Boss level for the RougelikeRPG game.
"""
import random
from typing import List, Dict, Any, Tuple, Optional
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.boss import Boss, generate_miniboss, generate_final_boss
from envs.cuterpg.RoguelikeRPG.entities.item import create_material, create_weapon
from envs.cuterpg.RoguelikeRPG.systems.combat import CombatSystem
from envs.cuterpg.RoguelikeRPG.constants import Element, ItemTier, ADVANCED_WEAPONS, BASE_MATERIALS
from envs.cuterpg.RoguelikeRPG.systems.crafting import CraftingSystem
from pdb import set_trace as st

class BossLevel(Level):
    """
    A level featuring a boss encounter.
    
    Similar to combat levels but with more powerful enemies
    and special mechanics.
    """
    
    def __init__(self, 
                 level_number: int, 
                 is_final_boss: bool = True, 
                 boss_element: Optional[Element] = None,
                 reversible=False):
        # Initialize the base Level class
        super().__init__(level_number, "boss", reversible=reversible)
        
        # Set boss-specific attributes
        self.is_final_boss = is_final_boss
        self.boss_element = boss_element
        self.difficulty = 3
        self.enemy = None
        self.combat_started = False
        self.combat_finished = False
        self.boss_analyzed = False
        self.optimal_weapons = []
        
        # Set available actions
        self.available_actions = [
            "attack",   # Attack the enemy
            # "equip",    # Equip a weapon
            "analyze",  # Analyze the boss for weaknesses
        ] + self._get_common_actions()
        
        # Generate the level content
        self._generate_level_content()
        return

    
    def _generate_level_content(self):
        """Generate the content for this boss level."""
        # Generate an environment theme based on the enemy element
        if self.boss_element:
            # Element-specific environments
            environments = {
                Element.FIRE: ["volcano", "forge", "infernal temple"],
                Element.WATER: ["underwater palace", "abyssal trench", "flooded ruins"],
                Element.NATURE: ["ancient grove", "living forest", "primal jungle"],
                Element.LIGHT: ["celestial temple", "radiant sanctuary", "divine throne"],
                Element.DARK: ["shadow realm", "void chamber", "nightmare domain"],
                Element.ELECTRIC: ["storm spire", "lightning citadel", "thunder peak"],
                Element.ICE: ["frozen fortress", "glacier citadel", "eternal winter"],
                Element.EARTH: ["stone colosseum", "crystal cavern", "mountain throne"],
            }
            theme_options = environments.get(self.boss_element, ["ancient battlefield", "ritual chamber", "dimensional nexus"])
            self.theme = random.choice(theme_options)
        else:
            # Generic boss environments
            boss_environments = ["ancient throne room", "cursed sanctuary", "forbidden vault", "elemental nexus", "dimensional rift"]
            self.theme = random.choice(boss_environments)
        
        # Generate the boss
        self._generate_boss()
        
        # Create the level description based on the theme
        self.description = self._generate_description()
    
    def _generate_boss(self):
        """Generate a boss for this level."""
        # Determine what drops the boss will have
        drops = []
        
        # Basic drops - usually better than regular enemies
        possible_materials = list(BASE_MATERIALS.keys())
        for _ in range(2):  # Always drop at least 2 basic materials
            material_name = random.choice(possible_materials)
            element = BASE_MATERIALS[material_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
            drops.append(create_material(material_name, description, element))
        
        # Always drop a universal crafting material
        universal_material = random.choice(["Weapon Prototype", "Magic Catalyst", "Enchanted Cloth"])
        description = "A universal crafting material used in many recipes."
        drops.append(create_material(universal_material, description, count=2))
        
        # Final bosses might drop a special weapon
        if self.is_final_boss and random.random() < 0.5:  # 50% chance
            # Choose a random advanced weapon
            weapon_name = random.choice(list(ADVANCED_WEAPONS.keys()))
            element = ADVANCED_WEAPONS[weapon_name]
            description = f"An advanced {element.value if element else ''} weapon dropped by a powerful boss."
            drops.append(create_weapon(weapon_name, description, ItemTier.ADVANCED, element, damage=30))
        
        # Generate the appropriate boss
        if self.is_final_boss:
            self.enemy = generate_final_boss(element=self.boss_element, drops=drops)
        else:
            self.enemy = generate_miniboss(element=self.boss_element, drops=drops)
        
        # Store the optimal weapons to defeat this boss
        self.optimal_weapons = Boss.get_optimal_weapons(self.enemy.element)
    
    def _generate_description(self) -> str:
        """Generate a description for the boss level."""
        descriptions = {
            "volcano": "Intense heat radiates from the molten lava surrounding the arena. The air shimmers with waves of heat.",
            "forge": "Ancient forges line the walls, their flames burning eternally. The metallic smell of molten ore fills the air.",
            "infernal temple": "Unholy symbols glow with fiery light across the temple walls. Heat radiates from the very stone beneath your feet.",
            "underwater palace": "Magical barriers hold back the ocean, creating an eerie blue-lit throne room deep beneath the waves.",
            "abyssal trench": "The crushing weight of the ocean depths presses in from all sides, barely held at bay by ancient magic.",
            "flooded ruins": "Water covers the ancient floor up to your ankles. Pillars rise from the shallow flood, covered in glowing runes.",
            "ancient grove": "Massive, sentient trees form a natural cathedral. Their branches intertwine overhead, creating a living ceiling.",
            "living forest": "Every plant in this clearing seems to watch you. The undergrowth shifts subtly even without wind.",
            "primal jungle": "Primal energies course through the dense jungle. The plants here have never known civilization's touch.",
            "celestial temple": "Light streams through crystal windows, refracting into rainbows that dance across white marble floors.",
            "radiant sanctuary": "The chamber glows with inner light, as if the very air is illuminated from within. No shadows exist here.",
            "divine throne": "A magnificent throne of pure light dominates this heavenly chamber. Divine energy radiates throughout the space.",
            "shadow realm": "Darkness clings to every surface, absorbing light. Shadowy tendrils reach out from the corners of the room.",
            "void chamber": "The edges of this chamber seem to fade into nothingness. Stars twinkle in the infinite blackness beyond.",
            "nightmare domain": "The walls shift and change as you watch, taking forms from your deepest fears before dissolving again.",
            "storm spire": "Lightning arcs between metal rods that circle the chamber. Thunder echoes continuously around you.",
            "lightning citadel": "The air crackles with electrical energy. Static makes your hair stand on end as you enter.",
            "thunder peak": "This mountaintop arena is surrounded by perpetual storm clouds. Lightning illuminates the space in bright flashes.",
            "frozen fortress": "Ice forms every surface of this frozen hall. Your breath materializes in clouds before your face.",
            "glacier citadel": "Massive pillars of ancient ice support the ceiling of this frigid throne room. The cold is bone-deep and relentless.",
            "eternal winter": "Snow falls eternally from the ceiling of this magical chamber, never melting, never ceasing.",
            "stone colosseum": "Ancient stone seating surrounds this circular fighting pit. The walls bear the scars of countless battles.",
            "crystal cavern": "Massive crystals jut from floor and ceiling, reflecting light in dazzling patterns across the chamber.",
            "mountain throne": "This throne room has been carved directly from the mountain's heart. The stone walls rise impossibly high.",
            "ancient battlefield": "The ground is scorched and scarred from countless battles. Ancient weapons lie half-buried in the earth.",
            "ritual chamber": "Arcane circles and runes cover the floor and walls. The air thrums with magical energy.",
            "dimensional nexus": "Reality seems thin in this place where multiple dimensions touch. The edges of the room shift and blur.",
        }
        
        # Get the description for this theme
        base_description = descriptions.get(self.theme, "You enter an imposing chamber clearly designed for a final confrontation.")
        
        # Add boss-specific information
        if self.enemy:
            boss_type = "FINAL BOSS" if self.is_final_boss else "MINI-BOSS"
            elem_str = f" ({self.enemy.element.value})" if getattr(self.enemy, 'element', None) else ""
            
            if self.enemy.current_hp <= 0 or self.combat_finished:
                return f"{base_description}\n\nThe defeated {self.enemy.name} lies before you."
            elif not self.combat_started:
                return f"{base_description}\n\nA powerful presence fills the air... THE {boss_type} {self.enemy.name}{elem_str} awaits your challenge!"
            else:
                return f"{base_description}\n\nYou're in combat with THE {boss_type} {self.enemy.name}!"
        else:
            # Fallback if enemy hasn't been generated yet
            return f"{base_description}\n\nA foreboding presence fills this chamber. A powerful enemy awaits..."
    
# For boss_level.py, we need to override the parent class method

    def enter(self, player: Player) -> str:
        """
        Called when the player enters this level.
        
        Args:
            player: The player entering the level
            
        Returns:
            str: A description of the level
        """
        # Call the parent class's enter method to set combat_started
        super().enter(player)
        self.description = self._generate_description()
        
        # Get a description of available items in this level
        available_items = self.get_available_items_description()
        
        # Combine the level description with the available items
        full_description = f"{self.description}{available_items}"
        
        return full_description
    
    def get_curr_obs(self):
        self.description = self._generate_description()
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
        if action == "analyze":
            return self._analyze_boss(player)
        
        # Handle combat actions
        elif action == "attack":
            if len(args) > 0 and self.enemy and args[0].strip().lower() != self.enemy.name.lower():
                return {"success": False, "message": f"The enemy {args[0]} does not exist here."}
            return self._attack_enemy(player)
        
        else:
            return {"success": False, "message": f"Invalid action: {action}."}

    def get_available_actions(self, player: Player) -> List[str]:
        actions = []
        if self.enemy and not self.combat_finished:
            actions.append("attack")
            actions.append(f"attack {self.enemy.name}")
            if not self.boss_analyzed:
                actions.append("analyze")
        return list(dict.fromkeys(actions + super().get_available_actions(player)))

    def _analyze_boss(self, player: Player) -> Dict[str, Any]:
        """
        Analyze the boss to discover its weaknesses.
        This doesn't consume a combat turn.
        """
        if not self.enemy or self.combat_finished:
            return {"success": False, "message": "There's no boss to analyze."}
        
        # Mark as analyzed
        self.boss_analyzed = True
        
        # Get the boss's weakness description
        weakness_info = self.enemy.weakness_description
        
        # Get optimal weapon recommendations
        if self.optimal_weapons:
            weapons_info = f"Recommended weapons: {', '.join(self.optimal_weapons)}"
        else:
            weapons_info = "No specific weapon recommendations available."
        
        return {
            "success": True,
            "message": "You carefully analyze the boss's movements and appearance...",
            "content": f"{weakness_info}\n\n{weapons_info}"
        }
    
    def _attack_enemy(self, player: Player) -> Dict[str, Any]:
        """Process an attack against the enemy."""
        # Check if combat is finished
        if self.combat_finished:
            return {"success": False, "message": "The combat has already ended."}
        
        # Check if there's an enemy to attack
        if not self.enemy:
            return {"success": False, "message": "There's no enemy to attack here."}
        
        # Process a round of combat
        combat_result = CombatSystem.process_combat_round(player, self.enemy, "attack")
        
        # Check if the battle is over
        if combat_result["battle_over"]:
            self.combat_finished = True
            self.description = self._generate_description()
            
            if combat_result["victory"]:
                # Player won, give rewards
                rewards, reward_message = CombatSystem.get_rewards(self.enemy)
                
                # Add items to player inventory
                for reward_info in rewards:
                    player.add_to_inventory(reward_info["item"])
                
                # Craft a boss-specific victory message
                if self.is_final_boss:
                    victory_message = f"You have defeated the {self.enemy.name}, the final boss! Congratulations!"
                else:
                    victory_message = f"You have defeated the {self.enemy.name}! A formidable victory!"
                
                return {
                    "success": True, 
                    "message": f"{combat_result['round_summary']} {reward_message} {victory_message}",
                    "battle_over": True,
                    "victory": True,
                    "is_final_boss": self.is_final_boss
                }
            else:
                # Player lost
                return {
                    "success": False,
                    "message": combat_result["round_summary"],
                    "battle_over": True,
                    "victory": False
                }
        
        # Add information about weapon effectiveness if player has a weapon equipped
        result = {
            "success": True,
            "message": combat_result["round_summary"],
            "battle_over": False
        }
        
        # Add weapon effectiveness information
        if player.equipped_weapon:
            if player.equipped_weapon.name in self.optimal_weapons:
                result["message"] += " Your weapon seems extremely effective against this boss!"
            elif self.boss_analyzed and player.equipped_weapon.element not in Boss.get_weakness_elements(self.enemy.element):
                result["message"] += " Your weapon doesn't seem very effective. Perhaps try a different element?"
        
        return result
    
    def can_exit(self, player: Player) -> Tuple[bool, str]:
        """
        Check if the player can exit this level.
        
        Args:
            player: The player
            
        Returns:
            Tuple[bool, str]: Whether the player can exit and a message
        """
        # Player can only exit if they've defeated the boss
        if not self.combat_finished:
            return False, "You must defeat the boss before you can leave this area."
        
        return True, "The path ahead is clear now that you've defeated the boss."
    
    def exit(self, player: Player) -> Dict[str, Any]:
        """Handle the player exiting the level."""
        result = super().exit(player)
        
        # Add boss-specific exit message
        if self.is_final_boss:
            result["message"] = f"You leave the arena victorious, having defeated the powerful {self.enemy.name}!"
            result["game_completed"] = True
        else:
            result["message"] = f"You've defeated the {self.enemy.name} and can now proceed deeper into the dungeon."
        
        return result