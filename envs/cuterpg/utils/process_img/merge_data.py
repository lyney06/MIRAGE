import os
import json
import shutil

def get_png_files(folder):
    """Returns a sorted list of object_<id>.png filenames from a folder."""
    return sorted([
        f for f in os.listdir(folder) if f.endswith('.png') and f.startswith('object_')
    ], key=lambda x: int(x.split('_')[1].split('.')[0]))  # Sort by ID

def load_json(json_path):
    """Loads JSON data from a file."""
    with open(json_path, 'r') as file:
        return json.load(file)

def save_json(data, output_path):
    """Saves JSON data to a file."""
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)

def merge_objects_and_relabel(winter_folder, shared_folder, winter_json, shared_json, output_folder, output_json):
    """
    Merges PNG images from winter_objects and shared_objects into a new folder.
    Keeps shared_object IDs the same and assigns new IDs to winter_objects.

    Parameters:
    - winter_folder: Path to winter_objects folder.
    - shared_folder: Path to shared_objects folder.
    - winter_json: Path to winter_objects JSON.
    - shared_json: Path to shared_objects JSON.
    - output_folder: Path to save merged images.
    - output_json: Path to save merged JSON.
    """

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Load JSON data
    winter_data = load_json(winter_json)
    shared_data = load_json(shared_json)

    # Get existing image filenames
    shared_files = get_png_files(shared_folder)
    winter_files = get_png_files(winter_folder)

    # Collect shared_objects data and IDs
    shared_objects = {obj["id"]: obj for obj in shared_data}
    max_shared_id = max(shared_objects.keys(), default=0)  # Get the max ID from shared objects

    # Copy shared_objects first, keeping IDs
    updated_objects = []
    for filename in shared_files:
        old_id = int(filename.split('_')[1].split('.')[0])  # Extract old ID

        # Copy image without renaming
        shutil.copy(os.path.join(shared_folder, filename), os.path.join(output_folder, filename))

        # Keep original object data
        if old_id in shared_objects:
            updated_objects.append(shared_objects[old_id])

        print(f"Kept {filename} (ID: {old_id})")

    # Process winter_objects and assign new IDs
    new_id = max_shared_id + 1  # Start new IDs from max_shared_id + 1
    for filename in winter_files:
        old_id = int(filename.split('_')[1].split('.')[0])  # Extract old ID

        # Rename image with new ID
        new_filename = f"object_{new_id}.png"
        shutil.copy(os.path.join(winter_folder, filename), os.path.join(output_folder, new_filename))

        # Find and update object data
        for obj in winter_data:
            if obj["id"] == old_id:
                updated_obj = obj.copy()
                updated_obj["id"] = new_id
                updated_objects.append(updated_obj)
                print(f"Renamed {filename} -> {new_filename} (New ID: {new_id})")
                break

        new_id += 1  # Increment new ID

    # Save the updated JSON
    save_json(updated_objects, output_json)
    print(f"\n✅ Merging Complete! New JSON saved at {output_json}")

# Example Usage
if __name__ == "__main__":
    # Input folders & JSONs
    winter_folder = "NavigationMap/assets/winter_objects"
    shared_folder = "NavigationMap/assets/shared_objects"
    winter_json = "NavigationMap/assets/object_boundaries_winter.json"
    shared_json = "NavigationMap/assets/shared_boundaries.json"

    # Output folder & JSON
    output_folder = "NavigationMap/assets/merged_objects"
    output_json = "NavigationMap/assets/merged_boundaries.json"

    merge_objects_and_relabel(winter_folder, shared_folder, winter_json, shared_json, output_folder, output_json)