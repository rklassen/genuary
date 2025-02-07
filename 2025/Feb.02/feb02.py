# This is a study/experiment
# That uses hexagonal screentone pattern and DCT to employ as
# a resolution-independent raster compression algorithm.
from PIL import Image, ImageDraw
import csv
import numpy as np
import os

def save_y_cbcr_images(ycbcr_image, quantize_levels, folder_path):
    y, cb, cr = ycbcr_image.split()
    y_image = Image.merge("L", (y,))
    mesne_folder = os.path.join(folder_path, 'mesne')
    if not os.path.exists(mesne_folder):
        os.makedirs(mesne_folder)
    y_image.save(f'{mesne_folder}quantized_y_{quantize_levels:03d}.webp', "WEBP", quality=65)
    uniform_y = Image.new("L", y.size, 128)
    cb = np.array(cb)
    cr = np.array(cr)
    cb_quantized = (cb // (256 // quantize_levels)) * (256 // quantize_levels)
    cr_quantized = (cr // (256 // quantize_levels)) * (256 // quantize_levels)
    cb_quantized = Image.fromarray(cb_quantized, mode="L")
    cr_quantized = Image.fromarray(cr_quantized, mode="L")
    cbcr_quantized_image = Image.merge("YCbCr", (uniform_y, cb_quantized, cr_quantized)).convert("RGB")
    cbcr_quantized_image.save(f'{mesne_folder}quantized_cbcr_{quantize_levels:03d}.webp', "WEBP", quality=65)

def create_hexagon_pattern_image(width, height):
    image = Image.new("1", (width, height), 0)
    draw = ImageDraw.Draw(image)
    hex_size = min(width, height) // 2
    hexagon = [
        (width // 2 + hex_size * 0.5, height // 2 + hex_size),
        (width // 2 + hex_size * 1.0, height // 2 + 0.0),
        (width // 2 + hex_size * 0.5, height // 2 - hex_size),
        (width // 2 - hex_size * 0.5, height // 2 - hex_size),
        (width // 2 - hex_size * 1.0, height // 2 + 0.0),
        (width // 2 - hex_size * 0.5, height // 2 + hex_size)
    ]
    draw.polygon(hexagon, fill=1)
    return image

def calculate_y_averages(source_ycrcb):
    y, cb, cr = source_ycrcb.split()
    y = np.array(y).astype(np.float32) / 127.5 - 1.0
    height, width = y.shape
    y_average_u = np.mean(y, axis=0)
    y_average_v = np.mean(y, axis=1)
    y_average_t = np.zeros(width, dtype=np.float32)
    for u in range(width):
        total_value = 0.0
        for v in range(height):
            t = (u + v) % width
            total_value += y_average_u[t]
        y_average_t[u] = total_value / float(height)
    return y_average_u, y_average_v, y_average_t



# region split source into y cb cr and calculate the average y in u v and t axes
source_image = Image.open('2025/Feb.02/source/source00.webp')
source_image = source_image.resize((256, 256))
source_ycrcb = source_image.convert("YCbCr")
save_y_cbcr_images(source_ycrcb, 128, '/Users/richardklassen/Developer/genuary/2025/Feb.02/mesne/')

y_average_u, y_average_v, y_average_t = calculate_y_averages(source_ycrcb)

w, h = source_ycrcb.width, source_ycrcb.height
dct_values_x = np.zeros(width, dtype=np.float32)
dct_values_y = np.zeros(height, dtype=np.float32)
dct_values_z = np.zeros(width, dtype=np.float32)

for u in range(width):
    total_weight = 0.0
    for x in range(width):
        total_weight += np.cos(np.pi * x * u / width) * y_average_u[x]
    dct_values_x[x] = total_weight

for v in range(height):
    total_weight = 0.0
    for y in range(height):
        total_weight += np.cos(np.pi * y * v / height) * y_average_v[y]
    dct_values_y[y] = total_weight

for t in range(width):
    total_weight = 0.0
    for z in range(width):
        total_weight += np.cos(np.pi * z * t / width) * y_average_t[z]
    dct_values_z[z] = total_weight

raw_dct_image = Image.new("L", (width, height))
raw_dct_pixels = raw_dct_image.load()
for x in range(width):
    for y in range(height):
        t = (x + y) % width
        dct_value = int(dct_values_x[x] * dct_values_y[y] * dct_values_z[t])
        raw_dct_pixels[x, y] = dct_value
raw_dct_image.save("/Users/richardklassen/Developer/genuary/2025/Feb.02/dct_image.webp", "WEBP", quality=65)

# Reverse the DCT to recreate the image
reconstructed_y = np.zeros((height, width), dtype=np.float32)
for x in range(width):
    for y in range(height):
        z = (x + y) % width
        reconstructed_y[y, x] = (dct_values_x[x] * dct_values_y[y] * dct_values_z[t]) / (127.5 * 127.5 * 127.5) - 1.0

