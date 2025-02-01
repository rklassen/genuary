# Genuary 2025 - Jan.26
# Convert the image 
from PIL import Image
import numpy as np

# load the image, convert to cymk, and split the image into components.
image_path = '2025/Jan.31/galaxy egg.webp'
image = Image.open(image_path)
cmyk_image = image.convert('CMYK')
c, m, y, k = cmyk_image.split()
components = {'c': c, 'm': m, 'y': y}  # map images to keys via dictionary
components_colors = {
    'c': (0, 1, 1),  # Cyan: Red channel
    'm': (1, 0, 1),  # Magenta: Green channel
    'y': (1, 1, 0),  # Yellow: Blue channel
}   

EDGE_SCALAR = 4
EDGE_THRESHOLD = 170
for component, color in components_colors.items():
    pixels = np.array(components[component])
    normalized = pixels / 255.0
    component_pixels = np.zeros((cmyk_image.size[1], cmyk_image.size[0], 3), dtype=np.uint8)
    for i in range(3):
        component_pixels[..., i] = (1 - normalized) * 255 + normalized * color[i] * 255

    component_image = Image.fromarray(component_pixels, 'RGB')
    component_path = f'2025/Jan.31/jan31_{component}.webp'
    component_image.save(component_path, 'WEBP', quality=50)
    print(f'Saved {component} component image as {component_path}')

    edges = np.zeros_like(pixels, dtype=np.uint8)
    for y in range(pixels.shape[0] - 1):
        for x in range(pixels.shape[1] - 1):
            diff_down = abs(int(pixels[y, x]) - int(pixels[y + 1, x]))
            diff_right = abs(int(pixels[y, x]) - int(pixels[y, x + 1]))
            edge_value = 255 - EDGE_SCALAR * (diff_down + diff_right)
            edge_value = 0 if edge_value < EDGE_THRESHOLD else 255
            edges[y, x] = np.clip(edge_value, 0, 255)

    edges_image = Image.fromarray(edges, 'L')
    edges_path = f'2025/Jan.31/edges_{component}.webp'
    edges_image.save(edges_path, 'WEBP', quality=50)
    print(f'Saved edges {component} image as {edges_path}')