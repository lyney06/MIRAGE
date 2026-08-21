# tileset.py

import pygame
from .config import GRID_SIZE, INTERVAL_SIZE, CHARACTER_WIDTH, CHARACTER_HEIGHT, ASSETS_PATH
from pdb import set_trace as st

class TileSet:
    def __init__(self, season='summer'):
        if season == 'summer':
            self.tile_sheet = pygame.image.load(f"{ASSETS_PATH}tiles.png").convert_alpha()
        elif season == 'winter':
            self.tile_sheet = pygame.image.load(f"{ASSETS_PATH}CuteRPG_Winter.png").convert_alpha()
        self.house_sheet = pygame.image.load(f"{ASSETS_PATH}houses.png").convert_alpha()
        self.object_sheet = pygame.image.load(f"{ASSETS_PATH}objects.png").convert_alpha()
        self.npc_sheets = []
        for i in range(14):
            self.npc_sheets.append(pygame.image.load(f"{ASSETS_PATH}npc/Character_{i+1}.png").convert_alpha())
        self.season = season

    def get_tile(self, tilesheet, x_index, y_index, width, height, type='object'):
        if type == 'object':
            rect = pygame.Rect(
                x_index * GRID_SIZE,    # x startpoint
                y_index * GRID_SIZE,    # y startpoint
                width * GRID_SIZE,      # width
                height * GRID_SIZE      # height
            )
        elif type == 'character':
            rect = pygame.Rect(
            x_index * 2 * (GRID_SIZE+INTERVAL_SIZE),    # x startpoint
            y_index * 2 * (GRID_SIZE+INTERVAL_SIZE),    # y startpoint
            width * GRID_SIZE,      # width
            height * GRID_SIZE      # height
        )
        return tilesheet.subsurface(rect)

    def get_house(self, x_index, y_index, width, height):
        return self.get_tile(self.house_sheet, x_index, y_index, width, height)

    def get_object(self, x_index, y_index, width, height):
        return self.get_tile(self.object_sheet, x_index, y_index, width, height)
    
    def get_road(self):
        if self.season == 'summer':
            return self.get_tile(self.tile_sheet, 0, 10, 6, 6)
        elif self.season == 'winter':
            return self.get_tile(self.tile_sheet, 0, 10, 6, 6)
        
    def get_highlighted_road(self):
        if self.season == 'summer':
            return self.get_tile(self.tile_sheet, 0, 18, 6, 6)
        elif self.season == 'winter':
            return self.get_tile(self.tile_sheet, 0, 24, 6, 6)
        
    def get_alter_road(self):
        if self.season == 'summer':
            return self.get_tile(self.tile_sheet, 33, 15, 6, 6)
        elif self.season == 'winter':
            return self.get_tile(self.tile_sheet, 6, 24, 6, 6)
        
    def get_land(self):
        if self.season == 'summer':
            return self.get_tile(self.tile_sheet, 0, 2, 6, 6)
        elif self.season == 'winter':
            return self.get_tile(self.tile_sheet, 18, 10, 6, 6)
        
    def get_npc(self):
        npc_lst = []
        for i in range(len(self.npc_sheets)):
            for x in range(1, 16, 4):
                npc_lst.append(self.get_tile(self.npc_sheets[i], x, 0, CHARACTER_WIDTH, CHARACTER_HEIGHT, type='character'))
        # static direction
        return npc_lst