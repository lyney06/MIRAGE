"""
Combat system for the RougelikeRPG game.
"""
from typing import List, Tuple, Dict, Optional, Union
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.enemy import Enemy
from envs.cuterpg.RoguelikeRPG.entities.boss import Boss
from pdb import set_trace as st

class CombatSystem:
    """
    Handles combat logic between the player and enemies.
    """
    
    @staticmethod
    def attack_enemy(player: Player, enemy: Enemy) -> Dict[str, Union[str, int, bool]]:
        """
        Process a player attack against an enemy.
        
        Args:
            player: The player
            enemy: The enemy to attack
            
        Returns:
            Dict: A dictionary containing the results of the attack
        """
        # Calculate damage
        damage, attack_msg = player.get_attack_damage(enemy.element)
        
        # Apply damage to enemy
        actual_damage = enemy.take_damage(damage)
        
        # Check if enemy died
        enemy_defeated = not enemy.is_alive
        
        # Prepare result
        result = {
            "success": True,
            "message": attack_msg,
            "damage_dealt": actual_damage,
            "enemy_defeated": enemy_defeated,
        }
        
        if enemy_defeated:
            result["defeat_message"] = f"You have defeated {enemy.name}!"
        
        return result
    
    @staticmethod
    def enemy_attack(enemy: Enemy, player: Player) -> Dict[str, Union[str, int, bool]]:
        """
        Process an enemy attack against the player.
        
        Args:
            enemy: The attacking enemy
            player: The player
            
        Returns:
            Dict: A dictionary containing the results of the attack
        """
        # Calculate damage
        damage, attack_msg = enemy.get_attack_damage()
        
        # Apply damage to player
        actual_damage = player.take_damage(damage)
        
        # Check if player died
        player_defeated = not player.is_alive
        
        # Prepare result
        result = {
            "success": True,
            "message": attack_msg,
            "damage_dealt": actual_damage,
            "player_defeated": player_defeated,
        }
        
        if player_defeated:
            result["defeat_message"] = "You have been defeated!"
        
        return result
    
    @staticmethod
    def process_combat_round(player: Player, 
                             enemy: Enemy, 
                             player_action: str) -> Dict[str, Union[str, List[Dict], bool]]:
        """
        Process a complete round of combat.
        
        Args:
            player: The player
            enemy: The enemy
            player_action: What action the player is taking this round
            
        Returns:
            Dict: A dictionary containing the results of the combat round
        """
        round_results = {
            "player_turn_result": None,
            "enemy_turn_result": None,
            "battle_over": False,
            "victory": False,
            "round_summary": "",
        }
        
        # Process player action
        if player_action.lower() == "attack":
            player_result = CombatSystem.attack_enemy(player, enemy)
            round_results["player_turn_result"] = player_result
            
            # Check if enemy was defeated
            if player_result.get("enemy_defeated", False):
                round_results["battle_over"] = True
                round_results["victory"] = True
                round_results["round_summary"] = f"{player_result.get('message')} {player_result.get('defeat_message')}"
                return round_results
        else:
            round_results["player_turn_result"] = {
                "success": False,
                "message": f"Invalid action: {player_action}"
            }
            # We still let the enemy attack even if player did an invalid action
        
        # Process enemy turn if battle isn't over
        if not round_results["battle_over"]:
            enemy_result = CombatSystem.enemy_attack(enemy, player)
            round_results["enemy_turn_result"] = enemy_result
            
            # Check if player was defeated
            if enemy_result.get("player_defeated", False):
                round_results["battle_over"] = True
                round_results["victory"] = False
                
                # Combine the results for the round summary
                player_msg = round_results["player_turn_result"].get("message", "")
                enemy_msg = enemy_result.get("message", "")
                defeat_msg = enemy_result.get("defeat_message", "")
                
                round_results["round_summary"] = f"{player_msg} Then, {enemy_msg} {defeat_msg}"
                return round_results
        
        # If we're here, the battle continues
        player_msg = round_results["player_turn_result"].get("message", "")
        enemy_msg = round_results["enemy_turn_result"].get("message", "")
        
        round_results["round_summary"] = f"{player_msg} Then, {enemy_msg}"
        return round_results
    
    @staticmethod
    def get_combat_status(player: Player, enemy: Enemy) -> str:
        """
        Get a status summary of the current combat situation.
        
        Args:
            player: The player
            enemy: The enemy
            
        Returns:
            str: A summary of the current combat status
        """
        return (
            f"--- Combat Status ---\n"
            f"Player: {player.name} - HP: {player.current_hp}/{player.max_hp}\n"
            f"Enemy: {enemy}\n"
            f"-------------------------"
        )
    
    @staticmethod
    def get_rewards(enemy: Enemy) -> Tuple[List[Dict], str]:
        """
        Calculate rewards for defeating an enemy.
        
        Args:
            enemy: The defeated enemy
            
        Returns:
            Tuple[List[Dict], str]: List of reward items and a message
        """
        rewards = enemy.get_drop_items()
        
        reward_items = []
        for item in rewards:
            if isinstance(item, str):
                reward_items.append({
                    "name": item,
                    "description": 'a coin',
                    "item": item
                })
            else:
                reward_items.append({
                    "name": item.name,
                    "description": item.description,
                    "item": item
                })
        
        def _get_item_display_name(item):
            if isinstance(item, str):
                return item
            if getattr(item, 'display_name', ''):
                return item.display_name
            return item.name

        # Generate a message
        if not rewards:
            msg = f"You defeated {enemy.name} but found no items."
        elif len(rewards) == 1:
            reward_name = _get_item_display_name(rewards[0])
            msg = f"You defeated {enemy.name} and found: {reward_name}!"
        else:
            items_str = ", ".join([_get_item_display_name(item) for item in rewards])
            msg = f"You defeated {enemy.name} and found: {items_str}!"
        
        return reward_items, msg