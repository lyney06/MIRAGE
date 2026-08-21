# map.py

import re
import json
import copy
import math
import pygame
import random
import itertools
import numpy as np
from collections import deque
from .path_converter import convert_path_to_instructions, path_to_turn
from .observation_converter import convert_obs_to_manual
from envs.cuterpg.utils.tileset import TileSet
from .utils import sample_light_positions
from ..utils.config import GRID_SIZE, TILE_SIZE, CHARACTER_WIDTH, CHARACTER_HEIGHT
from envs.cuterpg.utils.assets.label_to_description import SPECIAL_OBJECTS, WINTER_SPECIAL_OBJECTS
from pdb import set_trace as st

class GameMap:
    def __init__(self, screen, 
                       seasons,
                       dynamic,
                       npc,
                       mode,
                       construction,
                       max_land_size,
                       min_land_size,
                       map_rows=12,
                       map_cols=12,
                       ):
        self.screen = screen
        self.dynamic = dynamic
        self.npc = npc
        self.mode = mode
        self.seasons = seasons
        self.construction = construction
        self.max_land_size = max_land_size
        self.min_land_size = min_land_size
        self.MAP_ROWS = map_rows
        self.MAP_COLS = map_cols
        self.season_pointer = 0


    def reset(self):
        self.time_step = 0
        if not self.construction:
            self.path = []
            while not self.has_turn(self.path):
                self.initialize_season()
                self.goal_pos = None
                self.generate_random_map()
                self.initialize_agent()

                self.path, _ = self.find_path_bfs(self.start_position)
        else:
            self.alter_path = []
            while not self.alter_path:
                self.initialize_season()
                self.goal_pos = None
                self.generate_random_map()
                self.initialize_agent()

                self.path, _ = self.find_path_bfs(self.start_position)
                self.alter_path, _ = self.generate_obstructed_path(self.start_position)
                
        self.underlying_map = copy.deepcopy(self.map_data)
        self.place_pedestrian()
        self.estimate_step = len(self.path)
        return

    def has_turn(self, path):
        if not path or len(path) < 3:
            return False
        first_delta = (path[1][0] - path[0][0], path[1][1] - path[0][1])
        for i in range(2, len(path)):
            delta = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
            if delta != first_delta:
                return True
        return False

    def initialize_agent(self):
        m, n = len(self.map_data[self.season]), len(self.map_data[self.season][0])

        # List to store road tiles and their distances to the nearest goal tile
        road_tiles_with_distance = []

        # Iterate through the map and find all road tiles
        for row in range(0, m, TILE_SIZE):
            for col in range(0, n, TILE_SIZE):
                if self.map_data[self.season][row][col] == 'road':
                    tile_x, tile_y = col // TILE_SIZE, row // TILE_SIZE
                    path, min_distance = self.find_path_bfs((col, row))
                    if min_distance is not None:
                        road_tiles_with_distance.append(((tile_x, tile_y), min_distance, path))

        # Sort the list by distance (closest first)
        ranked_road_tiles = sorted(road_tiles_with_distance, key=lambda x: x[1])
        # print(f'sampling from {len(ranked_road_tiles)} road tiles.')
        road_tiles = ranked_road_tiles[int(-len(ranked_road_tiles)*0.25):] #furthest 25%

        if not self.construction:
            turn_tiles = [x for x in road_tiles if self.has_turn(x[2])]
            if not turn_tiles:
                turn_tiles = [x for x in ranked_road_tiles if self.has_turn(x[2])]
            if turn_tiles:
                road_tiles = turn_tiles

        road_tiles = [x[0] for x in road_tiles]
        col_tile, row_tile = random.choice(list(road_tiles))

        tile_center_x = col_tile * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = row_tile * TILE_SIZE + TILE_SIZE // 2

        x = tile_center_x - CHARACTER_WIDTH // 2
        y = tile_center_y - CHARACTER_HEIGHT // 2

        self.start_position = (x, y)
            
    
    def initialize_season(self):
        self.season_pointer = 0
        self.season = self.seasons[self.season_pointer]
        self.objects = {}
        self.tilesets = {}
        self.land_tile = {}
        self.road_tile = {}
        self.highlighted_road_tile = {}
        self.map_data = {}
        for season in self.seasons:
            self.objects[season] = []
            self.tilesets[season] = TileSet(season)
            self.land_tile[season] = self.tilesets[season].get_land()
            self.road_tile[season] = self.tilesets[season].get_road()
            self.highlighted_road_tile[season] = self.tilesets[season].get_highlighted_road()
            self.map_data[season] = [["" for _ in range(self.MAP_COLS * TILE_SIZE)] for _ in range(self.MAP_ROWS * TILE_SIZE)]
        if self.construction:
            self.alter_road_tile = {}
            self.alter_road_tile[season] = self.tilesets[season].get_alter_road()
        return
        

    def get_goal_tile(self):
        m, n = len(self.map_data[self.season]), len(self.map_data[self.season][0])
        goal_tiles = {(col // TILE_SIZE, row // TILE_SIZE)
                        for row in range(m)
                        for col in range(n)
                        if self.map_data[self.season][row][col] == 'destination'}
        return goal_tiles
    
    def closet_to_goal_tiles(self):
        m, n = len(self.map_data[self.season]), len(self.map_data[self.season][0])
        goal_tiles = self.get_goal_tile()
        min_distance = float('inf')
        closest_tiles = None

        for row in range(m // TILE_SIZE):
            for col in range(n // TILE_SIZE):
                # Compute the distance to the closest goal tile
                tile_type = self.map_data[self.season][row * TILE_SIZE][col * TILE_SIZE]
                if tile_type != 'road':
                    continue
                distance = min(abs(goal_col - col) + abs(goal_row - row) for (goal_col, goal_row) in goal_tiles)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_tiles = [(col, row)]
                elif distance == min_distance:
                    closest_tiles.append((col, row))

        pixels = []
        for closest_tile in closest_tiles:
            closest_tile_col, closest_tile_row = closest_tile
            pixels.extend([(x, y)
                    for y in range(closest_tile_row * TILE_SIZE, (closest_tile_row + 1) * TILE_SIZE)
                    for x in range(closest_tile_col * TILE_SIZE, (closest_tile_col + 1) * TILE_SIZE)])

        return pixels


    def generate_random_map(self):
        self.empty_grids = [(x, y) for x in range(TILE_SIZE*self.MAP_ROWS) for y in range(TILE_SIZE*self.MAP_COLS)]

        def place_land(x, y, w, h):
            # handle right double roads
            count_double_road_right = 0
            for row in range(max(y - TILE_SIZE, 0), y + h):
                if 0 <= row < self.MAP_ROWS * TILE_SIZE and x + w + TILE_SIZE < self.MAP_COLS * TILE_SIZE and self.map_data[self.season][row][x + w + TILE_SIZE] == "road":
                    count_double_road_right += 1
            if count_double_road_right > TILE_SIZE:
                w += TILE_SIZE

            # handle left double roads
            count_double_road_left = 0
            for row in range(y, y + h):
                if 0 <= row < self.MAP_ROWS * TILE_SIZE and x - TILE_SIZE - 1 >= 0 and self.map_data[self.season][row][x - TILE_SIZE - 1] == "road":
                    count_double_road_left += 1
            if count_double_road_left > TILE_SIZE:
                x -= TILE_SIZE

            # handle downward double roads
            for j in range(min(x + TILE_SIZE, self.MAP_COLS * TILE_SIZE), min(x + w, self.MAP_COLS * TILE_SIZE)):
                if y + h - 1 < self.MAP_ROWS * TILE_SIZE and self.map_data[self.season][y + h - 1][j] == "road":
                    h += TILE_SIZE

            for i in range(y, min(y + h, self.MAP_ROWS * TILE_SIZE)):
                for j in range(x, min(x + w, self.MAP_COLS * TILE_SIZE)):
                    if self.map_data[self.season][i][j] == "":
                        self.map_data[self.season][i][j] = "land"
            for i in range(max(0, y - TILE_SIZE), min(self.MAP_ROWS * TILE_SIZE, y + h + TILE_SIZE)):
                for j in range(max(0, x - TILE_SIZE), min(self.MAP_COLS * TILE_SIZE, x + w + TILE_SIZE)):
                    if self.map_data[self.season][i][j] == "":
                        self.map_data[self.season][i][j] = "road"
            return

        for j in range(0, self.MAP_ROWS):
            for i in range(0, self.MAP_COLS):
                y = j * TILE_SIZE
                x = i * TILE_SIZE
                if self.map_data[self.season][y][x] == "":
                    land_width = random.randint(self.min_land_size, self.max_land_size) * TILE_SIZE
                    land_height = random.randint(self.min_land_size, self.max_land_size) * TILE_SIZE
                    place_land(x, y, land_width, land_height)
                    # print(x, y, land_width // TILE_SIZE, land_height // TILE_SIZE)

        for i in range(0, TILE_SIZE*self.MAP_ROWS): 
            for j in range(0, TILE_SIZE*self.MAP_COLS):
                if self.map_data[self.season][i][j] == 'road':
                    self.empty_grids.remove((i, j))
                    
        self.place_houses('destination', 1, size=(10, 8))
        self.place_houses('house', random.randint(5, 8), size=(10, 8))
        self.enclose_lands()
        
        self.place_npc()
        self.place_dynamics()

        # copy the map before filling in additional objects 
        for other_season in [season for season in self.map_data.keys() if season != self.season]:
            self.copy_map_data(other_season)

        self.fill_land_with_objects()

    def copy_map_data(self, other_season):
        self.map_data[other_season] = copy.deepcopy(self.map_data[self.season])
        self.objects[other_season] = copy.deepcopy(self.objects[self.season])

    def switch_season(self):
        self.season_pointer = (self.season_pointer + 1) % len(self.seasons)
        self.season = self.seasons[self.season_pointer]

    def get_season(self):
        return self.seasons[self.season_pointer]

    def size_safe_to_place(self, size, row, col, season=None):
        if not season:
            season = self.season
        if not (row+size[0]<self.MAP_ROWS*TILE_SIZE and col+size[1]<self.MAP_COLS*TILE_SIZE):
            return False
        return all(self.map_data[season][row+r][col+c] == 'land' for r in range(size[0]) for c in range(size[1]))
    

    def place_item_at(self, row, col, size, obj_type, name_in_map, name="", id="", color='', season=None):
        if season is None:
            season = self.season
            
        for r in range(size[0]):
            for c in range(size[1]):
                self.map_data[season][row + r][col + c] = name_in_map

        self.objects[season].append({
            'type': obj_type,
            'position': (row, col),
            'size': size,
            'name': name,
            'id': id,
            'color': color,
        })


    def place_dynamics(self):
        if not self.dynamic:
            return
        # Place lanterns
        self.light_to_idx = {'red': 1, 'blue': 2, 'green': 3}
        count = 20

        # Step 1:all possible color orders
        color_permutations = list(itertools.permutations(sorted(self.light_to_idx.keys())))

        # Step 2: repeat such order until reaching the number limit
        repeated_permutations = (color_permutations * ((count + len(color_permutations) - 1) // len(color_permutations)))[:count]

        # Step 3: shuffle
        random.shuffle(repeated_permutations)
        self.light_orders = [list(seq) for seq in repeated_permutations]

        with open(f'envs/cuterpg/utils/assets/lights/light_boundaries.json') as f:
            light_boundaries = json.load(f)
            
        random.shuffle(self.empty_grids)
        self.light_positions = []

        for i in range(count):
            color_order = self.light_orders[i]
            color_idx = self.light_to_idx[color_order[self.time_step]]
            obj = light_boundaries[color_idx-1]
            size = (math.ceil(obj['height'] / GRID_SIZE), math.ceil(obj['width'] / GRID_SIZE))
            for (row, col) in self.empty_grids:
                if self.size_safe_to_place(size, row, col) and self.map_data[self.season][row][col] == 'land' and self.is_next_to_road(row, col, size):
                    name_in_map, _, obj_name = self.get_name(obj, i+1)
                    self.place_item_at(row, col, size, 'light', name_in_map, name=obj_name, id=obj['id'])
                    self.empty_grids.remove((row, col))
                    self.light_positions.append((obj, row, col, size, 'light', name_in_map, obj_name, obj['id']))
                    break

        return
    
    def place_pedestrian(self):
        if not self.dynamic:
            return
        # Place several pedestrians along the manual path so the agent meets
        # temporary forward-blocks more often (one sparse NPC rarely intervenes).
        total_npc = 5
        all_npc = self.tilesets[self.season].get_npc()
        self.npc_list = random.sample(all_npc, min(total_npc, len(all_npc)))
        original_path = copy.deepcopy(self.path[1:-1])  # path used for the manual
        self.npc_pos = []
        if not original_path:
            return

        n_place = min(total_npc, len(original_path), len(self.npc_list))
        # Spread along the route; fall back to unique samples if the path is short.
        if len(original_path) >= n_place:
            stride = max(1, len(original_path) // n_place)
            chosen = []
            for i in range(n_place):
                chosen.append(original_path[min(i * stride, len(original_path) - 1)])
            # Deduplicate while preserving order, then top up if needed.
            dedup = []
            seen = set()
            for p in chosen:
                if p not in seen:
                    dedup.append(p)
                    seen.add(p)
            for p in original_path:
                if len(dedup) >= n_place:
                    break
                if p not in seen:
                    dedup.append(p)
                    seen.add(p)
            chosen = dedup[:n_place]
        else:
            chosen = list(original_path)

        for idx, (x, y) in enumerate(chosen):
            # Offset inside the tile so the 3x3 NPC footprint dirties pure-road checks.
            px = x + random.randint(1, 2)
            py = y + random.randint(1, 2)
            self.place_item_at(
                py, px, (CHARACTER_WIDTH, CHARACTER_HEIGHT),
                'npc', f"npc_{idx}", f"npc_{idx}",
            )
            self.npc_pos.append((py, px))

        return


    def place_npc(self, count=None):
        if self.npc == 0:
            return
        if count is None:
            count = self.npc
        all_npc = self.tilesets[self.season].get_npc()
        self.npc_list = random.sample(all_npc, count)
        size = (CHARACTER_WIDTH, CHARACTER_HEIGHT)
        random.shuffle(self.empty_grids)
        placed_positions = []
        for (row, col) in self.empty_grids:
            if self.size_safe_to_place(size, row, col) and self.map_data[self.season][row][col] == 'land' and self.is_next_to_road(row, col, size):
                self.place_item_at(row, col, (CHARACTER_WIDTH, CHARACTER_HEIGHT), 'npc', f"npc_0", f"npc_0")
                self.empty_grids.remove((row, col))
                placed_positions.append((row, col))
                break
            
        for idx in range(1, count):
            best_position = None
            max_min_distance = -1
            for row, col in self.empty_grids:
                if not (self.size_safe_to_place(size, row, col) and self.map_data[self.season][row][col] == 'land' and self.is_next_to_road(row, col, size)):
                    continue
                # Compute the minimum distance from all previously placed NPCs
                min_distance = min(self.manhattan_distance((row, col), npc_pos) for npc_pos in placed_positions)

                # Select the position that maximizes this minimum distance
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_position = (row, col)

            row, col = best_position
            self.place_item_at(row, col, (CHARACTER_WIDTH, CHARACTER_HEIGHT), 'npc', f"npc_{idx}", f"npc_{idx}")
            placed_positions.append((row, col))
            self.empty_grids.remove((row, col))


    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def dist_to_goal(self, agent_pos):
        goal_pos = self.closet_to_goal_tiles()
        dist = float('inf')
        for pos in goal_pos:
            dist = min(dist, self.manhattan_distance(pos, agent_pos))

        return dist // TILE_SIZE
    

    def place_houses(self, obj_type, count, size=(1, 1)):
        for i in range(count):
            random.shuffle(self.empty_grids)
            for row, col in self.empty_grids:
                if self.size_safe_to_place(size, row, col) and not self.has_object_at(row, col, size) and self.is_next_to_road(row, col, size):
                    if obj_type == 'house':
                        self.place_item_at(row, col, size, obj_type, f"house_{i+1}")
                    else:
                        self.goal_pos = (row, col)
                        self.place_item_at(row, col, size, obj_type, "destination")
                    self.empty_grids.remove((row, col))
                    break


    def has_object_at(self, row, col, size=(1, 1), season=None):
        if season is None:
            season = self.season
        for obj in self.objects[season]:
            obj_row, obj_col = obj['position']
            obj_size = obj.get('size')
            if not (row + size[0] <= obj_row or row >= obj_row + obj_size[0] or col + size[1] <= obj_col or col >= obj_col + obj_size[1]):
                return True                
        return False


    def is_next_to_road(self, row, col, size=(1, 1)):
        for (y, x) in {(row-1, col), (row, col-1), (row+size[0], col+size[1]-1), (row + size[0]-1, col + size[1])}:
                if 0 <= x < self.MAP_COLS * TILE_SIZE and 0 <= y < self.MAP_ROWS * TILE_SIZE and self.map_data[self.season][y][x] in ['road', 'grass']:
                    return True
        return False


    def enclose_lands(self):
        direction = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for i in range(0, self.MAP_ROWS * TILE_SIZE):
            for j in range(0, self.MAP_COLS * TILE_SIZE):
                for d in direction:
                    dx, dy = d
                    y, x = i + dy, j + dx
                    if 0 <= x < self.MAP_COLS * TILE_SIZE and 0 <= y < self.MAP_ROWS * TILE_SIZE and self.map_data[self.season][i][j] == 'land' and self.map_data[self.season][y][x] == 'road':
                        self.map_data[self.season][i][j] = 'grass'
                        self.objects[self.season].append({'type': 'grass', 'position': (i, j), 'size': (1, 1)})

    
    def place_smaller_objs(self, target_land, objects, counter, season='summer'):
        last_counter = None
        while sum(row.count('land') for row in self.map_data[season]) > target_land and counter != last_counter:
            last_counter = counter
            for obj in objects:
                random.shuffle(self.empty_grids)
                size = (math.ceil(obj['height'] / GRID_SIZE), math.ceil(obj['width'] / GRID_SIZE))
                for row, col in self.empty_grids:
                    if self.size_safe_to_place(size, row, col, season=season) and not self.has_object_at(row, col, size, season=season):
                        name_in_map, obj_color, obj_name = self.get_name(obj, counter)
                        self.place_item_at(row, col, size, 'object', name_in_map, name=obj_name, id=obj['id'], color=obj_color, season=season)
                        self.empty_grids.remove((row, col))
                        counter += 1
                        break

    

    def place_special_objs(self, objects, counter, target=20):
        objects = sorted(objects, key=lambda obj: obj['width'] * obj['height'], reverse=True)
        # let's place the items one by one
        last_couter = None
        while counter < target and counter != last_couter: # if we are not able to fit any of them let's stop
            last_couter = counter
            for obj in objects:
                random.shuffle(self.empty_grids)
                size = (math.ceil(obj['height'] / GRID_SIZE), math.ceil(obj['width'] / GRID_SIZE))
                for row, col in self.empty_grids:
                    if self.size_safe_to_place(size, row, col) and not self.has_object_at(row, col, size):
                        name_in_map, obj_color, obj_name = self.get_name(obj, counter)
                        self.place_item_at(row, col, size, 'object', name_in_map, name=obj_name, id=obj['id'], color=obj_color)
                        self.empty_grids.remove((row, col))
                        counter += 1
                        break
                if counter >= target:
                    break
        return counter
    
    def get_name(self, obj, counter):
        obj_name = obj.get('name', '')
        obj_color = obj['color'] if obj_name else ''
        obj_name = f"{obj_name}_{obj_color}" if obj_name else ''
        name_in_map = f"{obj_name}_{counter}" if obj_name else f"object_{obj['id']}"
        return name_in_map, obj_color, obj_name
        
    
    def place_shared_object(self, target, 
                                  counter, 
                                  objects, 
                                  target_boundaries,
                                  obj=None,
                                  seasons=['summer', 'winter']):
        objects = sorted(objects, key=lambda obj: obj['width'] * obj['height'], reverse=True)
        last_couter = None
        while counter < target and counter != last_couter: # if we are not able to fit any of them let's stop
            last_couter = counter
            for obj in objects:
                random.shuffle(self.empty_grids)
                size = (math.ceil(obj['height'] / GRID_SIZE), math.ceil(obj['width'] / GRID_SIZE))
                for row, col in self.empty_grids:
                    if self.size_safe_to_place(size, row, col, season=seasons[0]) and not self.has_object_at(row, col, size, season=seasons[0]):
                        obj_other_season = [x for x in target_boundaries if x['id'] == obj['id']][0]
                        name_in_map, obj_color, obj_name = self.get_name(obj_other_season, counter)
                        self.place_item_at(row, col, size, 'object', name_in_map, name=obj_name, id=obj_other_season['id'], season=seasons[1], color=obj_color)

                        name_in_map, obj_color, obj_name = self.get_name(obj, counter)
                        self.place_item_at(row, col, size, 'object', name_in_map, name=obj_name, id=obj['id'], season=seasons[0], color=obj_color)
                        self.empty_grids.remove((row, col))
                        counter += 1
                        break
                if counter >= target:
                    break
        return counter


    def fill_land_with_objects(self):
        special_counter = 1
        initial_land = sum(row.count('land') for row in self.map_data[self.season])
        if len(self.seasons) == 1:
            target_land = int(0.5*initial_land)
            with open(f'envs/cuterpg/utils/assets/{self.season}_boundaries.json') as f:
                object_boundaries = json.load(f)
            named_objects = [obj for obj in object_boundaries if obj['name'] in SPECIAL_OBJECTS]
            special_counter = self.place_special_objs(named_objects, special_counter)
            other_objects = [obj for obj in object_boundaries if obj['name'] == '']
            
            self.place_smaller_objs(target_land, other_objects, special_counter)
        else:
            target_land = int(0.3*initial_land)
            with open('envs/cuterpg/utils/assets/winter_boundaries.json') as f:
                winter_object_boundaries = json.load(f)
            with open(f'envs/cuterpg/utils/assets/{self.season}_boundaries.json') as f:
                object_boundaries = json.load(f)
            
            n1 = random.choice(list(range(6, 10)))
            n2 = 25
            # place special items that are only in winter
            winter_special = [obj for obj in winter_object_boundaries if obj['name'] in WINTER_SPECIAL_OBJECTS]
            special_counter = self.place_shared_object(n1, special_counter, winter_special, object_boundaries, seasons=['winter', 'summer'])
            
            # place special items
            special_objects = [obj for obj in object_boundaries if obj['name'] in SPECIAL_OBJECTS]
            special_counter = self.place_shared_object(n2, special_counter, special_objects, winter_object_boundaries)

            counter_record = special_counter
            other_objects = [obj for obj in object_boundaries if obj['name'] == '']
            other_objects_winter = [obj for obj in winter_object_boundaries if obj['name'] == '']

            self.place_smaller_objs(target_land, other_objects, counter_record)
            self.place_smaller_objs(target_land, other_objects_winter, counter_record, 'winter')
        return


    def draw(self):
        for row in range(0, self.MAP_ROWS * TILE_SIZE, TILE_SIZE):
            for col in range(0, self.MAP_COLS * TILE_SIZE, TILE_SIZE):
                tile_type = self.map_data[self.season][row][col]
                # for those on the gt path let's change color
                if (col, row) in self.path:
                    tile = self.highlighted_road_tile
                elif self.construction and (col, row) in self.alter_path:
                    tile = self.alter_road_tile
                else:
                    tile = self.road_tile if tile_type == 'road' else self.land_tile
                tile = tile[self.season]
                x = col * GRID_SIZE
                y = row * GRID_SIZE
                self.screen.blit(tile, (x, y))

        for obj in self.objects[self.season]:
            obj_type = obj['type']
            obj_name = obj.get('name', '')
            row, col = obj['position']
            
            if obj_type == 'house':
                obj_tile = self.tilesets[self.season].get_house(16, 32, 8, 10)
            elif obj_type == 'destination':
                obj_tile = self.tilesets[self.season].get_house(8, 32, 8, 10)
            elif obj_type == 'grass':
                obj_tile = self.tilesets[self.season].get_object(25, 20, 1, 1)
            elif obj_type == 'npc':
                obj_tile = self.npc_list[int(obj_name.split('_')[1])]
            elif obj_type == 'object':
                obj_filename = f"object_{obj['id']}.png"
                try:
                    if self.season == 'summer':
                        obj_tile = pygame.image.load(f"envs/cuterpg/utils/assets/summer_objects/{obj_filename}").convert_alpha()
                    elif self.season == 'winter':
                        obj_tile = pygame.image.load(f"envs/cuterpg/utils/assets/winter_objects/{obj_filename}").convert_alpha()
                except (FileNotFoundError, pygame.error):
                    continue
            elif obj_type == 'construction':
                obj_file_name = obj['name'].split('_construction')[0]
                obj_tile = pygame.image.load(f"envs/cuterpg/utils/assets/construction/{obj_file_name}.png").convert_alpha()
            elif obj_type == 'light':
                obj_tile = pygame.image.load(f"envs/cuterpg/utils/assets/lights/object_{obj['id']}.png").convert_alpha()
            else:
                continue
            x = col * GRID_SIZE
            y = row * GRID_SIZE
            self.screen.blit(obj_tile, (x, y))
            
            
    def step_before(self):
        self.time_step += 1
        if self.dynamic:
            for idx, order in enumerate(self.light_orders):
                new_color = order[self.time_step%len(self.light_orders[0])]
                obj, row, col, size, obj_type, name_in_map, obj_name, _ = self.light_positions[idx]
                obj_id = self.light_to_idx[new_color]
                name_in_map = re.sub(r'(?<=light_)(blue|red|green)(?=_)', new_color, name_in_map)
                self.place_item_at(row, col, size, obj_type, name_in_map, name=obj_name, id=obj_id)
                
                
    def step_after(self, agent_position):
        if not self.dynamic:
            return

        agent_x, agent_y = agent_position
        agent_tile = (agent_x // TILE_SIZE, agent_y // TILE_SIZE)

        for idx, (row, col) in enumerate(self.npc_pos):
            npc_tile = (col // TILE_SIZE, row // TILE_SIZE)

            # NPC only considers moving if it's standing on the road dominant tile
            if self.get_dominant_tile_type(row, col) != 'road':
                continue

            dist = self.manhattan_distance(agent_tile, npc_tile)
            if dist > 1:
                continue

            # Prefer staying when adjacent so temporary blocks last long enough
            # for wait / explore to matter (previously they usually stepped away).
            action = random.choices(
                ["stay", "opposite", "side"],
                weights=[0.55, 0.25, 0.20],
                k=1
            )[0]

            if action == "stay":
                continue

            target_tile = None

            if action == "opposite":
                dx = npc_tile[0] - agent_tile[0]
                dy = npc_tile[1] - agent_tile[1]
                target_tile = (npc_tile[0] + dx, npc_tile[1] + dy)

                # Check if target_tile is within the MAP region
                if not (0 <= target_tile[0] < self.MAP_COLS and 0 <= target_tile[1] < self.MAP_ROWS):

                    action = "side"

            if action == "side":
                neighbors = [
                    (npc_tile[0] + 1, npc_tile[1]),
                    (npc_tile[0] - 1, npc_tile[1]),
                    (npc_tile[0], npc_tile[1] + 1),
                    (npc_tile[0], npc_tile[1] - 1),
                ]
                non_road_neighbors = [
                    pos for pos in neighbors
                    if 0 <= pos[0] < self.MAP_COLS
                    and 0 <= pos[1] < self.MAP_ROWS
                    and self.map_data[self.season][pos[1] * TILE_SIZE][pos[0] * TILE_SIZE] != 'road'
                ]
                if non_road_neighbors:
                    target_tile = random.choice(non_road_neighbors)
                else:
                    continue

            if not target_tile:
                continue

            new_col = target_tile[0] * TILE_SIZE + random.randint(1, 2)
            new_row = target_tile[1] * TILE_SIZE + random.randint(1, 2)

            for i in range(row, row + CHARACTER_HEIGHT):
                for j in range(col, col + CHARACTER_WIDTH):
                    if 0 <= i < self.MAP_ROWS * TILE_SIZE and 0 <= j < self.MAP_COLS * TILE_SIZE:
                        self.map_data[self.season][i][j] = self.underlying_map[self.season][i][j]

            # remove NPC from the old location
            self.objects[self.season] = [
                obj for obj in self.objects[self.season]
                if not (obj['type'] == 'npc' and obj['position'] == (row, col))
            ]

            # Place it in the new location
            self.place_item_at(new_row, new_col, (CHARACTER_WIDTH, CHARACTER_HEIGHT),
                            'npc', f"npc_{idx}", f"npc_{idx}")

            self.npc_pos[idx] = (new_row, new_col)

        
    def get_dominant_tile_type(self, row, col):
        for i in range(row, row + CHARACTER_HEIGHT):
            for j in range(col, col + CHARACTER_WIDTH):
                if 0 <= i < self.MAP_ROWS * TILE_SIZE and 0 <= j < self.MAP_COLS * TILE_SIZE:
                    tile = self.underlying_map[self.season][i][j]
                    if tile == 'road':
                        return 'road'
        return 'land'

    def revert_map(self,
                   map_data):
        result = copy.deepcopy(map_data)
        for season in self.seasons:
            result[season] = [["road" if "construction" in item else item for item in row] for row in result[season]]
        return result
    

    def get_map_manual_status(self,
                              agent_pos, 
                              agent_dir):
        x, y = agent_pos
        return self.map_manual_dict[self.season][x][y][agent_dir]


    def get_manual(self,
                   manual_type, 
                   path=None,
                   direction='east'):
        imperfect_info = 'This is a perfect manual.'
        if not path:
            path = self.path
            initial = f'Start! You are currently facing {direction}.' 
        else:
            initial = 'From your current location and direction, if you want to go to the destination, you can:'

        if self.construction:
            map_data = self.revert_map(self.map_data)
        elif self.dynamic and hasattr(self, 'underlying_map'):
            map_data = self.underlying_map
        else:
            map_data = self.map_data
        season = self.seasons[0] if len(self.seasons) > 1 else self.get_season()

        if manual_type == 0:
            manual, _ = path_to_turn(path, 
                                  map_data, 
                                  self.mode,
                                  self.MAP_ROWS,
                                  self.MAP_COLS,
                                  season,
                                  start_direction=direction,
                                  )
            manual = '\n'.join(manual)
        elif manual_type == 1:
            # perfect, number of tiles
            manual = convert_path_to_instructions(path, 
                                                  map_data, 
                                                  self.mode,
                                                  direction)[0]
            manual = '\n'.join(manual)
        elif manual_type == 2:
            # perfect, observation based
            proto_manual, imperfect_info = convert_path_to_instructions(path, 
                                                                        map_data, 
                                                                        self.mode,
                                                                        direction)
            start_p = path[0] if path else self.start_position
            manual = convert_obs_to_manual( map_data,
                                            self.seasons[0], # initial season
                                            start_p, 
                                            proto_manual,
                                            imperfect_info,
                                            self.MAP_ROWS,
                                            self.MAP_COLS,
                                            dir=direction)
                
        elif manual_type == 3:
            manual_instrs, imperfect_info = path_to_turn(path, 
                                                          map_data, 
                                                          self.mode,
                                                          self.MAP_ROWS,
                                                          self.MAP_COLS,
                                                          self.get_season(),
                                                          start_direction=direction,
                                                          wrong_turns=True,
                                                          closet=self.closet_to_goal_tiles())
            if manual_instrs is None:
                return None, None
            manual = '\n'.join(manual_instrs)
        elif manual_type == 4:
            proto_manual, imperfect_info = convert_path_to_instructions(path, 
                                                                        map_data, 
                                                                        self.mode, 
                                                                        direction,
                                                                        wrong_tiles=True,
                                                                        closet=self.closet_to_goal_tiles())
            if proto_manual is None:
                return None, None
            start_p = path[0] if path else self.start_position
            manual = convert_obs_to_manual( map_data,
                                            self.seasons[0], # initial season
                                            start_p, 
                                            proto_manual,
                                            imperfect_info,
                                            self.MAP_ROWS,
                                            self.MAP_COLS,
                                            dir=direction,
                                            manual_type='obs_wrong_step')
            # print(manual, imperfect_info)
            # st()
        else:
            manual = ''
            
        if manual_type <= 2:
            if len(self.seasons) > 1:
                imperfect_info = 'The manual was created in summer, but you are navigating in winter.'
            elif self.construction:
                imperfect_info = 'Some roads are blocked due to construction.'
            elif self.dynamic:
                imperfect_info = 'Pedestrians and traffic lights may temporarily block the path from the manual.'
        return f"{initial}\n{manual}", imperfect_info
        
    def get_npc_manual(self, manual_type, agent_pos, agent_dir):
        if manual_type in [3, 4]:
            for _ in range(50):
                if self.construction or self.dynamic or agent_pos == self.start_position:
                    curr_path = self.path
                else:
                    curr_path, _ = self.find_path_bfs(self.start_position)
                manual_res, imperfect_info = self.get_manual(manual_type, curr_path, direction=agent_dir)
                if manual_res is not None:
                    return manual_res, imperfect_info

                # Perturbation failed after 20 attempts. Regenerate start position, new path, and retry
                if self.construction:
                    self.alter_path = []
                    while not self.alter_path:
                        self.map_data = self.revert_map(self.map_data)
                        self.objects[self.season] = [obj for obj in self.objects[self.season] if obj.get('type') != 'construction']
                        self.initialize_agent()
                        self.path, _ = self.find_path_bfs(self.start_position)
                        self.alter_path, _ = self.generate_obstructed_path(self.start_position)
                else:
                    self.initialize_agent()
                    self.path, _ = self.find_path_bfs(self.start_position)
                self.estimate_step = len(self.path)
        else:
            if self.construction or self.dynamic or agent_pos == self.start_position:
                curr_path = self.path
            else:
                curr_path, _ = self.find_path_bfs(agent_pos)
            manual = self.get_manual(manual_type, curr_path, direction=agent_dir)
            return manual
    
    def find_path_bfs(self, start, closet=None):
        start = tuple((x // TILE_SIZE) * TILE_SIZE for x in start)

        directions = [      # God's view (dx, dy)
            (-TILE_SIZE, 0),    # up
            (TILE_SIZE, 0),     # down
            (0, -TILE_SIZE),    # left
            (0, TILE_SIZE),     # right
        ]

        queue = deque([(start, [], 0)])   # (current_position, previous_path)
        visited = set()
        if closet is None:
            closet = self.closet_to_goal_tiles()

        while queue:
            (x, y), path, dist = queue.popleft()

            # change this to target tiles
            if (x, y) in closet:
                # we want to record this specific tile actually (maybe), so that it's easier to keep track of
                self.specific_goal = (x, y)
                return path + [(x, y)], dist

            if (x, y) in visited:
                continue

            visited.add((x, y))

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= ny < self.MAP_ROWS * TILE_SIZE and 0 <= nx < self.MAP_COLS * TILE_SIZE and self.is_pure_tile(ny, nx, 'road') and (nx, ny) not in visited:
                    queue.append(((nx, ny), path + [(x, y)], dist+1))

        return False, None
    
    def is_pure_tile(self, x, y, category):
        for i in range((x // TILE_SIZE) * TILE_SIZE, (x // TILE_SIZE) * TILE_SIZE + TILE_SIZE):
            for j in range((y // TILE_SIZE) * TILE_SIZE, (y // TILE_SIZE) * TILE_SIZE + TILE_SIZE):
                if self.map_data[self.season][i][j] != category:
                    return False
        return True

    
    def generate_obstructed_path(self, start):
        # skip start and end
        original_path = copy.deepcopy(self.path[1:-1]) # original path which we used to generate manual
        random.shuffle(original_path)

        for _, (x, y) in enumerate(original_path):  # original_path every single tile on the path
            self.map_data[self.season][y][x] = 'construction'

            # check if it's still possible
            new_path, dist = self.find_path_bfs(start, [self.specific_goal])

            if new_path:
                # block road here
                with open(f'envs/cuterpg/utils/assets/construction/construction_boundaries.json') as f:
                    object_boundaries = json.load(f)
                obj = object_boundaries[1]
                name_in_map, _, obj_name = self.get_name(obj, 'inf')
                size = (math.ceil(obj['height'] / GRID_SIZE), math.ceil(obj['width'] / GRID_SIZE))
                self.place_item_at(y+1, x+1, size, 'construction', name_in_map, name=obj_name, id=obj['id'])
                return new_path, dist
            else:
                self.map_data[self.season][y][x] = 'road'

        return None, None
