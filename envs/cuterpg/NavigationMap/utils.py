import re
import random
from collections import defaultdict
from ..utils.config import GRID_SIZE, TILE_SIZE, CHARACTER_WIDTH, CHARACTER_HEIGHT
from pdb import set_trace as st

def change_tile_num(tile_count, wrong_tiles, ranges=[-1, 0, 1]):
    change = 0
    if not wrong_tiles:
        return change, tile_count
    change = random.choice(ranges)
    return change, tile_count + change


def fix_another_usage(encoded_obs):
    object_counts = defaultdict(int)
    new_encoded_obs = []

    for line in encoded_obs:
        if line.startswith("There is "):
            # 'There is a/another xxx that ... or There is a/another xxx on ...'
            match = re.match(r"There is (a|another) (.+?)(?: that| on| at| spanning| across)", line)
            if match:
                a_or_another = match.group(1)  # 'a' or 'another'
                object_name = match.group(2).strip()  # the full object description

                object_counts[object_name] += 1

                if object_counts[object_name] == 1:
                    # 'a' for the first one
                    if a_or_another == 'another':
                        line = line.replace('another', 'a', 1)
                else:
                    # 'another' for the second or more ones
                    if a_or_another == 'a':
                        line = line.replace(' a ', ' another ', 1)
        if line.startswith("There is "):
            line = line.replace('There is ', '', 1)
        new_encoded_obs.append(line.lower())

    return new_encoded_obs


def is_valid_tile(x, y, map_data, season):
    height = len(map_data[season])
    width = len(map_data[season][0])

    if x % TILE_SIZE != 0 or y % TILE_SIZE != 0:
        return False
    if not (0 <= x < width and 0 <= y < height):
        return False

    if map_data[season][y][x] == 'road':
        return False

    # Search for road
    neighbors = [
        ('up', x, y - TILE_SIZE),
        ('down', x, y + TILE_SIZE),
        ('left', x - TILE_SIZE, y),
        ('right', x + TILE_SIZE, y)
    ]

    for direction, nx, ny in neighbors:
        if 0 <= nx < width and 0 <= ny < height:
            if map_data[season][ny][nx] == 'road':
                return direction
    return None

def sample_light_positions(map_data, season, count):
    height = len(map_data[season])
    width = len(map_data[season][0])

    candidate_positions = []
    for y in range(0, height, TILE_SIZE):
        for x in range(0, width, TILE_SIZE):
            direction = is_valid_tile(x, y, map_data, season)
            if direction:
                candidate_positions.append((x, y, direction))

    sampled = random.sample(candidate_positions, min(count, len(candidate_positions)))

    placed_lights = []
    for x, y, direction in sampled:
        light_x = x + TILE_SIZE // 2
        light_y = y + TILE_SIZE // 2

        offset = TILE_SIZE // 4  # control how close against the border

        if direction == 'up':
            light_y -= offset
        elif direction == 'down':
            light_y += offset
        elif direction == 'left':
            light_x -= offset
        elif direction == 'right':
            light_x += offset

        placed_lights.append((light_x, light_y))

    return placed_lights