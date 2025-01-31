# Nihilism Compression Algorithm
# This is a Python script that reads an image and compresses it using the Nihilism Compression Algorithm.
# The algorithm converts each BLOCK into a gradient from the darkest to the brightest pixel in the block.
# Each bright or dark pixel is recorded as a bit minimal offset from block origin plus 24 bit color, 8 bits per rgb.

# uncompressed 16 x 16 block: 256 pixels, each 24 bits = 6144 bits
# compressed   16 x 16 block: 2 pixels, each 4 bits uv + 24 bits per color = 64 bits
# compression ratio = 96:1

# uncompressed 32 x 32 block: 1024 pixels, each 24 bits = 24576 bits
# compressed   32 x 32 block: 2 pixels, each 10 bits uv + 24 bits per color = 68 bits
# compression ratio = 360:1

# uncompressed 64 x 64 block: 4096 pixels, each 8 bits per rgb color component = 98304 bits
# compressed   64 x 64 block; 2 pixels, each 12 bits uv + 24 bits per color = 72 bits
# compression ratio = 1365:1

from PIL import Image
BLOCK_WIDTH = 64
BLOCK_HEIGHT = 64

source_image = Image.open('2025/Jan.22/source_img/ling_hua.webp')
source_pixels = source_image.load()
result_width = (source_image.width // BLOCK_WIDTH) * BLOCK_WIDTH
result_height = (source_image.height // BLOCK_HEIGHT) * BLOCK_HEIGHT
result_image = Image.new('RGB', (result_width, result_height))
result_pixels = result_image.load()

def find_block_min_max(pixels, x_start, y_start, block_width, block_height):
    min_color = (255, 255, 255)
    max_color = (0, 0, 0)
    min_offset = (0, 0)
    max_offset = (block_width - 1, block_height - 1)
    for y in range(y_start, y_start + block_height):
        for x in range(x_start, x_start + block_width):
            r, g, b = pixels[x, y]
            brightness = r + g + b
            if brightness > sum(max_color):
                max_color = (r, g, b)
                max_offset = (x - x_start, y - y_start)
            if brightness < sum(min_color):
                min_color = (r, g, b)
                min_offset = (x - x_start, y - y_start)
        progress = (y * source_image.width) / (source_image.width * source_image.height)
        print(f"\rreading source blocks [{'.' * int(progress * 32) + ' ' * (32 - int(progress * 32))}]", end='')
    return max_offset, max_color, min_offset, min_color

def draw_gradient(result_pixels, block_origin_x, block_origin_y, offset_min, color_min, offset_max, color_max, block_width, block_height):
    gradient_vector = (offset_max[0] - offset_min[0], offset_max[1] - offset_min[1])
    gradient_length_squared = gradient_vector[0] ** 2 + gradient_vector[1] ** 2
    for v in range(block_height):
        for u in range(block_width):
            this_vector = (u - offset_min[0], v - offset_min[1])
            dot_product = this_vector[0] * gradient_vector[0] + this_vector[1] * gradient_vector[1]
            mix = dot_product / gradient_length_squared if gradient_length_squared != 0 else 0.0
            t = max(0.0, min(1.0, mix)) # Clamp mix between 0 and 1
            r = int(color_min[0] + (color_max[0] - color_min[0]) * t)
            g = int(color_min[1] + (color_max[1] - color_min[1]) * t)
            b = int(color_min[2] + (color_max[2] - color_min[2]) * t)
            result_pixels[block_origin_x + u, block_origin_y + v] = (r, g, b)

this_block_width = BLOCK_WIDTH
this_block_height = BLOCK_HEIGHT
# Process the image in blocks
block_size = BLOCK_WIDTH
while block_size >= 4:
    this_block_width = block_size
    this_block_height = block_size
    for y in range(0, result_height, this_block_height):
        for x in range(0, result_width, this_block_width):
            brightest_offset, brightest_color, darkest_offset, darkest_color = \
                find_block_min_max(source_pixels, x, y, this_block_width, this_block_height)
            
            draw_gradient(
                result_pixels=result_pixels,
                block_origin_x=x,
                block_origin_y=y,
                offset_min=brightest_offset,
                color_min=brightest_color,
                offset_max=darkest_offset,
                color_max=darkest_color,
                block_width=this_block_width,
                block_height=this_block_height
            )
    
    output_filename = f'2025/Jan.22/output_img/rgb_block_size_{block_size:02d}.png'
    result_image.save(output_filename)
    print(f'Saved {output_filename}')
    block_size //= 2