import re
import numpy as np
from collections import defaultdict
from envs.cuterpg.utils.assets.label_to_description import LABEL_TO_DESCRIPTION, WINTER_LABEL_TO_DESCRIPTION
from pdb import set_trace as st


def get_first_person(pos, direction, map_data, season, MAP_ROWS, MAP_COLS, TILE_SIZE):
    (x, y) = pos
    agent_tile_x = x // TILE_SIZE
    agent_tile_y = y // TILE_SIZE

    start_x = (agent_tile_x - 1) * TILE_SIZE
    start_y = (agent_tile_y - 1) * TILE_SIZE
    end_x = (agent_tile_x + 2) * TILE_SIZE
    end_y = (agent_tile_y + 2) * TILE_SIZE

    observation = []

    for ny in range(start_y, end_y):
        row = []
        for nx in range(start_x, end_x):
            if 0 <= nx < MAP_COLS * TILE_SIZE and 0 <= ny < MAP_ROWS * TILE_SIZE:
                if x-1<=nx<=x+1 and y-1<=ny<=y+1:
                    row.append('agent')
                else:
                    row.append(map_data[season][ny][nx])
            else:
                row.append("void")
        observation.append(row)


    if direction == 'east':
        observation = [list(row) for row in zip(*observation)][::-1]
    elif direction == 'west':
        observation = [list(row) for row in zip(*observation[::-1])]
    elif direction == 'south':
        observation = [row[::-1] for row in observation[::-1]]

    return observation

def encode_obs(matrix,
               season,
               include_void=False,
               include_small_items=False,
               mode='full',
               return_lst=False): #either provide full information or only a part of it
    """
    Encode a 3x3 grid observation into detailed spatial descriptions.

    Parameters:
    - observation: List of Lists (3x3) where each entry is a tile description.

    Returns:
    - List of descriptive strings for each tile relative to the agent.
    """
    # Define relevant tiles to include in the description
    matrix = np.array(matrix)
    reshaped = matrix.reshape(3, 6, 3, 6)
    matrix = reshaped.transpose(0, 2, 1, 3)
    
    # Map positions to human-readable directions
    position_map = {
        (0, 0): "front-left",
        (0, 1): "front",
        (0, 2): "front-right",
        (1, 0): "left",
        (1, 1): "center",
        (1, 2): "right",
        (2, 0): "back-left",
        (2, 1): "back",
        (2, 2): "back-right"
    }

    # Regex pattern for house (e.g., house_1, house_2), destination, and tree detection
    possible_patterns = [   re.compile(r'house_\d+'), 
                            re.compile(r'.*tree.*'),
                            re.compile(r'destination'),
                            re.compile(r'void'),
                            re.compile(r'road'),
                            re.compile(r'construction'),
                            re.compile(r'snow'),
                            re.compile(r'ice'),
                            re.compile(r'light'),
                            re.compile(r'npc'),
                        ]
    objects = np.unique(matrix)
    shared_tiles = defaultdict(list)
    # tree, houses, and destination and 
    for obj in objects:
        if any([pattern.match(obj) for pattern in possible_patterns]):
            for i in range(3):
                for j in range(3):
                    cell_vals = np.unique(matrix[i][j])
                    if obj in cell_vals:
                        if obj == 'road' and any('construction' in str(x) for x in cell_vals):
                            continue
                        shared_tiles[obj].append((i, j))

    descriptions = ['You can see the 3x3 tiles surrounding you:']
    objs = set()
    for obj in shared_tiles:
        # The house spans the front and front-left tiles.
        obj_tiles = shared_tiles[obj]
        pos_info = ', '.join([position_map[tile] for tile in obj_tiles if tile != (1, 1)])
        if obj == 'void':
            if include_void:
                descriptions.append(f"The {pos_info} tiles are out of the map boundary.")
        elif obj == 'road':
            if ',' not in pos_info:
                descriptions.append(f"The {pos_info} tile is road that you can step on.")
            else:
                descriptions.append(f"The {pos_info} tiles are roads that you can step on.")
        elif obj == 'destination':
            if len(obj_tiles) > 1:
                descriptions.append(f"The destination spans the {pos_info} tiles.")
            else:
                descriptions.append(f"The destination is on the {pos_info} tile.")
        elif obj == 'construction':
            descriptions.append(f"In the {pos_info} tile there is a pointed construction cone with bold red and white stripes, indicating the road is under construction.")
        elif obj.startswith('npc'):
            if ',' not in pos_info:
                descriptions.append(f"There is a pedestrian standing on the {pos_info} tile.")
            else:
                descriptions.append(f"There is a pedestrian standing on the {pos_info} tiles.")
        else:
            obj_no_idx = re.sub(r'_\d+', '', obj)
            obj = obj_no_idx
            if 'house' not in obj_no_idx:
                color = obj_no_idx.split('_')[-1]
                obj_no_idx = '_'.join(obj_no_idx.split('_')[:-1])
                if season == 'summer':
                    obj_no_idx = LABEL_TO_DESCRIPTION[obj_no_idx].format(color=color)
                else:
                    obj_no_idx = WINTER_LABEL_TO_DESCRIPTION[obj_no_idx].format(color=color)
            if obj_no_idx:
                describe = 'a' if obj not in objs else 'another'
                if len(obj_tiles) == 1:
                    descriptions.append(f"There is {describe} {obj_no_idx} on the {pos_info} tile.")
                else:
                    descriptions.append(f"There is {describe} {obj_no_idx} that spans the {pos_info} tiles.")
        objs.add(obj)

    if return_lst:
        return descriptions

    return descriptions
