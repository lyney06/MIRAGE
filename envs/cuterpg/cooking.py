import gym
import pygame
from .Cooking.config import WINDOW_WIDTH, WINDOW_HEIGHT
from .Cooking.character import Character
from .Cooking.map import GameMap
from .Cooking.env import Env
from pdb import set_trace as st

class CookingEnv(gym.Env):
    def __init__(self, **kwargs):
        super(CookingEnv, self).__init__()

        self.mode = kwargs["mode"]
        self.crop_gone = kwargs.get("crop_gone", False)
        self.novice_mistake = kwargs.get("novice_mistake", False)
        self.storage_loss = kwargs.get("storage_loss", False)
        self.n_servings = kwargs.get("n_servings", 1)

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Cooking")

        self.env = Env( self.mode,
                        self.crop_gone,
                        self.novice_mistake,
                        self.storage_loss,
                        self.n_servings,
                        )

    def step(self, action):
        obs, reward, done, info = self.env.take_action(action)
        self.update_screen()
        return obs, reward, done, info
    
    def get_status(self):
        res = self.env.take_action('status')
        if isinstance(res, tuple):
            return res[0]
        return res
    
    def reset(self):
        obs = self.env.reset()
        self.update_screen()
        return obs
    
    def back_to_start(self):
        obs = self.env.rewind()
        self.update_screen()
        return obs
    
    def update_screen(self):
        self.screen.fill((0, 0, 0))
        self.env.map.draw(self.screen)
        self.env.character.draw(self.screen)
        self.env.farm.draw(self.screen)
        self.env.fishing.draw(self.screen)
        pygame.display.flip()

    def get_manual(self,
                   manual_type):
        return self.env.get_manual(manual_type), ""
    
    def get_horizon(self):
        return self.env.get_horizon()
    
    def simulate_env_variants(self):
        self.env.simulate_env_variants()
