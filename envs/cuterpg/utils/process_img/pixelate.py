from PIL import Image
import numpy as np
import cv2
from sklearn.cluster import KMeans
from pdb import set_trace as st

def pixelate_image(image_path, max_size=40, num_colors=10):
    """
    Loads an image, preserves transparency, reduces the number of colors before resizing,
    resizes it while maintaining aspect ratio, and applies a pixelation effect.

    :param image_path: Path to the input image
    :param max_size: The maximum width or height of the output image
    :param num_colors: The number of colors to reduce the image to
    :return: PIL Image (pixelated)
    """

    # Load the image
    img = Image.open(image_path)

    # Check if image has an alpha (transparency) channel
    has_alpha = img.mode == "RGBA"

    if has_alpha:
        # Split into RGB and Alpha channel
        img_rgb, alpha = img.convert("RGB"), img.getchannel("A")
    else:
        img_rgb = img

    # Convert to NumPy array
    img_array = np.array(img_rgb)

    # Flatten the image array for k-means clustering
    pixels = img_array.reshape(-1, 3)  # Reshape to (num_pixels, 3) RGB format

    # Apply k-means clustering to reduce colors **before resizing**
    kmeans = KMeans(n_clusters=num_colors, n_init=20, random_state=0)
    labels = kmeans.fit_predict(pixels)
    new_colors = kmeans.cluster_centers_.astype(np.uint8)

    # Reconstruct the image using the clustered colors
    clustered_img = new_colors[labels].reshape(img_array.shape)

    # Convert back to PIL Image
    img = Image.fromarray(clustered_img)

    # Resize while maintaining aspect ratio **after color merging**
    original_width, original_height = img.size
    ratio = min(max_size / original_width, max_size / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    img = img.resize((new_width, new_height), Image.NEAREST)

    # Resize Alpha channel separately (if exists)
    if has_alpha:
        alpha = alpha.resize((new_width, new_height), Image.NEAREST)
        img.putalpha(alpha)  # Merge back the alpha channel

    return img

# Example usage
# image_path = "tomato.png"  # Replace with your image path
# image_path = "carrot.png"  # Replace with your image path
# image_path = "potato.png"  # Replace with your image path
# image_path = "lettuce.png"  # Replace with your image path
# image_path = "cucumber.png"  # Replace with your image path
# image_path = "corn.png"  # Replace with your image path
# # pixel_art = pixelate_image(image_path, max_size=48, num_colors=30)
# pixel_art = pixelate_image(image_path, max_size=48, num_colors=40)
# pixel_art.save(f"pixelated_{image_path}")  # Save the image

# def make_white_transparent(image_path, output_path):
#     """
#     Loads a PNG image and makes all pure white (255, 255, 255) pixels transparent.
    
#     :param image_path: Path to the input image.
#     :param output_path: Path to save the output image with transparency.
#     """
#     img = Image.open(image_path).convert("RGBA")
#     data = img.getdata()

#     new_data = []
#     for item in data:
#         # Check if the pixel is pure white
#         if item[:3] == (255, 255, 255):
#             new_data.append((0, 0, 0, 0))  # Make it transparent
#         else:
#             new_data.append(item)

#     img.putdata(new_data)
#     img.save(output_path, "PNG")

#     return output_path


for crop in [
    # "tomato", 
    # "carrot",
    # "potato",
    # "lettuce",
    # "cucumber",
    # "corn",
    "cone",
    # "barricade",
    ]:
    image_path = f"{crop}.png" 
    pixel_art = pixelate_image(image_path, max_size=30, num_colors=40)
    pixel_art.save(f"pixelated_{image_path}")  # Save the image

#     output_image_path = f"trans_{crop}.png"  

#     make_white_transparent(input_image_path, output_image_path)