# map.py

from .config import GRID_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
import pygame
import random

class GameMap:
    def __init__(self, itemFetcher):
        self.water_tile = itemFetcher.get_water(1, 27, 4, 4)
        self.farmland_tile = itemFetcher.get_farmland(28, 18, 2, 6)
        self.grasslans_tile = itemFetcher.get_land(0, 2, 6, 6)
        # self.kitchen_pic = itemFetcher.get_kitchen(0, 28, 10, 8)
        self.kitchen_pic = pygame.transform.scale(itemFetcher.get_kitchen(0, 28, 10, 8), (20 * GRID_SIZE, 16 * GRID_SIZE))
        # self.shop_pic = itemFetcher.get_harbor(0, 32, 8, 10)
        self.shop_pic = pygame.transform.scale(itemFetcher.get_harbor(0, 32, 8, 10), (16 * GRID_SIZE, 20 * GRID_SIZE))
        # self.floor_pic = itemFetcher.get_harbor(25, 0, 6, 8)
        self.floor_pic = pygame.transform.scale(itemFetcher.get_harbor(25, 0, 6, 8), (12 * GRID_SIZE, 16 * GRID_SIZE))


    def draw(self, screen):
        for row in range(0, WINDOW_WIDTH, 6 * GRID_SIZE):
            for col in range(0, WINDOW_HEIGHT // 2, 6 * GRID_SIZE):
                screen.blit(self.grasslans_tile, (row, col))
        for row in range(0, WINDOW_WIDTH, 4 * GRID_SIZE):
            for col in range(WINDOW_HEIGHT // 2, WINDOW_HEIGHT, 4 * GRID_SIZE):
                screen.blit(self.water_tile, (row, col))

        for row in range(WINDOW_WIDTH // 2 - 3 * 6 * GRID_SIZE, WINDOW_WIDTH // 2 + 3 * 6 * GRID_SIZE, 2 * GRID_SIZE):
            for col in range(WINDOW_HEIGHT // 2 - (3 + 1) * 6 * GRID_SIZE, WINDOW_HEIGHT // 2 - 6 * GRID_SIZE, 6 * GRID_SIZE):
                screen.blit(self.farmland_tile, (row, col))

        screen.blit(self.kitchen_pic, (WINDOW_WIDTH // 2 - (18 + 20 + 0.5) * GRID_SIZE, WINDOW_HEIGHT // 2 - (6 + 16) * GRID_SIZE))

        screen.blit(self.shop_pic, (WINDOW_WIDTH // 2 + (18 + 0.5) * GRID_SIZE, WINDOW_HEIGHT // 2 - (6 + 20) * GRID_SIZE))

        for row in range(WINDOW_WIDTH // 4, WINDOW_WIDTH, WINDOW_WIDTH // 4):
            screen.blit(self.floor_pic, (row - 6 * GRID_SIZE, WINDOW_HEIGHT // 2))

