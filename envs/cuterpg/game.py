from typing import Optional
import gym
from .RoguelikeRPG.env import Env
from pdb import set_trace as st

class GameEnv(gym.Env):
    """
    Gym-compatible environment wrapper for the RPG game.
    Provides a standard RL interface.
    """

    def __init__(self, **kwargs):
        """
        Initialize the game environment.
        
        Args:
            **kwargs: Keyword arguments passed to Env
        """
        super(GameEnv, self).__init__()
        self.mode = kwargs.get("mode", 'easy')
        self.shuffle_container = kwargs.get("shuffle_container", False)
        self.single_level_enemy = kwargs.get("single_level_enemy", 1)
        self.shuffle_enemy = kwargs.get("shuffle_enemy", False)
        self.reversible = kwargs.get("reversible", False)
        self.item_rename = kwargs.get("item_rename", False)
        self.seed = kwargs.get("seed", None)
        self.neat = kwargs.get("neat", False)
        if hasattr(self, "spec") and self.spec is not None:
            if "neat" in self.spec.id.lower():
                self.neat = True
        self.env = Env(self.mode,
                       seed=self.seed,
                       shuffle_container=self.shuffle_container,
                       single_level_enemy=self.single_level_enemy,
                       shuffle_enemy=self.shuffle_enemy,
                       reversible=self.reversible,
                       item_rename=self.item_rename,
                       neat=self.neat)

    def set_seed(self, seed: int) -> None:
        """Set the random seed used for game generation and dynamics."""
        self.seed = seed
        self.env.seed = seed

    def step(self, action):
        """
        Take a step in the environment.
        
        Args:
            action: Action to take (string)
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        obs, reward, done, info = self.env.take_action(action)
        return obs, reward, done, info

    def reset(self, seed: Optional[int] = None):
        """
        Reset the environment.
        
        Args:
            seed: Optional random seed for reset
        Returns:
            Initial observation
        """
        if seed is not None:
            self.set_seed(seed)
        if hasattr(self, "spec") and self.spec is not None:
            if "neat" in self.spec.id.lower():
                self.neat = True
                self.env.neat = True
                if hasattr(self.env, "game") and self.env.game is not None:
                    self.env.game.neat = True
                    for level in self.env.game.levels:
                        level.neat = True
        return self.env.reset(seed=seed)
    
    def back_to_start(self):
        self.env.game = self.env.initial_game

    def get_available_actions(self):
        """Return the fully-specified, state-dependent action list for the current level."""
        return self.env.get_available_actions()
    
    def render(self, mode='human'):
        """
        Render the environment.
        
        Args:
            mode: Rendering mode
        """
        print(self.env.observation)
        
    def get_status(self):
        inventory = f"Your current inventory:\n{self.env.game.player.inventory}\n\n"
        level = self.env.game.get_current_level()
        obs = level.get_curr_obs()
        return f"{inventory}You are at Level {level.level_number}: \n{obs}"
    
    def close(self):
        """Clean up resources."""
        pass
    
    def get_manual(self, manual_type=None):
        """
        Get a manual for the environment.
        
        Args:
            manual_type: Type of manual to retrieve
            
        Returns:
            Tuple of (manual_text, additional_info)
        """
        manual = self.env.get_manual(manual_type)
        obs = self.env.reset_void()
        return obs, manual
    
    def get_horizon(self):
        return self.env.get_horizon()