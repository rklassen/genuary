from math import pi, sin, cos, sqrt
import os
from PIL import Image

# very approximate sinusoidal representation
def simulated_ekg(period: float):
    t = pi * 2.0 * period
    phase = 3.0 * cos ( t )
    r_wave = -sin ( t + phase )
    q_scalar = 0.50 - 0.75 * sin ( t - 1.0 )
    s_scalar = 0.25 - 0.125 * sin ( 1.25 * phase - 1.0 )
    return 3.14 * q_scalar * r_wave * s_scalar

# generate greyscale frames from the ekg of normalized t + u - v
os.makedirs('.frames', exist_ok=True)
for i in range(99):
    img = Image.new('RGB', (1080, 1080))
    pixels = img.load()
    for x in range(1080):
        for y in range(1080):
            period = float(i) / 100.0 + float(x - y) / 1079.0 / sqrt(2.0)
            ekg = 0.5 + 0.5 * simulated_ekg(period)
            color = int(254 * max(0.0, min(1.0, ekg)))
            pixels[x, y] = (color, color, color)
    filename = f'.frames/grey_{i:03d}.png'
    img.save(filename)
    print(f'Generated {filename}')