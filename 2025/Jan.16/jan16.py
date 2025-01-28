from PIL import Image, ImageDraw
from math import sin, cos
import os, random

# pseudostruct
class ColorCategory:
    def __init__(self, s_min, s_max, l_min, l_max):
        self.s_min = s_min
        self.s_max = s_max
        self.l_min = l_min
        self.l_max = l_max

# pseudoconsts
PALETTE_COLOR_MIN = 214
PALETTE_COLOR_MAX = 218
PALETTE_RADIUS = 0.025
IMG_WIDTH = 1024
# thanks to https://medium.com/@vermaayushi713
# https://medium.com/design-bootcamp/understanding-color-theory-part-3-f3b7a61c8790
earth  = ColorCategory(0.36, 0.41, 0.36, 0.77)
greys  = ColorCategory(0.00, 0.04, 0.00, 1.00)
jewel  = ColorCategory(0.73, 0.83, 0.56, 0.76)
muted  = ColorCategory(0.04, 0.10, 0.70, 0.80) # modified from article, then not used
neon   = ColorCategory(0.63, 1.00, 0.82, 1.00)
pastel = ColorCategory(0.14, 0.21, 0.82, 0.92) # modified from article
CATEGORIES = [earth, jewel, neon, pastel]
paint_uv = [(0.1, 0.4), (0.2, 0.2), (0.4, 0.1), (0.63, 0.07)]

# init mask and def helper functions
mask = Image.open('mask.png')
u_max, v_max, mask_width = 1.0, mask.size[1] / mask.size[0], mask.size[0]
os.makedirs('.frames', exist_ok=True)
index = 0

def is_inside_mask(u, v, radius):  # radius in uv space
    theta = 0.0
    while theta < 6.28:  # sample 24 points along the perimeter
        u_test, v_test = u + radius * cos(theta), v + radius * sin(theta)
        xy_test = (int(u_test * mask_width), int(v_test * mask_width))
        if u_test <= 0 or u_test >= 1 or v_test <= 0 or v_test >= v_max \
                or mask.getpixel(xy_test)[0] > 128:
            return False
        theta += 6.28 / 7.0
    return True

def hsl_to_rgb(h, s, l):  # hue in radians; s, l in [0, 1]
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 1.047) % 2 - 1))
    m = l - c / 2
    lookup = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)]
    r, g, b = [int((c + m) * 255) for c in lookup[int(h // 1.047)]]
    return (r, g, b)

def generate_palette(category: ColorCategory):
    # generate a randomized palette of tetrad colors within this color category sat and lum ranges
    # https://blog.matthewgove.com/2021/07/02/color-theory-a-simple-exercise-in-mathematics-and-graphic-design/
    hue_00 = random.uniform(0, 3.14)
    hue_01 = hue_00 + 3.13
    hue_02 = hue_00 + random.uniform(3.14/6, 5*3.14/6)
    hue_03 = (hue_02 + 3.14) % 6.28
    hues = [hue_00, hue_01, hue_02, hue_03]
    random.shuffle(hues)
    colors = [hsl_to_rgb(hue,
                         random.uniform(category.s_min, category.s_max),
                         random.uniform(category.l_min, category.l_max)) for hue in hues]
    return colors

# region draw palette
for _ in range(6):
    for category in CATEGORIES:
        new_image = Image.new('RGB', (IMG_WIDTH, int(IMG_WIDTH * v_max / u_max)), 'white')
        draw = ImageDraw.Draw(new_image)

        grid = PALETTE_RADIUS / 2.25
        jitter = PALETTE_RADIUS / 8
        radius = int(PALETTE_RADIUS * IMG_WIDTH)
        for v in range(0, int(v_max / grid)):
            for u in range(0, int(u_max / grid)):
                uj, vj = u * grid, v * grid
                if not is_inside_mask(uj, vj, PALETTE_RADIUS):
                    continue
                uj += random.uniform(-jitter, jitter)
                vj += random.uniform(-jitter, jitter)
                x, y = (int(uj * IMG_WIDTH), int(vj * IMG_WIDTH))
                l_min = 1.0 - category.l_max
                l_max = 0.5 * (l_min + 1.0 - category.l_min)
                color = hsl_to_rgb(random.uniform(0, 0.9), 0.04, random.uniform(l_min, l_max))
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
        
        colors = generate_palette(category)
        for color, uv in zip(colors, paint_uv):
            x, y = int(uv[0] * IMG_WIDTH), int(uv[1] * IMG_WIDTH)
            diameter = int(0.2 * IMG_WIDTH)
            draw.ellipse((x, y, x + diameter, y + diameter), fill=color)

        filename = f'.frames/palette_{index:02d}.png'
        new_image.save(filename)
        print(f'Generated {filename}')
        index += 1