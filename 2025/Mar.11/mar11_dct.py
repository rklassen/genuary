import copy, os, numpy
from PIL import Image
from scipy.fft import dctn, idctn

# dct part 2.
# perform 2d dct on the image. zero the lower frequencies. perform inverse dct.
# save the result.

# Japan Street Night by MasashiWakui https://pixabay.com/users/masashiwakui-4385858/
# https://pixabay.com/photos/japan-street-night-osaka-asia-2014618/
# Espresso photo, uncredited
# https://pixabay.com/photos/coffee-cappuccino-latte-espresso-4334647/

img = Image.open('./2025/Mar.08/input/japan_sq.png').convert('YCbCr')
channel_names = ['y', 'cb', 'cr']
channels = img.split()
os.makedirs("./2025/Mar.11/debug/", exist_ok=True)
width, height = img.size
r_max = int(((width / 2) ** 2 + (height / 2) ** 2) ** 0.5)

dct_data = [ ]
for index in range(3):
    name, ch = channel_names[index], channels[index]
    this_dct = dctn(numpy.array(ch, dtype=float))
    dct_data.append(this_dct)

this_dct_data = copy.deepcopy(dct_data)

with open('./2025/Mar.11/input/_counter.md', 'r') as file:
    counter = int(file.readline().strip())
counter += 1
with open('./2025/Mar.11/input/_counter.md', 'w') as file:
    file.write(str(counter))

mask = Image.open('./2025/Mar.11/input/dc_mask.webp').convert('L')
mask_array = numpy.array(mask, dtype=float)
shifted_mask = numpy.roll(mask_array, shift=(height // 2, width // 2), axis=(0, 1))
shifted_mask_img = Image.fromarray(shifted_mask.astype(numpy.uint8))
os.makedirs("./2025/Mar.11/debug/", exist_ok=True)
shifted_mask_img.save(f'./2025/Mar.11/debug/mask {counter:03d}.webp')


# mask 
for x in range(int(width)):
    for y in range(int(height)):
        mask = 0.0 if mask_array[x, y] < 10 else 1.0
        this_dct_data[0][x, y] *= mask
        this_dct_data[1][x, y] *= mask
        this_dct_data[2][x, y] *= mask

    frac = (1 + x) / width
    filled = int(frac * 32)
    bar = "▪" * filled + "▶" + " " * (32 - filled)
    percent = frac * 100
    print(f'\r[{bar}] {x} of {width} ({percent:.2f}%)', end='')

idct_data = [ ]
for channel_index in range(3):
    idct_data.append(idctn(this_dct_data[channel_index]).clip(0, 255).astype(numpy.uint8))

#idct_data[0][:] = 128

merged = Image.merge("YCbCr", [Image.fromarray(channel) for channel in idct_data]).convert("RGB")
os.makedirs("./2025/Mar.11/output/", exist_ok=True)
merged.save(f'./2025/Mar.11/output/mar11 {counter:03d}.png')
