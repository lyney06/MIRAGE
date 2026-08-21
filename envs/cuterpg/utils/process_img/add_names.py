import os
import json

# Paths
filtered_json_path = './NavigationMap/assets/filtered_object_boundaries.json'
rec_json_path = './NavigationMap/assets/object_boundaries_rec.json'

# Step 1: Load filtered boundaries
with open(filtered_json_path, 'r') as filtered_file:
    filtered_boundaries = json.load(filtered_file)

# Step 2: Load object boundaries with name and color
with open(rec_json_path, 'r') as rec_file:
    rec_boundaries = json.load(rec_file)

# Step 3: Create a lookup dictionary from rec_boundaries for fast access
rec_lookup = {
    (entry['x'], entry['y'], entry['width'], entry['height'], entry['id']): entry
    for entry in rec_boundaries
}

# Step 4: Update filtered boundaries with name and color if matched
for entry in filtered_boundaries:
    key = (entry['x'], entry['y'], entry['width'], entry['height'], entry['id'])
    if key in rec_lookup:
        entry['name'] = rec_lookup[key].get('name', '')
        entry['color'] = rec_lookup[key].get('color', '')

# Step 5: Save the updated filtered boundaries
with open(filtered_json_path, 'w') as out_file:
    json.dump(filtered_boundaries, out_file, indent=4)

print(f"Filtered boundaries updated with 'name' and 'color' in {filtered_json_path}")