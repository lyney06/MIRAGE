import cv2
import pygame
import numpy as np
import textwrap
from llmagentbase.agent.base import Agent
from pdb import set_trace as st


class Chef(Agent):
    def __init__(   self, 
                    env,
                    instruction,
                    in_context,
                    logger,
                    model_name,
                    temperature,
                    manual_type
                    ):
        super().__init__(env,
                        instruction,
                        in_context,
                        logger,
                        model_name,
                        temperature)
        self.manual_type = manual_type
        self.mode_recs = []

    def construct_prompt(self,
                         traj
                        ):
        if ('qwen3' in self.model_name.lower() or 'deepseek' in self.model_name.lower()) and "Warning: Do not put" not in self.instruction:
            self.instruction += "\nWarning: Do not put 'Observation:' in your answer as your answer will be truncated!"
        if self.manual_type is None:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\n"
        else:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nRecipe of the required dish(es):\n{self.manual}\n\nTry your best to complete the required dish(es):\n"

        prompt += f"{traj}\nAction: "
        return prompt
    
    def reset_env(self):
        reward, done, info = 0, False, {}
        epi_history = []
        observation = self.env.reset()
        self.manual, self.imperfect_info = self.env.get_manual(self.manual_type)
        self.env.simulate_env_variants()
        self.logger.colored_log("Loaded Manual:", self.manual, color="yellow")
        self.logger.colored_log("Imperfect Info:", self.imperfect_info, color="yellow")
        self.logger.colored_log("Horizon:", self.env.get_horizon(), color="green")
        return observation, reward, done, info, epi_history
    
    def log_frame(self, action, step, add_to_history=True):
        return