from PIL import Image
import os

# Japan Street Night by MasashiWakui https://pixabay.com/users/masashiwakui-4385858/
# https://pixabay.com/photos/japan-street-night-osaka-asia-2014618/
# Espresso photo, uncredited
# https://pixabay.com/photos/coffee-cappuccino-latte-espresso-4334647/

source_img = Image.open('./2025/Mar.08/input/japan-2014618.jpg')
output_path = './2025/Mar.08/input/japan_sq.png'
#source_img = Image.open('./2025/Mar.08/input/coffee-4334647.jpg')
#output_path = './2025/Mar.08/input/coffee_sq.png'
print(f'Opened {source_img.filename}. Image size: {source_img.size}, format: {source_img.format}')

# crop and rescale to 512 x 512
square_size = min(source_img.size[0], source_img.size[1])
left = (source_img.size[0] - square_size) // 2
top = (source_img.size[1] - square_size) // 2
right = left + square_size
bottom = top + square_size
square_img = source_img.crop((left, top, right, bottom))
resized_img = square_img.resize((512, 512))

# save
os.makedirs(os.path.dirname(output_path), exist_ok=True)
resized_img.save(output_path)
print(f'Saved cropped and scaled image to {resized_img.size}')
