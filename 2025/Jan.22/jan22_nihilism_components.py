from PIL import Image
from PIL import ImageDraw
BLOCK_WIDTH = 16
BLOCK_HEIGHT = 16

source_image = Image.open('2025/Jan.22/ethan-dow.webp')
source_pixels = source_image.load()
# component is 0 for red, 1 for green, 2 for blue
# uses BLOCK_WIDTH and BLOCK_HEIGHT as global psuedo-constants

component_names = ['red', 'green', 'blue']
def find_block_min_max(pixels, block_origin_x, block_origin_y, component):  
    min_value = 255
    max_value = 0
    min_offset = (0, 0)
    max_offset = (BLOCK_WIDTH - 1, BLOCK_HEIGHT - 1)
    for y in range(block_origin_y, block_origin_y + BLOCK_HEIGHT):
        for x in range(block_origin_x, block_origin_x + BLOCK_WIDTH):
            value = pixels[x, y][component]
            if value > max_value:
                max_value = value
                max_offset = (x - block_origin_x, y - block_origin_y)
            if value < min_value:
                min_value = value
                min_offset = (x - block_origin_x, y - block_origin_y)
        progress = (y * source_image.width) / (source_image.width * source_image.height)
        print(f"\rreading source blocks {component_names[component]} [{'.' * int(progress * 32) + ' ' * (32 - int(progress * 32))}]", end='')
    return max_offset, max_value, min_offset, min_value

def draw_gradient(result_pixels, block_origin_x, block_origin_y, offset_min, color_min, offset_max, color_max):
    gradient_vector = (offset_max[0] - offset_min[0], offset_max[1] - offset_min[1])
    gradient_length_squared = gradient_vector[0] ** 2 + gradient_vector[1] ** 2
    for v in range(BLOCK_HEIGHT):
        for u in range(BLOCK_WIDTH):
            this_vector = (u - offset_min[0], v - offset_min[1])
            dot_product = this_vector[0] * gradient_vector[0] + this_vector[1] * gradient_vector[1]
            mix = dot_product / gradient_length_squared if gradient_length_squared != 0 else 0.0
            t = max(0.0, min(1.0, mix)) # Clamp mix between 0 and 1
            value = int(color_min + (color_max - color_min) * t)
            result_pixels[block_origin_x + u, block_origin_y + v] = (value, value, value)

# Create separate images for each RGB component
result_images = [Image.new('RGB', source_image.size) for _ in range(3)]
result_pixels_list = [img.load() for img in result_images]

# Process the image in blocks for each component
for component in range(3):
    for y in range(0, source_image.height, BLOCK_HEIGHT):
        for x in range(0, source_image.width, BLOCK_WIDTH):
            brightest_offset, brightest_color, darkest_offset, darkest_color = \
                find_block_min_max(source_pixels, x, y, component)
            draw_gradient(result_pixels_list[component], x, y, brightest_offset, brightest_color, darkest_offset, darkest_color)

# Save the resulting images
result_images[0].save('2025/Jan.22/2025jan22_red.png')
result_images[1].save('2025/Jan.22/2025jan22_green.png')
result_images[2].save('2025/Jan.22/2025jan22_blue.png')

# Combine the RGB component images into one final image
final_image = Image.new('RGB', source_image.size)
final_pixels = final_image.load()

for y in range(source_image.height):
    for x in range(source_image.width):
        r = result_pixels_list[0][x, y][0]
        g = result_pixels_list[1][x, y][1]
        b = result_pixels_list[2][x, y][2]
        final_pixels[x, y] = (r, g, b)
    progress = (y * source_image.width) / (source_image.width * source_image.height)
    print(f"\rcompositing final image [{'.' * int(progress * 32) + ' ' * (32 - int(progress * 32))}]", end='')

# Save the final combined image
final_image.save('2025/Jan.22/2025jan22_components.png')
print ('Finished.')