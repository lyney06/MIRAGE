# RL_environment.py
import re
import random
import copy 
import numpy as np
from .observation import encode_obs
from .path_converter import convert_path_to_instructions
from pdb import set_trace as st

class Env:
    def __init__(self, game_map, 
                       character, 
                       npc_manual_lst,
                       obs_type='raw',
                       ):
        self.game_map = game_map
        self.character = character
        self.num_rounds = 0
        self.last_obs = None
        self.obs_type = obs_type
        self.npc_manual_lst = npc_manual_lst
        self.initial_map = None
        self.initial_character= None
            
    def get_max_round(self):
        self.max_round = 4 * self.game_map.estimate_step
        if self.game_map.dynamic:
            self.max_round *= 2
        if self.game_map.construction:
            self.max_round += 20
        return self.max_round

    def reset(self):
        self.game_map.reset()
        self.character.reset()
        self.initial_map = copy.deepcopy(self.game_map.map_data)
        self.num_rounds = 0
        self.get_max_round()
        return self.character.get_observation()


    def goal_completed(self):
        # at the cloest road to the destimation
        closet = self.game_map.closet_to_goal_tiles()
        return self.character.position in closet
    
    def _format_obs_from_character(self):
        raw_obs = self.character.get_observation()
        if self.obs_type == 'raw':
            next_obs = self.matrix_to_string(raw_obs)
        else:
            next_obs = self.encode_obs(raw_obs)
        next_obs += f"\nDirection: You are facing {self.character.direction}."
        return next_obs

    def take_action(self, action):
        reward = 0
        action = action.strip()
        if action not in ['reset', 'void']:
            self.game_map.step_before()

        next_obs = None
        if action in ['forward', 'turn left', 'turn right', 'turn around']:
            self.character.move(action)
        elif action == "reset":
            self.reset()
            # reset rebuilds the world; observe immediately (no dynamic step_after).
            next_obs = self._format_obs_from_character()
        elif action == "wait":
            pass
        elif action == 'void':
            next_obs = self._format_obs_from_character()
        elif action == 'inquire_npc':
            # NOTE: NPC inquiry is currently experimental and not yet fully wired up.
            # Missing pieces: proximity/facing validation, exposure in get_available_actions(), and agent prompt integration.
            manual_type = random.choice(self.npc_manual_lst)
            next_obs = self.game_map.get_npc_manual(
                manual_type,
                self.character.position,
                self.character.direction,
            )
        # else: invalid action — no movement; still advance dynamics below.

        # Pedestrians/lights update before we emit the observation so the agent
        # sees the same world state that Available Actions is computed from.
        if action not in ['reset', 'void']:
            self.game_map.step_after(self.character.position)

        if next_obs is None:
            next_obs = self._format_obs_from_character()

        self.num_rounds += 1
        info = {}
        done = self.goal_completed()
        if self.num_rounds > self.max_round:
            done = True
            info['horizon'] = 'exceeds longest horizon.'

        if done:
            dist = self.game_map.dist_to_goal(self.character.position)
            reward = 1 - (dist/(self.game_map.MAP_ROWS + self.game_map.MAP_COLS))

        self.last_obs = next_obs
        return next_obs, reward, done, info

    def gt_instructions(self):
        """Steps"""
        return convert_path_to_instructions(self.game_map.path)

    def descriptive_manual(self):
        return self.game_map.gt_manual

    def matrix_to_string(self, matrix):
        return '\n'.join([' '.join(row) for row in matrix])
    
    def string_to_matrix(self, matrix_str):
        return [line.strip().split() for line in matrix_str.strip().split('\n')]

    def encode_obs(self, matrix):
        obs = encode_obs(matrix,
                         self.game_map.season,
                         include_void=True,
                         include_small_items=True,
                         )
        obs = '\n'.join(obs)
        return obs