from PIL import Image, ImageDraw
from math import sin, cos
import random
PALETTE_COLOR_MIN = 214
PALETTE_COLOR_MAX = 218
PALETTE_RADIUS = 0.025
IMG_WIDTH = 1024

# region init
mask = Image.open('mask.png')
u_max, v_max, mask_width = 1.0, mask.size[1] / mask.size[0], mask.size[0]
new_image = Image.new('RGB', (IMG_WIDTH, int(IMG_WIDTH * v_max / u_max)), 'white')
draw = ImageDraw.Draw(new_image)

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

def hsl_to_rgb(h, s, l):  # h in [0, 6.28], s, l in [0, 1]
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 1.047) % 2 - 1))
    m = l - c / 2
    lookup = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)]
    r, g, b = [int((c + m) * 255) for c in lookup[int(h // 1.047)]]
    return (r, g, b)
#endregion

# region draw palette
grid = PALETTE_RADIUS / 3
jitter = PALETTE_RADIUS / 2
for v in range(0, int(v_max / grid)):
    for u in range(0, int(u_max / grid)):
        uj = u * grid + random.uniform(-jitter, jitter)
        vj = v * grid + random.uniform(-jitter, jitter)
        if not is_inside_mask(uj, vj, PALETTE_RADIUS):
            continue
        x, y = (int(uj * IMG_WIDTH), int(vj * IMG_WIDTH))
        color = hsl_to_rgb(random.uniform(0, 1), 0.04, random.uniform(0.82, 0.86))
        radius = int(PALETTE_RADIUS * IMG_WIDTH)
        draw.ellipse((x - radius, y - radius, x +
                     radius, y + radius), fill=color)
# endregion
new_image.show()
new_image.save('2025jan16.png')