# character.py

import pygame
from .config import CHARACTER_WIDTH, CHARACTER_HEIGHT
from pdb import set_trace as st

class Character:
    def __init__(self, sprite, 
                       game_map):
        self.sprite = sprite
        self.images = { 'south': self.sprite.get_frame(0, 0, CHARACTER_WIDTH, CHARACTER_HEIGHT),
                        'west':  self.sprite.get_frame(0, 1, CHARACTER_WIDTH, CHARACTER_HEIGHT),
                        'east':  self.sprite.get_frame(0, 2, CHARACTER_WIDTH, CHARACTER_HEIGHT),
                        'north': self.sprite.get_frame(0, 3, CHARACTER_WIDTH, CHARACTER_HEIGHT),
                      }
        self.game_map = game_map

    def reset(self):
        raise NotImplementedError("reset() is not implemented yet.")

    def draw(self, screen):
        raise NotImplementedError("draw() is not implemented yet.")

    def get_observation(self):
        raise NotImplementedError("get_observation() is not implemented yet.")

    def test_image(self):
        # Assuming self.images contains the sprites for each direction
        directions = ['south', 'east', 'west', 'north']

        # Get the size of a single sprite (assuming all are the same size)
        sprite_width, sprite_height = self.images['east'].get_size()

        # Create a new surface to hold all 4 sprites horizontally
        total_width = sprite_width * len(directions)
        combined_surface = pygame.Surface((total_width, sprite_height), pygame.SRCALPHA)

        # Blit each sprite onto the combined surface
        for idx, direction in enumerate(directions):
            combined_surface.blit(self.images[direction], (idx * sprite_width, 0))

        # Save the combined surface as an image
        pygame.image.save(combined_surface, "combined_sprites.png")
        return