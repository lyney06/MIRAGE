import os
import json

def filter_objects_by_images(json_path, images_folder, output_json):
    """
    Filters objects in JSON based on the presence of corresponding object_<id>.png files.
    Updates the color field to 'winter' and saves to a new JSON file.

    Parameters:
    - json_path (str): Path to the input JSON file.
    - images_folder (str): Path to the folder containing PNG files.
    - output_json (str): Path to save the filtered JSON file.
    """

    # Load JSON data
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Get a list of object_<id>.png files in shared_objects folder
    existing_ids = {
        int(filename.split('_')[1].split('.')[0])  # Extracts ID from object_<id>.png
        for filename in os.listdir(images_folder)
        if filename.startswith('object_') and filename.endswith('.png')
    }

    # Filter objects based on IDs and update color
    filtered_objects = [
        {**obj, "color": "winter"}  # Keep all fields but change color to 'winter'
        for obj in data
        if obj['id'] in existing_ids
    ]

    # Save the filtered data
    with open(output_json, 'w') as file:
        json.dump(filtered_objects, file, indent=4)

    print(f"Filtered JSON saved at: {output_json}")

# Example usage
if __name__ == "__main__":
    json_file = "NavigationMap/assets/object_boundaries.json"  # Replace with actual path
    images_folder = "NavigationMap/assets/shared_objects"      # Replace with actual path
    output_json = "NavigationMap/assets/shared_boundaries.json" # Output JSON file

    filter_objects_by_images(json_file, images_folder, output_json)