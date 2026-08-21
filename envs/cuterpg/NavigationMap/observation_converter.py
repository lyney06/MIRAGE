# observation_converter.py
import re
import random
import numpy as np
from ..utils.config import TILE_SIZE
from .observation import encode_obs, get_first_person
from .utils import fix_another_usage
from pdb import set_trace as st

def convert_obs_to_manual(map_data,
                          season,
                          start_pos, 
                          instructions,
                          imperfect_info,
                          MAP_ROWS,
                          MAP_COLS,
                          dir='east',
                          manual_type='obs_only', # obs_only, obs_wrong_step
                          ):
    manual = []
    pos = np.array(start_pos)
    tile_step = {'east': (TILE_SIZE, 0), 'south': (0, TILE_SIZE), 'west': (-TILE_SIZE, 0), 'north': (0, -TILE_SIZE)}

    if manual_type == 'obs_only':
        for idx, instr in enumerate(instructions):
            if "Turn " in instr:
                dir = instr.split('to face ')[1][:-1]
                manual.append(f"Turn until you are facing {dir}.")
            elif "Move forward " in instr:
                match = re.search(r"Move forward (\d+) tile", instr)
                num_tiles = int(match.group(1))
                match_dir = re.search(r"\((\w+)\)", instr)
                if match_dir:
                    dir = match_dir.group(1)
                pos += np.array(tile_step[dir]) * num_tiles
                obs = get_first_person(pos, dir, map_data, season, MAP_ROWS, MAP_COLS, TILE_SIZE)
                encoded_obs = encode_obs(obs,
                                        season)
                encoded_obs = ' '.join(encoded_obs[1:])
                manual.append(f"Walk forward (toward {dir}) until you see {encoded_obs.lower()}")
        if manual and manual[-1].startswith('Walk forward '):
            manual.pop()
        manual.append(f"Walk forward (toward {dir}) until you are close to the destination.")

    elif manual_type == 'obs_wrong_step':
        for idx, instr in enumerate(instructions):
            if "Turn " in instr:
                dir = instr.split('to face ')[1][:-1]
                manual.append(f"Turn until you are facing {dir}.")

            elif "Move forward " in instr:
                match = re.search(r"Move forward (\d+) tile", instr)
                tile_count = int(match.group(1))
                match_dir = re.search(r"\((\w+)\)", instr)
                if match_dir:
                    dir = match_dir.group(1)
                if imperfect_info[idx]:
                    delta_count = imperfect_info[idx][0]
                else:
                    delta_count = 0
                pos += np.array(tile_step[dir]) * (tile_count - delta_count)
                obs = get_first_person(pos, dir, map_data, season, MAP_ROWS, MAP_COLS, TILE_SIZE)
                encoded_obs = encode_obs(obs, season, return_lst=True)
                candidates = encoded_obs[1:]
                distinct_obs = [
                    item for item in candidates
                    if "road that you can step on" not in item
                    and "roads that you can step on" not in item
                    and "out of the map boundary" not in item
                ]
                if len(distinct_obs) >= 2:
                    sampled_obs = random.sample(distinct_obs, 2)
                elif len(distinct_obs) == 1:
                    remaining = [item for item in candidates if item not in distinct_obs]
                    if remaining:
                        sampled_obs = distinct_obs + random.sample(remaining, 1)
                    else:
                        sampled_obs = distinct_obs
                else:
                    sampled_obs = random.sample(candidates, min(2, len(candidates))) if candidates else []

                encoded_obs = fix_another_usage(sampled_obs)
                if len(encoded_obs) == 2:
                    encoded_obs = f"{encoded_obs[0][:-1]} and {encoded_obs[1][:-1]}."
                elif len(encoded_obs) == 1:
                    encoded_obs = ' '.join(encoded_obs)
                    encoded_obs = encoded_obs[:-1] + '.'
                else:
                    encoded_obs = ""
                tile_str = "tile" if tile_count == 1 else "tiles"
                manual.append(f"Walk forward (toward {dir}) {tile_count} {tile_str}, after that you will see {encoded_obs}")

        if manual and manual[-1].startswith('Walk forward '):
            last_step = manual.pop()
            match = re.search(r" (\d+) tile", last_step)
            tile_count = int(match.group(1))
            tile_str = "tile" if tile_count == 1 else "tiles"
            manual.append(f"Walk forward (toward {dir}) {tile_count} {tile_str} to get close to the destination.")
            

    instruction = '\n'.join([f'Step {i+1}. {manual[i]}' for i in range(len(manual))])
    return instruction

