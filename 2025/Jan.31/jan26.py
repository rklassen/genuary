# Genuary 2025 - Jan.26
# Convert the image 
from PIL import Image
import numpy as np

# Rafael Leao https://unsplash.com/@raflfc
# https://unsplash.com/photos/man-and-woman-sitting-on-wooden-fence-near-brown-and-green-palm-tree-YqCB5Bd1TcI
image_path = '2025/Jan.31/rafael-leao.webp'
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
    total_rows = pixels.shape[0] - 1
    progress_bar_length = 32

    for y in range(total_rows):
        for x in range(pixels.shape[1] - 1):
            diff_down = abs(int(pixels[y, x]) - int(pixels[y + 1, x]))
            diff_right = abs(int(pixels[y, x]) - int(pixels[y, x + 1]))
            edge_value = 255 - EDGE_SCALAR * (diff_down + diff_right)
            edge_value = 0 if edge_value < EDGE_THRESHOLD else 255
            edges[y, x] = np.clip(edge_value, 0, 255)

        # Print progress bar for y
        progress = (y + 1) / total_rows
        num_dots = int(progress * progress_bar_length)
        progress_bar = '[' + '.' * num_dots + ' ' * (progress_bar_length - num_dots) + ']'
        print(f'\r{progress_bar}', end='')

    print()  # Move to the next line after the progress bar is complete

    edges_image = Image.fromarray(edges, 'L')
    edges_path = f'2025/Jan.31/edges_{component}.webp'
    edges_image.save(edges_path, 'WEBP', quality=50)
    print(f'Saved edges {component} image as {edges_path}')

    sorted_pixels = np.array(components[component])
    total_columns = edges.shape[1]
    progress_bar_length = 32

    for x in range(total_columns):
        start_idx = None
        for y in range(edges.shape[0]):
            if edges[y, x] == 255:
                if start_idx is None:
                    start_idx = y
            else:
                if start_idx is not None:
                    end_idx = y
                    sorted_pixels[start_idx:end_idx, x] = np.sort(sorted_pixels[start_idx:end_idx, x])
                    start_idx = None
        if start_idx is not None:
            sorted_pixels[start_idx:, x] = np.sort(sorted_pixels[start_idx:, x])

        # Print progress bar
        progress = (x + 1) / total_columns
        num_dots = int(progress * progress_bar_length)
        progress_bar = '[' + '.' * num_dots + ' ' * (progress_bar_length - num_dots) + ']'
        print(f'\r{progress_bar}', end='')

    print()  # Move to the next line after the progress bar is complete

    sorted_component_pixels = np.zeros((cmyk_image.size[1], cmyk_image.size[0], 3), dtype=np.uint8)
    normalized_sorted = sorted_pixels / 255.0
    for i in range(3):
        sorted_component_pixels[..., i] = (1 - normalized_sorted) * 255 + normalized_sorted * color[i] * 255

    sorted_component_image = Image.fromarray(sorted_component_pixels, 'RGB')
    sorted_component_path = f'2025/Jan.31/sorted_{component}.webp'
    sorted_component_image.save(sorted_component_path, 'WEBP', quality=50)
    print(f'Saved sorted {component} component image as {sorted_component_path}')

# Combine the sorted component images by multiplying the colors together
sorted_c = Image.open('2025/Jan.31/sorted_c.webp')
sorted_m = Image.open('2025/Jan.31/sorted_m.webp')
sorted_y = Image.open('2025/Jan.31/sorted_y.webp')

sorted_c_pixels = np.array(sorted_c) / 255.0
sorted_m_pixels = np.array(sorted_m) / 255.0
sorted_y_pixels = np.array(sorted_y) / 255.0

combined_pixels = sorted_c_pixels * sorted_m_pixels * sorted_y_pixels
combined_image = Image.fromarray((combined_pixels * 255).astype(np.uint8), 'RGB')
combined_image_path = '2025/Jan.31/2025jan31.webp'
combined_image.save(combined_image_path, 'WEBP', quality=90)
print(f'Saved combined image as {combined_image_path}')