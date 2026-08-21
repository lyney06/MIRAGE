import cv2
import numpy as np
import os
import json
from pdb import set_trace as st
# Set paths
# IMAGE_PATH = 'assets/CuteRPG_Winter_C.png'  # Replace with your image path
# OUTPUT_DIR = './NavigationMap/assets/winter_objects'
# BOUNDARY_FILE = './NavigationMap/assets/object_boundaries_winter.json'
IMAGE_PATH = '../assets/animation.png'  # Replace with your image path
OUTPUT_DIR = '../assets/lights'
BOUNDARY_FILE = '../assets/light_boundaries.json'

# Create output directory
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

image = cv2.imread(IMAGE_PATH, cv2.IMREAD_UNCHANGED)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Store boundary information
boundaries = []

# Function to check if at least two corners are non-empty or contain black pixels
# Only applies to larger objects to avoid filtering small items like flowers or small clusters
def has_non_empty_corners(obj, threshold=1):
    # h, w = obj.shape[:2]
    # if w <= 10 and h <= 10:  # Skip corner check for very small objects (like flowers or small clusters)
    #     return False, 0

    # corners = [
    #     obj[0:threshold, 0:threshold],             # Top-left
    #     obj[0:threshold, -threshold:],             # Top-right
    #     obj[-threshold:, 0:threshold],             # Bottom-left
    #     obj[-threshold:, -threshold:]              # Bottom-right
    # ]

    # non_empty_count = sum(np.count_nonzero(corner[:, :, 3]) > 0 for corner in corners)  # Check alpha channel
    # return non_empty_count >= 2, non_empty_count
    return False, 0

# Function to calculate average color of an object
def average_color(obj):
    mask = obj[:, :, 3] > 0  # Consider only non-transparent pixels
    if np.count_nonzero(mask) == 0:
        return np.array([0, 0, 0])
    return np.mean(obj[:, :, :3][mask], axis=0)

# Function to merge nearby bounding boxes
def merge_close_objects(boundaries, distance_threshold=20, color_threshold=30):
    merged = [x for x in boundaries]
    used = set()

    for i, box1 in enumerate(boundaries):
        if i in used:
            continue
        x1, y1, w1, h1 = box1['x'], box1['y'], box1['width'], box1['height']
        merged_box = [x1, y1, x1 + w1, y1 + h1]
        obj1 = image[y1:y1+h1, x1:x1+w1]
        color1 = average_color(obj1)

        for j, box2 in enumerate(boundaries):
            if i != j and j not in used:
                x2, y2, w2, h2 = box2['x'], box2['y'], box2['width'], box2['height']
                obj2 = image[y2:y2+h2, x2:x2+w2]
                color2 = average_color(obj2)

                # Check proximity and color similarity
                distance_check = abs(x1 - x2) < distance_threshold and abs(y1 - y2) < distance_threshold
                color_check = np.linalg.norm(color1 - color2) < color_threshold

                if distance_check and color_check:
                    merged_box[0] = min(merged_box[0], x2)
                    merged_box[1] = min(merged_box[1], y2)
                    merged_box[2] = max(merged_box[2], x2 + w2)
                    merged_box[3] = max(merged_box[3], y2 + h2)
                    used.add(j)

        merged.append({
            'x': merged_box[0],
            'y': merged_box[1],
            'width': merged_box[2] - merged_box[0],
            'height': merged_box[3] - merged_box[1],
        })
        used.add(i)
    
    filtered = []
    duplicates = set()
    for idx, boundary in enumerate(merged):
        # Skip objects with at least two non-empty or black corners (only for larger objects)
        x, y, w, h = boundary['x'], boundary['y'], boundary['width'], boundary['height']
        obj = image[y:y+h, x:x+w]
        nonempty_corner, num_corner = has_non_empty_corners(obj)
        boundary['id'] = idx + 1
        boundary['num_corners'] = num_corner
        print(boundary['id'], num_corner, w, h, w*h)
        if obj.tobytes() not in duplicates:
            if not nonempty_corner:
                filtered.append(boundary)
                duplicates.add(obj.tobytes())

    return filtered

# Extract objects and save them
for i, cnt in enumerate(contours):
    x, y, w, h = cv2.boundingRect(cnt)

    area = w * h
    # Filter out very small noise
    if w >= 5 and h >= 5 and area < 60000:
    # if w >= 5 and h >= 5:
        obj = image[y:y+h, x:x+w]

        boundaries.append({
            'x': int(x),
            'y': int(y),
            'width': int(w),
            'height': int(h),
        })

# Merge close objects (flower clusters)
merged_boundaries = merge_close_objects(boundaries)

# Save merged objects
for i, boundary in enumerate(merged_boundaries):
    x, y, w, h = boundary['x'], boundary['y'], boundary['width'], boundary['height']
    obj = image[y:y+h, x:x+w]
    idx = boundary['id']
    output_path = os.path.join(OUTPUT_DIR, f'object_{idx}.png')
    cv2.imwrite(output_path, obj)

# Save boundary information to a JSON file
with open(BOUNDARY_FILE, 'w') as f:
    json.dump(merged_boundaries, f, indent=4)

print(f"Successfully extracted {len(merged_boundaries)} objects, saved in the '{OUTPUT_DIR}' folder.")
print(f"Boundary information saved to '{BOUNDARY_FILE}' file.")
