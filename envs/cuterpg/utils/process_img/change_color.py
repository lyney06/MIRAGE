import os
from PIL import Image

def color_substitution(image_path, color_map, output_path=None):
    """
    Substitute colors in the given image based on color_map.

    Parameters:
    - image_path (str): Path to the PNG image.
    - color_map (dict): Dictionary mapping (R, G, B, A) tuples from original to target colors.
    - output_path (str): Path to save the modified image. If None, overwrites the original.
    """
    img = Image.open(image_path).convert("RGBA")
    pixels = img.load()

    width, height = img.size

    # Iterate through each pixel
    for x in range(width):
        for y in range(height):
            current_color = pixels[x, y]

            # Substitute color if it matches the map
            if current_color in color_map:
                pixels[x, y] = color_map[current_color]

    # Save modified image
    save_path = output_path if output_path else image_path
    img.save(save_path)
    print(f"Updated image saved at: {save_path}")

def batch_color_substitution(folder_path, color_map, output_folder=None):
    """
    Apply color substitution to all PNG images in a folder.

    Parameters:
    - folder_path (str): Path to the folder containing PNG images.
    - color_map (dict): Color mapping dictionary.
    - output_folder (str): Folder to save updated images. If None, overwrite originals.
    """
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, filename) if output_folder else None
            color_substitution(input_path, color_map, output_path)

# Example Usage:
if __name__ == "__main__":
    # Define color mapping: (R, G, B, A) -> (R, G, B, A)
    color_map = {
        (255, 220, 140, 255): (183, 199, 229, 255),
        (255, 201, 76, 255): (229, 238, 255, 255),
        (255, 147, 25, 255): (0, 212, 255, 255),
        (229, 122, 0, 255): (0, 178, 255, 255),
        (178, 95, 0, 255): (0, 144, 255, 255),


        (255, 165, 127, 255): (183, 199, 229, 255),
        # (140, 0, 5, 255): (102, 30, 0, 255),
        (255, 120, 63, 255): (229, 238, 255, 255),
        (255, 55, 25, 255): (0, 212, 255, 255),
        (229, 29, 0, 255): (0, 178, 255, 255),
        (178, 0, 6, 255): (0, 144, 255, 255),

        (152, 255, 106, 255): (183, 199, 229, 255),
        # (140, 0, 5, 255): (102, 30, 0, 255),
        (131, 222, 109, 255): (229, 238, 255, 255),
        (123, 193, 127, 255): (0, 212, 255, 255),
        (109, 171, 143, 255): (0, 178, 255, 255),
        (87, 136, 134, 255): (0, 144, 255, 255),
        
    }

    # Single image substitution
    # image_path = "path/to/your/image.png"
    # color_substitution(image_path, color_map)

    # Batch substitution for all images in a folder
    folder_path = "NavigationMap/assets/extracted_objects"
    output_folder = "NavigationMap/assets/extracted_objects_w"  # Optional
    batch_color_substitution(folder_path, color_map, output_folder)



# Color RGBA (60, 102, 50, 255) - Count: 80
# Color RGBA (131, 222, 109, 255) - Count: 445
# Color RGBA (152, 255, 106, 255) - Count: 25
# Color RGBA (123, 193, 127, 255) - Count: 1102
# Color RGBA (45, 76, 37, 255) - Count: 113
# Color RGBA (109, 171, 143, 255) - Count: 963
# Color RGBA (87, 136, 134, 255) - Count: 625
# Color RGBA (102, 69, 20, 255) - Count: 22 no
# Color RGBA (178, 72, 53, 255) - Count: 63
# Color RGBA (209, 88, 66, 255) - Count: 85
# Color RGBA (0, 0, 0, 76) - Count: 124
# Color RGBA (255, 105, 50, 255) - Count: 101
# Color RGBA (89, 56, 8, 255) - Count: 74
# Color RGBA (51, 32, 5, 255) - Count: 127
# Color RGBA (0, 0, 0, 167) - Count: 1


# Color RGBA (0, 0, 0, 0) - Count: 1016
# Color RGBA (183, 199, 229, 255) - Count: 88
# Color RGBA (142, 164, 204, 255) - Count: 48
# Color RGBA (229, 238, 255, 255) - Count: 104
# Color RGBA (255, 255, 255, 255) - Count: 16
# Color RGBA (0, 108, 191, 255) - Count: 40
# Color RGBA (0, 212, 255, 255) - Count: 364
# Color RGBA (0, 86, 153, 255) - Count: 144
# Color RGBA (0, 255, 255, 255) - Count: 36
# Color RGBA (0, 178, 255, 255) - Count: 420
# Color RGBA (0, 144, 255, 255) - Count: 372
# Color RGBA (102, 69, 20, 255) - Count: 32
# Color RGBA (0, 0, 0, 76) - Count: 120
# Color RGBA (209, 88, 66, 255) - Count: 40
# Color RGBA (255, 105, 50, 255) - Count: 40


# Color RGBA (127, 46, 0, 255) - Count: 80 brown
# Color RGBA (255, 201, 76, 255) - Count: 445 yellow
# Color RGBA (255, 220, 140, 255) - Count: 25
# Color RGBA (255, 147, 25, 255) - Count: 1102
# Color RGBA (102, 30, 0, 255) - Count: 113
# Color RGBA (229, 122, 0, 255) - Count: 963
# Color RGBA (178, 95, 0, 255) - Count: 625
# Color RGBA (102, 69, 20, 255) - Count: 22
# Color RGBA (178, 72, 53, 255) - Count: 63
# Color RGBA (209, 88, 66, 255) - Count: 85
# Color RGBA (0, 0, 0, 76) - Count: 124
# Color RGBA (255, 105, 50, 255) - Count: 101
# Color RGBA (89, 56, 8, 255) - Count: 74
# Color RGBA (51, 32, 5, 255) - Count: 127
# Color RGBA (0, 0, 0, 167) - Count: 1





# Color RGBA (140, 0, 5, 255) - Count: 64
# Color RGBA (255, 120, 63, 255) - Count: 205
# Color RGBA (255, 165, 127, 255) - Count: 16
# Color RGBA (255, 55, 25, 255) - Count: 365
# Color RGBA (102, 0, 3, 255) - Count: 157
# Color RGBA (229, 29, 0, 255) - Count: 713
# Color RGBA (178, 0, 6, 255) - Count: 605
# Color RGBA (0, 0, 0, 76) - Count: 65
# Color RGBA (102, 69, 20, 255) - Count: 14
# Color RGBA (209, 88, 66, 255) - Count: 21
# Color RGBA (255, 105, 50, 255) - Count: 21