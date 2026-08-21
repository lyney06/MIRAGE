import os
from PIL import Image
import json
from pdb import set_trace as st

# ---------- Part 1: Resize PNG Images ----------

# size_corres = { "special_hole_tree": 1,
#                 "triangular_tree": 1,
#                 "cluster_club_tree": 1,
#                 "cluster_rounded_tree": 1,
#                 "rounded_tree": 1,
#                 "club_tree": 1,
#                 "grouped_tree_comb1": 1,
#                 "dense_tree": 1,
#                 "compact_tree": 1,
#                 "cluster_compact_tree": 1,
#                 "tiered_tree": 1,
#                 "chestnut_tree": 1,
#                 "cluster_chestnut_tree": 1,
#                 "cluster_triangular_tree": 1,
#                 "grouped_tree_comb2": 1,
#                 "grouped_tree_comb3": 1,
#                 "grouped_tree_comb4": 1,
#                 "": 1}

size_corres = { "snow1": 0.75, 
                "snow2": 0.75,
                "snow3": 0.75, 
                "snow4": 0.75, 
                "snow5": 0.75, 
                "iceblock": 0.75,
                "special_hole_tree": 0.75,
                "triangular_tree": 0.75,
                "cluster_club_tree": 0.75,
                "cluster_rounded_tree": 0.75,
                "rounded_tree": 0.75,
                "club_tree": 0.75,
                "grouped_tree_comb1": 0.75,
                "dense_tree": 0.75,
                "compact_tree": 0.75,
                "cluster_compact_tree": 0.75,
                "tiered_tree": 0.75,
                "chestnut_tree": 0.75,
                "cluster_chestnut_tree": 0.75,
                "cluster_triangular_tree": 0.75,
                "grouped_tree_comb2": 0.75,
                "grouped_tree_comb3": 0.75,
                "grouped_tree_comb4": 0.75,
                "": 1}
season = 'winter'
season = 'summer'

def resize_images(folder_path, obj_size):
    for filename in os.listdir(folder_path):
        # object_{id}
        if filename.endswith('.png'):
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)
            # Double the size
            new_size = (int(img.width * obj_size[int(filename.split('object_')[1].split('.png')[0])]), int(img.height * obj_size[int(filename.split('object_')[1].split('.png')[0])]))
            resized_img = img.resize(new_size, Image.NEAREST)  # NEAREST for pixel art
            # Save the resized image (overwrite)
            resized_img.save(os.path.join(f'NavigationMap/assets/{season}_objects', filename))
            print(f"Resized {filename} to {new_size}")

# ---------- Part 2: Update JSON Data ----------
def update_json(json_path):
    obj_size = {}
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Double x, y, width, and height
    for obj in data:
        ratio = size_corres.get(obj['name'], 1)
        obj['width'] = int(obj['width']*ratio)
        obj['height'] = int(obj['height']*ratio)
        obj_size[obj['id']] = ratio

    # Save the updated JSON
    with open(f'NavigationMap/assets/{season}_boundaries.json', 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Updated JSON saved at {json_path}")
    print(obj_size)
    return obj_size

# ---------- Main Execution ----------
if __name__ == "__main__":
    # Paths to the folder and JSON
    images_folder = f'NavigationMap/assets/{season}_objects1'  # Replace with the actual path if different
    json_file = f'NavigationMap/assets/{season}_boundaries1.json'  # Replace with the actual path if different

    # Resize images and update JSON
    changed = update_json(json_file)
    resize_images(images_folder, changed)

    print("All images resized and JSON updated successfully.")