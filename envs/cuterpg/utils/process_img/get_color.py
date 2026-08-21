from PIL import Image
from collections import Counter

def extract_colors(image_path):
    """
    Extracts all unique colors from the given PNG image.

    Parameters:
    - image_path (str): Path to the PNG image.

    Returns:
    - color_counts (dict): A dictionary with color tuples as keys and their counts as values.
    """
    # Open the image and ensure it's in RGBA mode
    img = Image.open(image_path).convert("RGBA")
    pixels = list(img.getdata())

    # Count occurrences of each color
    color_counts = Counter(pixels)

    # Display all colors
    print(f"Total unique colors: {len(color_counts)}")
    for color, count in color_counts.items():
        print(f"Color RGBA {color} - Count: {count}")

    return color_counts

if __name__ == "__main__":
    # Example usage
    # image_path = "NavigationMap/assets/extracted_objects/object_55.png"  # Replace with your PNG file path
    image_path = "NavigationMap/assets/winter_objects/object_35.png"  # Replace with your PNG file path
    color_data = extract_colors(image_path)