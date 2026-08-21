# observation.py
import copy
from pdb import set_trace as st

class Observation:
    def __init__(self, character, kitchen, farm, store, harbor):
        self.character = character
        self.kitchen = kitchen
        self.farm = farm
        self.store = store
        self.harbor = harbor
        self.last_location = 'task start'
        self.last_ingredients = 'task start'

    def get_full_observation(self, force=False):
        obs_lines = []

        position = self.character.position

        if force or position != self.last_location:
            env_obs = ''
            if position == 'kitchen':
                env_obs = self.kitchen.get_kitchen_observation()
            elif position == 'farm':
                env_obs = self.farm.get_farm_observation()
            elif position == 'store':
                env_obs = self.store.get_store_observation()
            elif position == 'harbor':
                env_obs = "You are by the harbor, ready to fish."

            if env_obs:
                obs_lines.append(env_obs)

        if force or (position != self.last_location) or (self.character.ingredients != self.last_ingredients):
            self_obs = self.character.get_self_observation()
            if self_obs:
                obs_lines.append(self_obs)

        self.last_location = position
        self.last_ingredients = copy.deepcopy(self.character.ingredients)

        obs = '\n'.join(obs_lines)
        obs = obs.strip()
        return obs