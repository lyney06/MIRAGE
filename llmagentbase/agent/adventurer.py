import numpy as np
from .base import Agent
from pdb import set_trace as st


class Adventurer(Agent):
    def __init__(self, 
                env,
                instruction,
                in_context,
                logger,
                model_name,
                temperature,
                manual_type=0
                ):
        super().__init__(env,
                        instruction,
                        in_context,
                        logger,
                        model_name,
                        temperature)
        self.manual_type = manual_type
        self.game_history = []
        self.action_stats = {}
        self.available_actions = []
        self.mode_recs = []

    def construct_prompt(self, traj):
        if self.manual_type is None:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nSomething useful:\n{self.manual}\n\nTry your best to complete the game:\n"
        else:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nStrategy Guide for Roguelike Game:\n{self.manual}\n\nTry your best to complete the game:\n"
        prompt += f"{traj}\nAction: "
        return prompt
    
    def reset_env(self):
        reward, done, info = 0, False, {}
        epi_history = []

        observation = self.env.reset()
        observation, self.manual = self.env.get_manual(self.manual_type)
        self.logger.colored_log("Loaded Strategy Guide:", self.manual, color="yellow")
        self.logger.colored_log("Max Steps:", self.env.get_horizon(), color="green")
        
        # Keep available actions up to date at reset (step 0)
        if hasattr(self.env, 'get_available_actions'):
            self.available_actions = self.env.get_available_actions()
        elif hasattr(self.env, 'unwrapped') and hasattr(self.env.unwrapped, 'get_available_actions'):
            self.available_actions = self.env.unwrapped.get_available_actions()
            
        return observation, reward, done, info, epi_history
    
    def process_game_info(self, info):
        """Process game state information to track available actions"""
        return ""
    
    def process_input(self, 
                      epi_history,
                      info,
                      i):
        # Update self.available_actions from the info dictionary
        self.process_game_info(info)
        return ''.join(epi_history)
    
    def log_frame(self, action, step, add_to_history=True):
        return