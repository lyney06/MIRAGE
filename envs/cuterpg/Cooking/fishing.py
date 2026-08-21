# fishing.py

import random
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE
from envs.cuterpg.utils.tileset import TileSet
from .utils import singularize, pluralize
from pdb import set_trace as st

class Fishing:
    def __init__(self, map, available_seafood=[]):
        self.map = map
        self.available_seafood = available_seafood

        self.num_positions = 3
        self.position_status = []

        for _ in range(self.num_positions):
            self.position_status.append(random.choice(['occupied', 'empty']))

        if 'empty' not in self.position_status:
            self.position_status[random.randint(0, self.num_positions - 1)] = 'empty'

        self.position_coordinates = [(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2 + 12 * GRID_SIZE),
                                     (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 12 * GRID_SIZE), 
                                     (WINDOW_WIDTH // 4 * 3, WINDOW_HEIGHT // 2 + 12 * GRID_SIZE)]
        self.attempts = {}
        self.tilesets = TileSet()
        all_npc = self.tilesets.get_npc()
        self.npc_list = random.sample(all_npc, self.num_positions)

    def draw(self, screen):
        for idx, status in enumerate(self.position_status):
            if status == 'occupied':
                npc_image = self.npc_list[idx]
                screen.blit(npc_image, self.position_coordinates[idx])

    def get_available_harbor(self):
        empty_indices = [i + 1 for i, status in enumerate(self.position_status) if status == 'empty']
        return empty_indices


    def fishing(self, character, goal_seafood):
        info = ''

        if character.position != 'harbor':
            info = "You can only fish by the harbor."
            return False, info

        goal_seafood = singularize(goal_seafood)

        # Check is it's in FISHABLE_INGREDIENTS
        if goal_seafood not in self.available_seafood:
            info = f"{goal_seafood.capitalize()} can't be found in the waters today."
            return False, info

        # Get current attempts for this seafood
        current_attempts = self.attempts.get(goal_seafood, 0)

        if current_attempts < 2:
            outcome = random.choices(
                ['success', 'fail', 'wrong_seafood'],
                weights=[0.4, 0.3, 0.3]
            )[0]

            if outcome == 'success':
                info = f"You reeled in some fresh {pluralize(goal_seafood)}!"
                character.get_ingredient({f'raw {goal_seafood}': {  'state': ['raw'], 
                                                                    'name': goal_seafood,
                                                                    'serving': 100}})
                self.attempts[goal_seafood] = 0
                return True, info

            elif outcome == 'fail':
                info = random.choice([
                    "The sea was quiet... try again.",
                    "Nothing took the bait this time.",
                    "You waited, but caught nothing."
                ])
                self.attempts[goal_seafood] = current_attempts + 1
                return False, info

            elif outcome == 'wrong_seafood':
                wrong_choices = [s for s in self.available_seafood if s != goal_seafood]
                if wrong_choices:
                    wrong_pick = random.choice(wrong_choices)
                    info = f"You pulled up some {pluralize(wrong_pick)} instead."
                    character.get_ingredient({f'raw {wrong_pick}': {'state': ['raw'], 
                                                                    'name': wrong_pick,
                                                                    'serving': 100}})
                else:
                    info = "Something tugged the line, but it slipped away..."
                self.attempts[goal_seafood] = current_attempts + 1
                return False, info

        else:
            info = f"Persistence pays off! You landed some fresh {pluralize(goal_seafood)}!"
            character.get_ingredient({f"raw {goal_seafood}": {  'state': ['raw'], 
                                                                'name': goal_seafood,
                                                                'serving': 100}})
            self.attempts[goal_seafood] = 0
            return True, info
