import pygame
import os

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((12, 12))
pygame.display.set_caption("Icon Extractor")

# Constants - matching your original parameters
GRID_SIZE = 6.5/2
INTERVAL_SIZE = 9.5/2

# Create output directory if it doesn't exist
output_dir = "./extracted_icons"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def get_icon(x_index, y_index, width=5, height=5):
    sprite_sheet = pygame.image.load("../assets/CuteRPG_Icons02.png").convert_alpha()
    rect = pygame.Rect(
        x_index * 2 * (GRID_SIZE+INTERVAL_SIZE),  # x startpoint (with the *2 as in your code)
        y_index * 2 * (GRID_SIZE+INTERVAL_SIZE),  # y startpoint (with the *2 as in your code)
        width * GRID_SIZE,  # width
        height * GRID_SIZE  # height
    )
    return sprite_sheet.subsurface(rect)

# Extract all icons - from your image I can see 16 columns and 8 rows
for y in range(8):  # 8 rows
    for x in range(16):  # 16 columns
        try:
            img = get_icon(x, y)
            pygame.image.save(img, f"{output_dir}/icon_{x}_{y}.png")
            print(f"Saved icon at position ({x}, {y})")
        except Exception as e:
            print(f"Error extracting icon at ({x}, {y}): {e}")

print("Extraction complete!")
pygame.quit()