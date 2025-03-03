from PIL import Image

# Continue from Feb.18 results
luma     = Image.open('./2025/Mar.02/input/step_01_y.png').load()
cyan     = Image.open('./2025/Mar.02/input/step_06_screened_c.png').load()
magenta  = Image.open('./2025/Mar.02/input/step_06_screened_m.png').load()
yellow   = Image.open('./2025/Mar.02/input/step_06_screened_y.png').load()
original = Image.open('./2025/Mar.02/input/original.webp')
orig_pix = original.load()

def hsl_to_rgb(h, s, l):  # hue in radians; s, l in [0, 1]. Rgb in [0, 255]
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 1.047) % 2 - 1))
    m = l - c / 2
    lookup = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)]
    r, g, b = [int((c + m) * 255) for c in lookup[int(h // 1.047)]]
    return (r, g, b)

def rgb_to_hsl(red, green, blue): # hue in radians, s, l in [0, 1]. Rgb in [0, 255]
    red /= 255
    green /= 255
    blue /= 255
    max_chroma = max(red, green, blue)
    min_chroma = min(red, green, blue)
    delta = max_chroma - min_chroma
    
    if delta == 0:
        hue = 0
    elif max_chroma == red:
        hue = ((green - blue) / delta) % 6
    elif max_chroma == green:
        hue = (blue - red) / delta + 2
    elif max_chroma == blue:
        hue = (red - green) / delta + 4
    
    hue *= (3.1415926 / 3)
    lightness = (max_chroma + min_chroma) / 2
    saturation = 0 if delta == 0 else delta / (1 - abs(2 * lightness - 1))

    return (hue, saturation, lightness)

def print_progress_bar(progress, total):
    bar_length = 32
    filled_length = int(bar_length * progress // total)
    bar = '·' * filled_length + '⏵' + ' ' * (bar_length - filled_length)  # ·
    print(f'[ {bar} ] {progress}/{total}', end='\r')

def integer_mix(percent: int, red: int, green: int, blue: int, other):
    r = int((1 - percent / 100) * red + (percent / 100) * other[0])
    g = int((1 - percent / 100) * green + (percent / 100) * other[1])
    b = int((1 - percent / 100) * blue + (percent / 100) * other[2])
    return (r, g, b)

# Composite 0.
# start with black, screen cym at 1/3 opacity
comp_0_screen = Image.new('RGB', original.size)
comp_0_pixels = comp_0_screen.load()

# Composite 1.
# start with white, subtract cym at 1/2 opacity
comp_1_screen = Image.new('RGB', original.size)
comp_1_pixels = comp_1_screen.load()

# Composite 2.
# blue = 1.0 - yellow, green = 1.0 - magenta, red = 1.0 - cyan
comp_2_screen = Image.new('RGB', original.size)
comp_2_pixels = comp_2_screen.load()

for x in range(original.width):
    for y in range(original.height):
        orig = orig_pix[x, y]
        c0, m0, y0 = cyan[x, y] / 255, magenta[x, y] / 255, yellow[x, y] / 255

        # composite 0
        r0 = 255 - int(255 * (1 - 0.5 * m0) * (1 - 0.5 * y0))
        g0 = 255 - int(255 * (1 - 0.5 * c0) * (1 - 0.5 * y0))
        b0 = 255 - int(255 * (1 - 0.5 * c0) * (1 - 0.5 * m0))
        h, s, _ = rgb_to_hsl(r0, g0, b0)
        l = float(luma[x, y]) / 255.0
        r1, g1, b1 = hsl_to_rgb(h, s, l)
        comp_0_pixels[x, y] = integer_mix(33, r1, g1, b1, orig)

        # composite 1
        c1, m1, y1 = c0, m0, 1.0 - y0
        r3 = int(255 - 0.5 * m1 * 255 - 0.5 * y1 * 255)
        g3 = int(255 - 0.5 * c1 * 255 - 0.5 * y1 * 255)
        b3 = int(255 - 0.5 * c1 * 255 - 0.5 * m1 * 255)
        # comp_1_pixels[x, y] = r3, g3, b3 # integer_mix(33, r4, g4, b4, orig)
        h, s, _ = rgb_to_hsl(r3, g3, b3)
        l = float(luma[x, y]) / 255.0
        r4, g4, b4 = hsl_to_rgb(h, s, l)
        comp_1_pixels[x, y] = integer_mix(50, r4, g4, b4, orig)

        r5 = 255 * int(1.0 - c0)
        g5 = 255 * int(1.0 - m0)
        b5 = 255 * int(1.0 - y0)
        h, s, _ = rgb_to_hsl(r5, g5, b5)
        l = float(luma[x, y]) / 255.0
        r6, g6, b6 = hsl_to_rgb(h, s, l)
        comp_2_pixels[x, y] = integer_mix(33, r6, g6, b6, orig)

    print_progress_bar(x + 1, original.width)

comp_0_screen.save('./2025/Mar.02/output/composite_0.png')
comp_1_screen.save('./2025/Mar.02/output/composite_1.png')
comp_2_screen.save('./2025/Mar.02/output/composite_2.png')