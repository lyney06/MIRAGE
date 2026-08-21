from envs.cuterpg.utils.character import Character

# character.py

from ..utils.config import GRID_SIZE, TILE_SIZE
from .observation import get_first_person
from pdb import set_trace as st

class NavigationCharacter(Character):
    def __init__(self, sprite, game_map, step_size=1):
        super().__init__(sprite, game_map)
        self.step_size = step_size

    def reset(self):
        self.direction = 'east'    # Initial direction
        self.position = self.game_map.start_position     # Start position

    def draw(self, screen):
        x, y = self.position
        screen.blit(self.images[self.direction], (x * GRID_SIZE, y * GRID_SIZE))

    def whole_tile_road(self, x, y):
        tile_x_start = (x // TILE_SIZE) * TILE_SIZE
        tile_y_start = (y // TILE_SIZE) * TILE_SIZE

        for yy in range(tile_y_start, tile_y_start + TILE_SIZE):
            for xx in range(tile_x_start, tile_x_start + TILE_SIZE):
                if self.game_map.map_data[self.game_map.season][yy][xx] != 'road':
                    return False
        return True


    def can_move_to(self, new_position):
        MAP_COLS = self.game_map.MAP_COLS
        MAP_ROWS = self.game_map.MAP_ROWS
        x, y = new_position
        if not (0 <= x < MAP_COLS * TILE_SIZE - 2 and 0 <= y < MAP_ROWS * TILE_SIZE - 2):
            return False
        return self.whole_tile_road(x, y)

    def move(self, movement):
        """movement in ['forward', 'turn left', 'turn right', 'turn around']"""
        directions = ['east', 'south', 'west', 'north']
        directions_step = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        curr_dir_ind = directions.index(self.direction)

        if movement == 'turn right':
            self.direction = directions[(curr_dir_ind + 1) % 4]
        elif movement == 'turn around':
            self.direction = directions[(curr_dir_ind + 2) % 4]
        elif movement == 'turn left':
            self.direction = directions[(curr_dir_ind - 1) % 4]

        elif movement == "forward":

            dx, dy = directions_step[directions.index(self.direction)]
            # Calculate new tile position
            new_position = (
                self.position[0] + dx * TILE_SIZE,
                self.position[1] + dy * TILE_SIZE
            )

            # Check if the next tile is a road
            if self.can_move_to(new_position):
                self.position = new_position  # Move to the new tile

    def get_observation(self):
        x, y = self.position
        MAP_COLS = self.game_map.MAP_COLS
        MAP_ROWS = self.game_map.MAP_ROWS
        return get_first_person((x, y), self.direction, self.game_map.map_data, self.game_map.season, MAP_ROWS, MAP_COLS, TILE_SIZE)
