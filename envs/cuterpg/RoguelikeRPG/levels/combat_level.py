"""
Combat level for the RougelikeRPG game.
"""
import random
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.enemy import Enemy, generate_random_enemies
from envs.cuterpg.RoguelikeRPG.entities.item import Item, create_material
from envs.cuterpg.RoguelikeRPG.systems.combat import CombatSystem
from envs.cuterpg.RoguelikeRPG.systems.crafting import CraftingSystem
from envs.cuterpg.RoguelikeRPG.constants import Element, CAPACITY_INCREASE_COMBAT, BASE_MATERIALS
from .utils import add_item
from pdb import set_trace as st

class CombatLevel(Level):
    """
    A level focused on combat encounters.
    
    Players must defeat enemies to progress.
    """
    
    def __init__(self, 
                 level_number: int, 
                 difficulty: int = 1, 
                 enemy_elements: Optional[Element] = None,
                 enemy_num = 1,
                 reversible = False,
                 ):
        super().__init__(level_number, "combat", reversible=reversible)
        self.available_actions = [
            "attack",   # Attack the enemy
        ] + self._get_common_actions()
        self.enemy_num = enemy_num
        self.difficulty = difficulty
        self.enemy_elements = enemy_elements
        self.enemies = []
        self.combat_started = False
        self.ever_increase = False
        self.combat_finished = False
        self.combat_all_finished = False
        
        self.collectibles = {}    # Items that can be collected
        # Generate the level content
        self._generate_level_content()
    
    def _generate_level_content(self):
        """Generate the random content for this level."""
        # Generate an environment theme based on the enemy element
        if self.enemy_elements:
            # Element-specific environments
            environments = {
                Element.FIRE: ["volcano", "forge", "desert"],
                Element.WATER: ["lake", "ocean", "river"],
                Element.NATURE: ["forest", "jungle", "garden"],
                Element.LIGHT: ["temple", "crystal cave", "sunny meadow"],
                Element.DARK: ["shadow realm", "haunted mansion", "dark cave"],
                Element.ELECTRIC: ["lightning plains", "storm peak", "power station"],
                Element.ICE: ["glacier", "frozen tundra", "ice cave"],
                Element.EARTH: ["mountains", "canyon", "rocky plateau"],
            }
            theme_options = environments.get(self.enemy_elements[0], ["battlefield", "arena", "dangerous lands"])
            self.theme = random.choice(theme_options)
        else:
            # Generic combat environments
            generic_environments = ["battlefield", "arena", "ruins", "dark forest", "mountain pass", "abandoned temple"]
            self.theme = random.choice(generic_environments)
        
        # Generate the enemy
        self._generate_enemies()

         # Create the level description based on the theme
        self.description = self._generate_descriptions()
    
    def _generate_descriptions(self) -> str:
        """Generate a description for the level based on its theme."""
        descriptions = {
            "volcano": "You find yourself in a scorching volcanic field. Lava bubbles nearby, and the air is thick with ash and heat.",
            "forge": "The ancient forge glows with an unnatural fire. Tools of battle lie scattered about, and the heat is oppressive.",
            "desert": "The desert stretches out before you, sand whipping in the hot wind. Mirages shimmer in the distance.",
            "lake": "You stand at the edge of a vast lake, its waters unnaturally still and reflective. Mist rises from the surface.",
            "ocean": "Waves crash against rocky cliffs as you navigate the treacherous shoreline. The salt spray stings your eyes.",
            "river": "A powerful river rushes past, its waters churning and frothing. The roar of the current fills your ears.",
            "forest": "Thick, ancient trees surround you, their canopy blocking most of the light. Strange sounds echo through the woods.",
            "jungle": "The jungle is dense and humid, filled with exotic plants and the calls of unseen creatures.",
            "garden": "This overgrown garden might once have been beautiful, but now it's wild and menacing, with plants that seem to move on their own.",
            "temple": "Golden light filters through the columns of this ancient temple. Symbols of power adorn the walls.",
            "crystal cave": "Enormous crystals jut from every surface, reflecting light in dazzling patterns. The air feels charged with energy.",
            "sunny meadow": "This peaceful meadow seems too perfect - the flowers too bright, the light too golden. Something is not right here.",
            "shadow realm": "Darkness clings to everything in this twisted place. Shadows move in ways they shouldn't, and the air feels heavy.",
            "haunted mansion": "The decrepit mansion creaks and groans as if alive. Portraits on the walls seem to follow your movements.",
            "dark cave": "The cave is pitch black except for an eerie glow coming from deeper within. Unsettling sounds echo off the walls.",
            "lightning plains": "Static electricity makes your hair stand on end in these barren plains. Lightning strikes randomly in the distance.",
            "storm peak": "Atop this windswept mountain, a perpetual storm rages. Lightning illuminates the area in bright flashes.",
            "power station": "Ancient machinery hums and crackles with dangerous energy. Electricity arcs between metal structures.",
            "glacier": "The ice beneath your feet is slick and treacherous. Massive formations of ice tower overhead, and your breath freezes in the air.",
            "frozen tundra": "A bitter wind cuts across the frozen wasteland. Snow and ice stretch as far as the eye can see.",
            "ice cave": "Spectacular formations of ice surround you, reflecting light in blue and white hues. The air is frigid.",
            "mountains": "The rocky mountain path is treacherous and steep. Loose stones shift under your feet as you move.",
            "canyon": "Towering walls of rock rise on either side as you make your way through the narrow canyon.",
            "rocky plateau": "The windswept plateau offers little shelter, with jagged rocks and boulders strewn about.",
            "battlefield": "The smell of battle hangs in the air. Discarded weapons and signs of combat surround you.",
            "arena": "You find yourself in what appears to be an ancient arena, designed for combat and spectacle.",
            "ruins": "Crumbling structures and toppled columns suggest this was once a grand place, now reduced to ruins.",
            "dark forest": "The forest here is unnaturally dark, with twisted trees that seem to reach out like claws.",
            "mountain pass": "The narrow mountain pass offers precarious footing, with a sheer drop on one side.",
            "abandoned temple": "This temple has clearly been abandoned for ages, yet candles still burn, and there are signs of recent activity."
        }
        
        # Get the description for this theme, or use a generic one if not found
        base_description = descriptions.get(self.theme, "You find yourself in a place that seems designed for combat. The atmosphere is tense and threatening.")
        
        if getattr(self, "combat_all_finished", False) or (self.enemies and all(e.current_hp <= 0 for e in self.enemies)):
            return f"{base_description} All enemies have been defeated."
        elif self.enemies and not self.combat_started:
            enemies_str = ", ".join(f"{e.name} ({e.element.value if getattr(e, 'element', None) else 'neutral'})" for e in self.enemies)
            return f"{base_description} \nAs you enter, you spot the following enemies preparing to attack: {enemies_str}"
        elif self.enemies and self.combat_started and not self.combat_finished:
            alive_enemies = [e for e in self.enemies if e.current_hp > 0]
            if alive_enemies:
                enemies_str = ", ".join(f"{e.name} ({e.element.value if getattr(e, 'element', None) else 'neutral'})" for e in alive_enemies)
                return f"{base_description} \nYou're currently engaged in combat with: {enemies_str}"
            else:
                return f"{base_description} All enemies have been defeated."
        else:
            return base_description

    def _generate_enemies(self):
        """Generate one or more enemies for this combat encounter with unique names."""
        self.enemies = []

        elements_list = self.enemy_elements if isinstance(self.enemy_elements, list) else [self.enemy_elements]
        for element in elements_list:
            drops = []

            # Primary guaranteed drop
            material_name = random.choice(list(BASE_MATERIALS.keys()))
            mat_element = BASE_MATERIALS[material_name]
            description = f"A basic crafting material with {mat_element.value if mat_element else 'no'} elemental properties."
            drops.append(create_material(material_name, description, mat_element))
            drops.append('coin')

            # Optional second drop
            if random.random() < 0.3:
                extra = random.choice(["Weapon Prototype", "Magic Catalyst", "Enchanted Cloth"])
                drops.append(create_material(extra, "A universal crafting material used in many recipes."))

            # Generate random enemy for this element
            enemies = generate_random_enemies(
                    level=self.difficulty,
                    elements=[element],
                    drops=drops
                )
            self.enemies.extend(enemies)
    
    def enter(self, player: Player) -> str:
        """
        Called when the player enters this level.
        
        Args:
            player: The player entering the level
            
        Returns:
            str: A description of the level
        """
        self.combat_started = True
        self.description = self._generate_descriptions()
        
        # Get a description of available items in this level
        available_items = self.get_available_items_description()
        
        # Combine the level description with the available items
        full_description = f"{self.description}{available_items}"
        
        return full_description
    
    def get_curr_obs(self):
        self.description = self._generate_descriptions()
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
        if action == "attack":
            if len(args) == 0:
                alive_enemies = [e for e in self.enemies if e.current_hp > 0]
                if len(alive_enemies) == 1:
                    enemy_name = alive_enemies[0].name
                else:
                    return {"success": False, "message": "Attack what? Try 'attack [enemy name]'"}
            else:
                enemy_name = args[0]
            
            return self._attack_single_enemy(player, enemy_name)
        
        elif action == "collect":
            if len(args) == 0:
                return {"success": False, "message": "Collect what? Try 'collect [item name]'"}
            
            item_name = args[0]
            return self._collect_item(player, item_name)
        
        else:
            return {"success": False, "message": f"Invalid action: {action}."}

    def get_available_actions(self, player: Player) -> List[str]:
        actions = []
        if not self.combat_all_finished:
            alive_enemies = [e for e in self.enemies if e.current_hp > 0]
            for enemy in alive_enemies:
                actions.append(f"attack {enemy.name}")
            if len(alive_enemies) == 1:
                actions.append("attack")
        return list(dict.fromkeys(actions + super().get_available_actions(player)))

    def _attack_single_enemy(self, player: Player, enemy_name=None) -> Dict[str, Any]:
        """Process an attack against the enemy."""
        # Check if combat is finished
        if self.combat_all_finished:
            return {"success": False, "message": "All enemies have already been defeated."}

        matching_enemies = [e for e in self.enemies if e.name.lower() == (enemy_name or "").strip().lower()]
        if not matching_enemies:
            return {"success": False, "message": "The enemy does not exist here."}
        enemy = matching_enemies[0]
        if enemy.current_hp == 0:
            return {"success": False, "message": "The enemy has already been defeated."}
        # Process a round of combat
        combat_result = CombatSystem.process_combat_round(player, enemy, "attack")

        # Check if the battle is over
        if combat_result["battle_over"]:
            self.combat_finished = True
            if len([e for e in self.enemies if e.current_hp > 0]) == 0:
                self.combat_all_finished = True
            self.description = self._generate_descriptions()

            if combat_result["victory"]:
                # Player won, give rewards
                rewards, reward_message = CombatSystem.get_rewards(enemy)

                successful_adds = defaultdict(int)
                rew_info = ''
                failed_items = []

                # Increase inventory capacity as a reward
                if not self.ever_increase:
                    player.inventory.increase_capacity(CAPACITY_INCREASE_COMBAT)
                    self.ever_increase = True
                    capacity_message = f"Your inventory capacity has increased by {CAPACITY_INCREASE_COMBAT}!"
                else:
                    capacity_message = ''

                for reward_info in rewards:
                    if reward_info['name'] == 'coin':
                        player.inventory.coins += 1
                        rew_info += 'You got a coin.\n'
                    else:
                        success, info = player.add_to_inventory(reward_info["item"])
                        item_name = reward_info["item"].name
                        if success:
                            successful_adds[item_name] += reward_info["item"].count
                        else:
                            display_name = getattr(reward_info["item"], "display_name", "") or (self.renamed_items[item_name] if item_name in self.renamed_items else item_name)
                            add_item(item_name, self.collectibles, display_name=display_name)
                            failed_items.append(display_name)

                # Summarize successful adds
                for item_name, total_count in successful_adds.items():
                    if item_name in self.renamed_items:
                        item_name = self.renamed_items[item_name]
                    if total_count > 1:
                        rew_info += f"Added {item_name} ×{total_count} to inventory.\n"
                    else:
                        rew_info += f"Added {item_name} to inventory.\n"

                inventory_info = []
                # After the loop, summarize failed items if any
                if failed_items:
                    failed_items_str = ', '.join(failed_items)
                    rew_info += f"Due to insufficient inventory space, the following items could not be added: {failed_items_str}.\n"
                    reward_message = rew_info
                    
                    # if hasattr(self, 'collectibles') and self.collectibles:
                    inventory_info.append("\nThe items you couldn't collect have been left scattered around:")
                    for item_name, item_info in self.collectibles.items():
                        if "item" in item_info:
                            item = item_info["item"]
                            element_str = f" ({item.element.value})" if item.element else ""
                            if str(item) not in item_info['description']:
                                item_info['description'] = item_info['description'].replace(item_name, str(item))
                            inventory_info.append(f"- {str(item)}{element_str}: {item_info['description']}")
                
                if inventory_info:
                    inventory_info = '\n'.join(inventory_info)
                    message = f"{combat_result['round_summary']} {reward_message}\n{capacity_message}\n{inventory_info}\n"
                else:
                    message = f"{combat_result['round_summary']} {reward_message}\n{capacity_message}"
                
                return {
                    "success": True, 
                    "message": message,
                    "battle_over": True,
                    "victory": True
                }
            else:
                # Player lost
                return {
                    "success": False,
                    "message": combat_result["round_summary"],
                    "battle_over": True,
                    "victory": False
                }
        
        # Battle continues
        return {
            "success": True,
            "message": combat_result["round_summary"],
            "battle_over": False
        }
    
    def can_exit(self, player: Player) -> Tuple[bool, str]:
        """
        Check if the player can exit this level.
        
        Args:
            player: The player
            
        Returns:
            Tuple[bool, str]: Whether the player can exit and a message
        """
        # Player can only exit if they've defeated the enemy
        if not self.combat_finished:
            return False, "You must defeat the enemy before you can leave this area."
        
        return True, "The path ahead is clear now that you've defeated the enemy."
    
    def exit(self, player: Player) -> Dict[str, Any]:
        """Handle the player exiting the level."""
        result = super().exit(player)
        
        # Add information about inventory capacity increase
        if self.combat_finished:
            result["message"] += f" Your inventory capacity has increased to {player.inventory.capacity}."
        
        return result