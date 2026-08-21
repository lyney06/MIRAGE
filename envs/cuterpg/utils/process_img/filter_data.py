import os
import json
import re

# Paths
image_dir = './NavigationMap/assets/extracted_objects'
json_path = './NavigationMap/assets/object_boundaries.json'

# Step 1: Get list of object IDs from the image filenames
image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]

# Extract numeric IDs even if there's a prefix like 'object_'
image_ids = set()
for f in image_files:
    match = re.search(r'(\d+)', os.path.splitext(f)[0])  # Extract number from filename
    if match:
        image_ids.add(int(match.group(1)))

# Step 2: Load the JSON data
with open(json_path, 'r') as json_file:
    boundaries = json.load(json_file)

# Step 3: Filter boundaries based on existing image IDs
filtered_boundaries = [entry for entry in boundaries if entry['id'] in image_ids]

# Step 4: Save filtered boundaries (optional)
filtered_json_path = './NavigationMap/assets/filtered_object_boundaries.json'
with open(filtered_json_path, 'w') as out_file:
    json.dump(filtered_boundaries, out_file, indent=4)

print(f"Filtered boundaries saved to {filtered_json_path}")