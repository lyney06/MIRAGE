import pygame
from .config import GRID_SIZE, ASSETS_PATH, INTERVAL_SIZE
from pdb import set_trace as st

class CharacterSprite:
    def __init__(self):
        self.sprite_sheet = pygame.image.load(f"{ASSETS_PATH}character.png").convert_alpha()

    def get_frame(self, x_index, y_index, width, height):
        rect = pygame.Rect(
            # not sure why tho...
            x_index * 2 * (GRID_SIZE+INTERVAL_SIZE),    # x startpoint
            y_index * 2 * (GRID_SIZE+INTERVAL_SIZE),    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return self.sprite_sheet.subsurface(rect)
