from PIL import Image, ImageSequence
import os

# Load all images from the 'gif' subfolder
image_folder = './2025/Mar.11/gif/'
images = [Image.open(os.path.join(image_folder, file)) 
          for file in sorted(os.listdir(image_folder))
            if file.endswith(('webp', 'png', 'jpg'))]

# Create the forward and backward sequence for the zigzag pattern, playing each end image only once
frames = images + images[-1:0:-1]

# Save as an animated GIF
output_path = './2025/Mar.11/mar11.gif'
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=650, loop=0)

# Convert each PNG in the gif folder to WEBP format
for file in os.listdir(image_folder):
  if file.endswith('png'):
    img = Image.open(os.path.join(image_folder, file))
    webp_path = os.path.join(image_folder, os.path.splitext(file)[0] + '.webp')
    img.save(webp_path, 'WEBP')