# getCuterpgElements.py

import pygame
from .config import GRID_SIZE, ASSETS_PATH

class getCuterpgItem:
    def __init__(self):
        self.sprite_sheet = pygame.image.load(f"{ASSETS_PATH}character.png").convert_alpha()
        self.water_sheet = pygame.image.load(f"{ASSETS_PATH}waters.png").convert_alpha()
        self.harbor_sheet = pygame.image.load(f"{ASSETS_PATH}harbor.png").convert_alpha()
        self.kitchen_sheet = pygame.image.load(f"{ASSETS_PATH}kitchen.png").convert_alpha()
        self.land_sheet = pygame.image.load(f"{ASSETS_PATH}lands.png").convert_alpha()
        self.farmland_sheet = pygame.image.load(f"{ASSETS_PATH}farmland.png").convert_alpha()

    def get_sprite(self, x_index, y_index, width, height):
        rect = pygame.Rect(
            x_index * GRID_SIZE,    # x startpoint
            y_index * GRID_SIZE,    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return self.sprite_sheet.subsurface(rect)
    
    def get_water(self, x_index, y_index, width, height):
        rect = pygame.Rect(
            x_index * GRID_SIZE,    # x startpoint
            y_index * GRID_SIZE,    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return self.water_sheet.subsurface(rect)

    def get_kitchen(self, x_index, y_index, width, height):
        rect = pygame.Rect(
            x_index * GRID_SIZE,    # x startpoint
            y_index * GRID_SIZE,    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return self.kitchen_sheet.subsurface(rect)

    def get_land(self, x_index, y_index, width, height):
        rect = pygame.Rect(
            x_index * GRID_SIZE,    # x startpoint
            y_index * GRID_SIZE,    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return self.land_sheet.subsurface(rect)
    
    def get_harbor(self, x_index, y_index, width, height):
        rect = pygame.Rect(
            x_index * GRID_SIZE,    # x startpoint
            y_index * GRID_SIZE,    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return self.harbor_sheet.subsurface(rect)
    
    def get_farmland(self, x_index, y_index, width, height):
        rect = pygame.Rect(
            x_index * GRID_SIZE,    # x startpoint
            y_index * GRID_SIZE,    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return self.farmland_sheet.subsurface(rect)
  