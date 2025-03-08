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
os.makedirs("./2025/Mar.08/debug/", exist_ok=True)
width, height = img.size
r_max = int(((width / 2) ** 2 + (height / 2) ** 2) ** 0.5)

dct_data = [ ]
for index in range(3):
    name, ch = channel_names[index], channels[index]
    ch.convert("L").save(f"./2025/Mar.08/debug/source_{name}.png")
    this_dct = dctn(numpy.array(ch, dtype=float))
    dct_data.append(this_dct)
    Image.fromarray(this_dct.astype(numpy.uint8)).save(f"./2025/Mar.08/debug/dct_{name}.png")
    this_dct_normalized = (this_dct - this_dct.min()) / (this_dct.max() - this_dct.min()) * 255


for radius in range(r_max):
    this_frame_ch = [ ]
    for ch_index in range(3):
        this_channel = copy.deepcopy(dct_data[ch_index])
        for x in range(width):
            for y in range(height):
                if ((x - width / 2) ** 2 + (y - height / 2) ** 2) ** 0.5 > radius:
                    this_channel[x, y] = 0
        this_channel_denormalized = this_channel * (dct_data[ch_index].max() - dct_data[ch_index].min()) + dct_data[ch_index].min()
        idct_data = idctn(this_channel_denormalized).clip(0, 255).astype(numpy.uint8)
        #idct_data = idctn(this_channel).clip(0, 255).astype(numpy.uint8)
        this_frame_ch.append(idct_data)

    merged = Image.merge("YCbCr", [Image.fromarray(c) for c in this_frame_ch]).convert("RGB")
    merged.save(f"./2025/Mar.08/frames/frame {str(radius).zfill(3)}.png")

    frac = radius / (r_max - 1) if r_max > 1 else 1
    filled = int(frac * 32)
    bar = "▶" * filled + " " * (32 - filled)
    percent = frac * 100
    print(f'\r[{bar}] frame {radius} of {r_max} ({percent:.2f}%)', end='')

