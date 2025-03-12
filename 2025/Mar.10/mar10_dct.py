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
os.makedirs("./2025/Mar.10/debug/", exist_ok=True)
os.makedirs("./2025/Mar.10/frames/", exist_ok=True)
width, height = img.size
r_max = int(((width / 2) ** 2 + (height / 2) ** 2) ** 0.5)

dct_data = [ ]
for index in range(3):
    name, ch = channel_names[index], channels[index]
    ch.convert("L").save(f"./2025/Mar.10/debug/source_{name}.png")
    this_dct = dctn(numpy.array(ch, dtype=float))
    dct_data.append(this_dct)
    this_dct_normalized = (this_dct - this_dct.min()) / (this_dct.max() - this_dct.min()) * 255
    Image.fromarray(this_dct.astype(numpy.uint8)).save(f"./2025/Mar.10/debug/dct_{name}.png")


TOTAL_FRAMES = 256 // 3
for distance in range(1, TOTAL_FRAMES):
    this_dct_data = copy.deepcopy(dct_data)
    for x in range(int(width/2)):
        for y in range(int(height/2)):
            if x + y >= distance:
                for index, channel in enumerate(this_dct_data[1:]):
                    channel[x, y] = 0
                    channel[width - x - 1, y] = 0
                    channel[x, height - y - 1] = 0
                    channel[width - x - 1, height - y - 1] = 0
            if x + y >= 2 * distance:
                this_dct_data[0][x, y] = 0
                this_dct_data[0][width - x -1, y] = 0
                this_dct_data[0][x, height - y -1] = 0
                this_dct_data[0][width - x - 1, height - y - 1] = 0
    
    idct_data = [ ]
    for channel_index in range(3):
        this_idct = idctn(this_dct_data[channel_index])
        idct_data.append(this_idct.clip(0, 255).astype(numpy.uint8))

    #idct_data[0][:] = 128

    merged = Image.merge("YCbCr", [Image.fromarray(channel) for channel in idct_data]).convert("RGB")
    merged.save(f"./2025/Mar.10/frames/frame {str(distance).zfill(3)}.png")

    frac = (1 + distance) / TOTAL_FRAMES
    filled = int(frac * 32)
    bar = "▪" * filled + "▶" + " " * (32 - filled)
    percent = frac * 100
    print(f'\r[{bar}] {distance} of {TOTAL_FRAMES} ({percent:.2f}%)', end='')