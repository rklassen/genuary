from math import pi, sin, cos, sqrt
import os
from PIL import Image, ImageFilter
import numpy as np
import cv2  # pip install opencv-python

screen_dpi = 96.0
image_path = '2025/Feb.02/trashcore.galaxy.egg.webp'
image = Image.open(image_path)

# split into components
ycbcr_image = image.convert('YCbCr')
ycbcr_values = ycbcr_image.load()
image_y = Image.new('L', image.size)
image_cr = Image.new('L', image.size)
image_cb = Image.new('L', image.size)
y_pixels = image_y.load()
cr_pixels = image_cr.load()
cb_pixels = image_cb.load()
for x in range(image.size[0]):
    for y in range(image.size[1]):
        y_pixels[x, y], cr_pixels[x, y], cb_pixels[x, y] = ycbcr_values[x, y]

# region STEP 1
# Subsample Cr and Cb components using numpy
cr_array = np.array(image_cr)
cb_array = np.array(image_cb)
height = (image.size[1] // 4) * 4
width = (image.size[0] // 4) * 4
cr_array = cr_array[:height, :width]
cb_array = cb_array[:height, :width]
subsampled_cr_array = cr_array.reshape((height // 4, 4, width // 4, 4)).mean(axis=(1, 3))
subsampled_cb_array = cb_array.reshape((height // 4, 4, width // 4, 4)).mean(axis=(1, 3))
subsampled_cr = Image.fromarray(subsampled_cr_array.astype(np.uint8))
subsampled_cb = Image.fromarray(subsampled_cb_array.astype(np.uint8))
subsampled_cr.save('2025/Feb.18/debug/step_01_cr.png')
subsampled_cb.save('2025/Feb.18/debug/step_01_cb.png')
image_y.save('2025/Feb.18/debug/step_01_y.png')
print('Finished Step 1. Separated image into Y, Cr, and Cb components.')
# endregion

# region STEP 2
# combine cr and cb into chroma slice
chroma_image = Image.new('YCbCr', (width // 4, height // 4))
chroma_pixels = chroma_image.load()
for x in range(width // 4):
    for y in range(height // 4):
        y_value = 128  # Midpoint value for Y component
        cr_value = int(subsampled_cr_array[y, x])
        cb_value = int(subsampled_cb_array[y, x])
        chroma_pixels[x, y] = (y_value, cr_value, cb_value)
rgb_chroma_image = chroma_image.convert('RGB')
rgb_chroma_image.save('2025/Feb.18/debug/step_02_chroma.png')
print('Finished Step 2. Generated chroma image.')
# endregion

# region STEP 3
# Convert chroma_image to CMYK
cmyk_image = chroma_image.convert('CMYK')
cmyk_values = cmyk_image.load()
image_cmy_0 = Image.new('L', cmyk_image.size)
image_cmy_1 = Image.new('L', cmyk_image.size)
image_cmy_2 = Image.new('L', cmyk_image.size)
cmy_pixels_0 = image_cmy_0.load()
cmy_pixels_1 = image_cmy_1.load()
cmy_pixels_2 = image_cmy_2.load()
for x in range(cmyk_image.size[0]):
    for y in range(cmyk_image.size[1]):
        cmy_pixels_0[x, y], cmy_pixels_1[x, y], cmy_pixels_2[x, y], _ = cmyk_values[x, y]
image_cmy_0.save('2025/Feb.18/debug/step_03_cyan.png')
image_cmy_1.save('2025/Feb.18/debug/step_03_magenta.png')
image_cmy_2.save('2025/Feb.18/debug/step_03_yellow.png')
print('Finished Step 3. Separated chroma into CMY components.')
# endregion

# region STEP 4
# Apply a 1 px blur to each CMYK component
image_cmy_0 = image_cmy_0.filter(ImageFilter.GaussianBlur(1)).resize(image.size, Image.Resampling.BILINEAR)
image_cmy_1 = image_cmy_1.filter(ImageFilter.GaussianBlur(1)).resize(image.size, Image.Resampling.BILINEAR)
image_cmy_2 = image_cmy_2.filter(ImageFilter.GaussianBlur(1)).resize(image.size, Image.Resampling.BILINEAR)
image_cmy_0.save('2025/Feb.18/debug/step_04_blur_and_upscale_cyan.png')
image_cmy_1.save('2025/Feb.18/debug/step_04_blur_and_upscale_magenta.png')
image_cmy_2.save('2025/Feb.18/debug/step_04_blur_and_upscale_.png')
print('Finished Step 4. Blur and upscale CMY components')
# endregion

# region STEP 5
component_names = ['cyan', 'magenta', 'yellow']
for component_index in range(3):
    screentone_image = Image.new('L', image.size)
    screentone_values = screentone_image.load()
    f_index = float(component_index)  
    cosine_theta = cos(f_index * pi / 6.0)
    sine_theta = sin(f_index * pi / 6.0)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            x_rotated = cosine_theta * x + sine_theta * y
            y_rotated = -sine_theta * x + cosine_theta * y
            u = float(x_rotated) * screen_dpi / 1079.0
            v = float(y_rotated) * screen_dpi / 1079.0
            value = 0.5 + 0.5 * sin(2 * pi * u) * sin(2 * pi * v)
            color = int(254 * max(0.0, min(1.0, value)))
            screentone_values[x, y] = color
    screentone_image.save(f'2025/Feb.18/debug/step_05_screentone_{component_names[component_index]}.png')
    screentone_image.save(f'2025/Feb.18/output/screentone_{component_index}.png')
    screentone_image.close()
    #print(f'generated screentone {component_index}')
#endregion
print('Finished Step 5. Generated screens.')

# load screentone images from file
screentone_c = Image.open('2025/Feb.18/output/screentone_0.png').load()
screentone_m = Image.open('2025/Feb.18/output/screentone_1.png').load()
screentone_y = Image.open('2025/Feb.18/output/screentone_2.png').load()


# Create screened images for C, M, Y channels
screened_c = Image.new('L', image.size)
screened_m = Image.new('L', image.size)
screened_y = Image.new('L', image.size)
screened_c_pixels = screened_c.load()
screened_m_pixels = screened_m.load()
screened_y_pixels = screened_y.load()
pixels_cmy_0 = image_cmy_0.load()
pixels_cmy_1 = image_cmy_1.load()
pixels_cmy_2 = image_cmy_2.load()

for x in range(image.size[0]):
    for y in range(image.size[1]):
        screened_c_pixels[x, y] = 255 if pixels_cmy_0[x, y] > screentone_c[x, y] else 0
        screened_m_pixels[x, y] = 255 if pixels_cmy_1[x, y] > screentone_m[x, y] else 0
        screened_y_pixels[x, y] = 255 if pixels_cmy_2[x, y] > screentone_y[x, y] else 0

screened_c.save('2025/Feb.18/debug/step_06_screened_c.png')
screened_m.save('2025/Feb.18/debug/step_06_screened_m.png')
screened_y.save('2025/Feb.18/debug/step_06_screened_y.png')
print('Finished Step 6. Screened CMY channels.')


# Final compositing steps was started on Mar 2.

# output_image = Image.new('RGB', image.size)
# output_pixels = output_image.load()

# for x in range(image.size[0]):
#     for y in range(image.size[1]):
#         this_c = screened_c_pixels[x, y] / 255.0
#         this_m = screened_m_pixels[x, y] / 255.0
#         this_y = screened_y_pixels[x, y] / 255.0

#         hue, sat, lightness = cv2.cvtColor(np.array([[[this_c, this_m, l]]], dtype=np.uint8), cv2.COLOR_HLS2RGB)[0][0]
#         # override lightness

#         # end override
#         red, green, blue = cv2.cvtColor(np.array([[[hue, s, l]]], dtype=np.uint8), cv2.COLOR_HLS2RGB)[0][0]
       
#         output_pixels[x, y] = (red, green, blue)

# output_image.save('2025/Feb.18/output/rgb.png')
# print('Generated RGB output image.')


# os.makedirs('2025/Feb.18/output', exist_ok=True)
# output_image = Image.new('RGB', image.size)
# output = output_image.load()
# for x in range(output_image.size[0]):
#     for y in range(output_image.size[1]):
#         c_sdf = screentone_c[x,y]
#         c_sampled = 255.0 * c_values[x,y]
#         c_screened = 0 if c_sampled < c_sdf else 255
#         m_sdf = screentone_m[x,y]
#         m_sampled = 255.0 * m_values[x,y]
#         m_screened = 0 if m_sampled < m_sdf else 255
#         y_sdf = screentone_y[x, y]
#         y_sampled = 255.0 * image_y[x,y]
#         y_screened = 0 if  y_sampled < y_sdf else 255
#         red   = int(255 * m_screened * y_screened)
#         green = int(255 * c_screened * y_screened)
#         blue  = int(255 * c_screened * m_screened)
#         output[x,y] = (red, green, blue)
# filename = f'2025/Feb.18/output/rgb.png'
# output_image.save(filename)
# print(f'Generated {filename}')