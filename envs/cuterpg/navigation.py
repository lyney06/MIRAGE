import re
import copy
import gym
import pygame
from collections import Counter, defaultdict
from .utils.config import TILE_SIZE
from .utils.charactersprite import CharacterSprite
from .NavigationMap.navigationMap import GameMap
from .NavigationMap.main_character import NavigationCharacter
from .NavigationMap.env import Env
from envs.cuterpg.utils.assets.label_to_description import LABEL_TO_DESCRIPTION, WINTER_LABEL_TO_DESCRIPTION

from pdb import set_trace as st

class NavigationEnv(gym.Env):
    def __init__(self, **kwargs):
        super(NavigationEnv, self).__init__()
        
        self.obs_type = kwargs["obs_type"]
        self.mode = kwargs.get("mode", 'hard')
        self.seasons = kwargs.get("seasons", ["summer"])
        self.dynamic = kwargs.get("dynamic", False)
        self.npc = kwargs.get("npc", 0)
        npc_manual_lst = kwargs.get('npc_manual_lst', [1, 2])
        construction = kwargs.get('construction', False)
        window_width = kwargs.get('window_width', 600)
        window_height = kwargs.get('window_height', 600)
        max_land_size = kwargs.get('max_land_size', 4)
        min_land_size = kwargs.get('min_land_size', 2)
        map_rows = kwargs.get('map_rows', 12)
        map_cols = kwargs.get('map_cols', 12)
        
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Navigation Map")

        self.character_sprite = CharacterSprite()
        self.game_map = GameMap(self.screen,
                                self.seasons,
                                self.dynamic,
                                self.npc,
                                self.mode,
                                construction,
                                max_land_size=max_land_size,
                                min_land_size=min_land_size,
                                map_rows=map_rows,
                                map_cols=map_cols,
                                )
        self.character = NavigationCharacter(self.character_sprite, self.game_map, step_size=TILE_SIZE)
        self.env = Env(self.game_map, self.character, npc_manual_lst, obs_type=self.obs_type)
    
    def record_initial(self):
        self.initial_pos = self.character.position
        self.initial_dir = self.character.direction
        
    def get_available_actions(self):
        actions = [
            'turn left',
            'turn right',
            'turn around',
            'wait',
        ]

        x, y = self.character.position

        tile_x = x // TILE_SIZE
        tile_y = y // TILE_SIZE

        direction_to_delta = {
            'north': (0, -1),
            'south': (0, 1),
            'west': (-1, 0),
            'east': (1, 0),
        }

        dx, dy = direction_to_delta[self.character.direction]

        front_tile_x = tile_x + dx
        front_tile_y = tile_y + dy

        # front tile inside map
        if (
            0 <= front_tile_x < self.game_map.MAP_COLS
            and 0 <= front_tile_y < self.game_map.MAP_ROWS
        ):
            front_px_x = front_tile_x * TILE_SIZE
            front_px_y = front_tile_y * TILE_SIZE

            if self.game_map.is_pure_tile(
                front_px_y,
                front_px_x,
                'road'
            ):
                actions.insert(0, 'forward')

        return actions


    def reset(self):
        done = True
        while done:
            # in case a task diectly succeeds
            obs, reward, done, info = self.env.take_action('reset')
        self.update_screen()
        self.switch_season()
        # need to get the observation here in case the season is changed
        obs, reward, done, info = self.env.take_action('void')
        self.record_initial()
        self.update_screen()
        self.build_partial_map()
        self.update_partial_map()
        return obs
    
    def build_partial_map(self):
        self.partial_map = copy.deepcopy(self.game_map.map_data)
        for season in self.partial_map:
            m, n = len(self.partial_map[season]), len(self.partial_map[season][0])
            for i in range(m):
                for j in range(n):
                    self.partial_map[season][i][j] = 'unknown'
        return 
        
    def update_partial_map(self):
        # from the currrent position of the agent, fill the corresponding partial map with gt information 
        y, x = self.character.position
        x, y = x//TILE_SIZE, y//TILE_SIZE
        m, n = len(self.partial_map[self.game_map.get_season()]), len(self.partial_map[self.game_map.get_season()][0])
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if x+dx < 0 or x+dx >= m//TILE_SIZE or y+dy < 0 or y+dy >= n//TILE_SIZE:
                    continue
                for ddx in range(TILE_SIZE):
                    for ddy in range(TILE_SIZE):
                        try:
                            self.partial_map[self.game_map.get_season()][TILE_SIZE*(x+dx)+ddx][TILE_SIZE*(y+dy)+ddy] = self.game_map.map_data[self.game_map.get_season()][TILE_SIZE*(x+dx)+ddx][TILE_SIZE*(y+dy)+ddy]
                        except IndexError as e:
                            pass
        return 
        
    
    def rewind(self):
        # go back to the initial state
        self.character.position = self.initial_pos
        self.character.direction = self.initial_dir
        obs, reward, done, info = self.env.take_action('void')
        self.build_partial_map()
        return obs, reward, done, info
    
    def back_to_start(self):
        self.env.game_map.map_data = self.env.initial_map
        # self.character = self.initial_character
        self.env.num_rounds = 0
        obs = self.rewind()[0]
        self.update_screen()
        return obs

    def get_horizon(self):
        return self.env.get_max_round()

    def step(self, action):
        obs, reward, done, info = self.env.take_action(action)
        self.update_partial_map()
        self.update_screen()
        return obs, reward, done, info
    
    def get_gt_mode(self):
        status = self.env.game_map.get_map_manual_status(self.character.position,
                                       self.character.direction)
        return status
    
    def get_gt_action(self):
        action = self.env.game_map.move_towards_goal(self.character.position, 
                                                     self.character.direction)
        return action
    
    def switch_season(self):
        self.game_map.switch_season()

    def update_screen(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw()
        self.character.draw(self.screen)
        pygame.display.flip()

    def get_manual(self, manual_type):
        if manual_type is None:
            return '', ''
        manual, imperfect_info = self.env.game_map.get_npc_manual(manual_type,
                                                                      self.character.position,
                                                                      self.character.direction)
        if self.character.position != self.game_map.start_position:
            self.character.position = self.game_map.start_position
            self.character.direction = 'east'
            self.record_initial()
            self.build_partial_map()
            self.update_partial_map()
            self.update_screen()
            self.env.initial_map = copy.deepcopy(self.game_map.map_data)
            self.env.num_rounds = 0
            self.env.get_max_round()
        # for this specific manual, let's generate gt mode map
        return manual, imperfect_info
    
    
    def get_partial_map(self):
        season = self.env.game_map.get_season()
        pixel_map = self.partial_map[season]  # shape: [H=72][W=72]
        H, W = len(pixel_map), len(pixel_map[0])
        grid_H, grid_W = H // TILE_SIZE, W // TILE_SIZE

        agent_x, agent_y = self.character.position  # pixel-level
        agent_tile_x = agent_x // TILE_SIZE
        agent_tile_y = agent_y // TILE_SIZE
        
        init_x, init_y = self.initial_pos
        init_tile_x, init_tile_y = init_x//TILE_SIZE, init_y//TILE_SIZE

        # Symbol maps
        static_symbols = {
            'road': 'R',
            'unknown': 'UN',
            'destination': 'D',
            'construction': 'C',
            'npc': 'P',
        }

        legend = {'UN': 'unknown'}
        grid = []

        label_to_symbol = {}  # Global mapping from full label to consistent symbol
        symbol_counter = defaultdict(int)  # Separate counters per type: tree, house, etc.

        for gy in range(grid_H):
            row = []
            for gx in range(grid_W):
                label_set = set()
                for dy in range(TILE_SIZE):
                    for dx in range(TILE_SIZE):
                        py = gy * TILE_SIZE + dy
                        px = gx * TILE_SIZE + dx
                        if 0 <= py < H and 0 <= px < W:
                            label = pixel_map[py][px]
                            label_set.add(label)

                # Agent location
                if (gx, gy) == (agent_tile_x, agent_tile_y):
                    cell = ["A"]
                    legend['A'] = "Agent (current position)"
                else:
                    cell = []
                    
                if (gx, gy) == (init_tile_x, init_tile_y):
                    cell.append("IA")
                    legend['IA'] = "Agent's initial position"

                for label in label_set:
                    if label in static_symbols:
                        sym = static_symbols[label]
                        legend[sym] = label
                        if label == 'construction':
                            legend[sym] = 'a pointed construction cone with bold red and white stripes, indicating the road is under construction and not traversable.'
                            
                    elif 'house' in label or 'tree' in label or 'light' in label:
                        # Use shared label-to-symbol map
                        if label not in label_to_symbol:
                            if 'house' in label:
                                base_type = 'H'
                            elif 'tree' in label:
                                base_type = 'T'
                            elif 'light' in label:
                                base_type = 'DL'
                            symbol_counter[base_type] += 1
                            sym = f"{base_type}{symbol_counter[base_type]}"
                            label_to_symbol[label] = sym

                            # Build legend entry
                            if 'tree' in label or 'light' in label:
                                # Parse tree type and color
                                obj_no_idx = re.sub(r'_\d+', '', label)  # remove _1, _2
                                parts = obj_no_idx.split('_')
                                if len(parts) >= 2:
                                    color = parts[-1]
                                    base = '_'.join(parts[:-1])
                                    if season == 'summer':
                                        desc_template = LABEL_TO_DESCRIPTION.get(base, base)
                                    else:
                                        desc_template = WINTER_LABEL_TO_DESCRIPTION.get(base, base)
                                    full_desc = desc_template.format(color=color)
                                    legend[sym] = full_desc
                                else:
                                    legend[sym] = obj_no_idx
                            elif 'house' in label:
                                legend[sym] = 'House'
                        else:
                            sym = label_to_symbol[label]
                    else:
                        sym = 'L'

                    cell.append(sym)

                # Remove 'L' if it's co-occurring with other symbols
                if set(cell) == set(['L']):
                    legend['L'] = 'Land'
                    cell = ['L']
                elif 'C' in cell and 'R' in cell:
                    cell = [xx for xx in cell if xx != 'R']
                if 'L' in cell:
                    cell = [s for s in cell if s != 'L']

                row.append(','.join(sorted(cell)))
            grid.append(row)

        lines = []
        lines.extend(  ["This is a partial map constructed from your navigation history.\n"
                        "It is presented as a 12x12 top-down 2D grid.\n"
                        "Each cell represents one grid tile of the environment. A grid can contain multiple objects, "
                        "and a single object (like a house or tree) can span across multiple grid tiles.\n"
                        "The map is always oriented with **north at the top and south at the bottom**\n"
                        f"The agent is currently facing: **{self.character.direction}**.\n"]
        )

        for i, row in enumerate(grid):
            lines.append(f"Row {i}: " + '  '.join(f"{cell:8}" for cell in row))

        # Merge symbols by shared description
        desc_to_symbols = defaultdict(list)
        for symbol, description in sorted(legend.items()):
            desc_to_symbols[description].append(symbol)

        lines.append("\nLegend:")
        for desc, symbols in sorted(desc_to_symbols.items(), key=lambda x: x[0]):
            merged = ', '.join(sorted(symbols))
            lines.append(f"{merged:15} = {desc}")

        output_str = '\n'.join(lines)
        return output_str  # or: return lines if you want a list of strings
    