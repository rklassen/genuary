# Nihilism Compression Algorithm - YCbCr
# In YCbCr color space, and with block size of 4x4 for Y, 16x16 for Cb and Cr, find the minimum and maximum
# value per block per component, and draw a gradient from the corresponding offsets and values to the output
# YCbCr image, then convert back to rgb and write to file.

# for a given 16x16 block:
# the uncompressed image has 24 bits, 8 bit per rgb component, per pixel and 256 pixels per block = 6144 bits per block

# compressed y has 16 subblocks of 4x4 pixels, each block has a brightest and darkest pixel, 2 bits each for u and v offset from block
# origin, 2 bits each for the brightest and darkest pixel value = 16 * ( (2 + 2 )vectors + ( 2 + 2)values = 128 bits per block
# compressed cb and cr each have 4 bits for each u and v offset from block origin, 3 bits each for brightest and darkest pixel.
# (4 + 4 + 3 + 3) = 14 bits per block per component, 2 components = 28 bits per block
# combined, the compressed image has 156 bits per block, a compression ratio of 39.4:1


# 1536 x 1024 pixels = 96 blocks wide and 64 blocks tall at 16x16 blocks
total_bits = 1867776

from PIL import Image
BLOCK_WIDTH = 8
BLOCK_HEIGHT = 8
BLOCK_WIDTH_Y = 4
BLOCK_WIDTH_CB = 4 * BLOCK_WIDTH_Y
BLOCK_WIDTH_CR = BLOCK_WIDTH_CB
QUANTIZE_Y_LEVELS = 32
QUANTIZE_CB_LEVELS = 2 * QUANTIZE_Y_LEVELS
QUANTIZE_CR_LEVELS = QUANTIZE_CB_LEVELS

# see 2025/Jan.22/readme.md for credits
source_image = Image.open('2025/Jan.22/source_img/neon-wang.webp')
source_pixels = source_image.load()
source_ycbcr = source_image.convert('YCbCr')
source_ycbcr_pixels = source_ycbcr.load()

def find_block_min_max(pixels, block_width: int, component_index: int, block_origin_x, block_origin_y):
    min_value = 255
    max_value = 0
    min_offset = (0, 0)
    max_offset = (block_width - 1, block_width - 1)
    for v in range(block_width):
        for u in range(block_width):
            value = pixels[block_origin_x + u, block_origin_y + v][component_index]
            if value < min_value:
                min_value = value
                min_offset = (u, v)
            if value > max_value:
                max_value = value
                max_offset = (u, v)
    return max_offset, max_value, min_offset, min_value

def draw_gradient(result_pixels, block_size, block_origin, offset_min, value_min, offset_max, value_max):
    block_width, block_height = block_size
    block_origin_x, block_origin_y = block_origin
    gradient_vector = (offset_max[0] - offset_min[0], offset_max[1] - offset_min[1])
    gradient_length_squared = gradient_vector[0] ** 2 + gradient_vector[1] ** 2
    for v in range(block_height):
        for u in range(block_width):
            this_vector = (u - offset_min[0], v - offset_min[1])
            dot_product = this_vector[0] * gradient_vector[0] + this_vector[1] * gradient_vector[1]
            mix = dot_product / gradient_length_squared if gradient_length_squared != 0 else 0.0
            t = max(0.0, min(1.0, mix)) # Clamp mix between 0 and 1
            value = int(value_min + (value_max - value_min) * t)
            x = block_origin_x + u
            y = block_origin_y + v
            result_pixels[x, y] = (value, value, value)

def quantize(value, levels):
    height = 255.0 / (1.0 + float(levels))
    offset = 0.5 * height
    level = max(0, int((value + offset) // height))
    return min(255, int(level * height))

output_size = (64 * int(source_image.width//64), 64 * int(source_image.height // 64))
image_y = Image.new('RGB', output_size)
pixels_y = image_y.load()
for y in range(0, output_size[1], BLOCK_WIDTH_Y):
    for x in range(0, output_size[0], BLOCK_WIDTH_Y):
        max_offset, max_value, min_offset, min_value = find_block_min_max(source_ycbcr_pixels, BLOCK_WIDTH_Y, 0, x, y)
        min_value = quantize(min_value, QUANTIZE_Y_LEVELS)
        max_value = quantize(max_value, QUANTIZE_Y_LEVELS)
        draw_gradient(pixels_y, (BLOCK_WIDTH_Y, BLOCK_WIDTH_Y), (x, y), min_offset, min_value, max_offset, max_value)
    progress = y / source_image.height
    print(f"\rprocessing blocks Y  [{'.' * int(progress * 32) + ' ' * (32 - int(progress * 32))}]", end='')
image_y.save('2025/Jan.22/2025jan22_Y_block_04.png')

image_cb = Image.new('RGB', output_size)
pixels_cb = image_cb.load()
for y in range(0, output_size[1], BLOCK_WIDTH_CB):
    for x in range(0, output_size[0], BLOCK_WIDTH_CB):
        max_offset, max_value, min_offset, min_value = find_block_min_max(source_ycbcr_pixels, BLOCK_WIDTH_CB, 1, x, y)
        min_value = quantize(min_value, QUANTIZE_CB_LEVELS)
        max_value = quantize(max_value, QUANTIZE_CB_LEVELS)
        draw_gradient(pixels_cb, (BLOCK_WIDTH_CB, BLOCK_WIDTH_CB), (x, y), min_offset, min_value, max_offset, max_value)
    progress = y / source_image.height
    print(f"\rprocessing blocks Cb [{'.' * int(progress * 32) + ' ' * (32 - int(progress * 32))}]", end='')
image_cb.save(f'2025/Jan.22/2025jan22_Cb_block_{BLOCK_WIDTH_CB:02d}.png')


image_cr = Image.new('RGB', output_size)
pixels_cr = image_cr.load()
for y in range(0, output_size[1], BLOCK_WIDTH_CR):
    for x in range(0, output_size[0], BLOCK_WIDTH_CR):
        max_offset, max_value, min_offset, min_value = find_block_min_max(source_ycbcr_pixels, BLOCK_WIDTH_CR, 2, x, y)
        min_value = quantize(min_value, QUANTIZE_CR_LEVELS)
        max_value = quantize(max_value, QUANTIZE_CR_LEVELS)
        draw_gradient(pixels_cr, (BLOCK_WIDTH_CR, BLOCK_WIDTH_CR), (x, y), min_offset, min_value, max_offset, max_value)
    progress = y / source_image.height
    print(f"\rprocessing blocks Cr [{'.' * int(progress * 32) + ' ' * (32 - int(progress * 32))}]", end='')
image_cr.save(f'2025/Jan.22/2025jan22_Cr_block_{BLOCK_WIDTH_CR:02d}.png')

final_image = Image.new('YCbCr', output_size)
final_pixels = final_image.load()
for y in range(output_size[1]):
    for x in range(output_size[0]):
        y_value = pixels_y[x, y][0]
        cb_value = pixels_cb[x, y][0]
        cr_value = pixels_cr[x, y][0]
        final_pixels[x, y] = (y_value, cb_value, cr_value)
final_image_rgb = final_image.convert('RGB')
filename = '2025/Jan.22/output_img/ycbcr.png'
final_image_rgb.save(filename)
print(f'\nSaved to {filename}')