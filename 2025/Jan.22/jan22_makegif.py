import os
from PIL import Image

# Define the order of the PNG files
filename_prefix = '2025/Jan.22/nihilismcompression_block_size'
file_order = ["_64.png", "_32.png", "_16.png", "_08.png", "_04.png", "_08.png", "_16.png", "_32.png"]

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the images in the specified order
images = []
for suffix in file_order:
    images.append(Image.open(filename_prefix + suffix))

# Save as a looping GIF with 1.15 seconds per frame
if images:
    images[0].save(
        os.path.join(script_dir, "2025jan22_nihilism.gif"),
        save_all=True,
        append_images=images[1:],
        duration=1150,
        loop=0
    )