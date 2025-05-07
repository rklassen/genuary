from PIL import Image
import random
from PIL import ImageDraw, ImageFilter, ImageChops
import math

width, height = 512, 512
image = Image.new('L', (width, height))

for y in range(height):
    t = y / height
    intensity = int(25.5 + (51 * (t ** 3)))
    
    for x in range(width):
        noise_strength = max(0, (76.5 - intensity) / 76.5 * 2.5)
        noise = random.uniform(-noise_strength, noise_strength)
        noisy_intensity = max(0, min(255, intensity + noise))
        image.putpixel((x, y), int(noisy_intensity))

image.save('gradient_cubic_falloff.png')

# Define the triangle parameters
image_center = (width // 2, height // 2)
image_radius = min(width, height) // 2
triangle_radius = int(0.65 * image_radius * 0.75)  # 25% smaller
eccentricity = 0.1  # 10% eccentricity from equilateral
triangle_color = (255, 255, 255)  # White color for the triangle

# Calculate the vertices of the triangle
vertices = []
for i in range(3):
    angle = 2 * math.pi * i / 3  # Equilateral triangle angles
    if i == 1:  # Apply eccentricity to one vertex
        angle += eccentricity
    x = image_center[0] + triangle_radius * math.cos(angle)
    y = image_center[1] + triangle_radius * math.sin(angle)
    vertices.append((x, y))

# Create a new image for the triangle
triangle_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(triangle_image)
draw.polygon(vertices, fill=triangle_color)

# Create a bloom effect
bloom_image = triangle_image.copy()
bloom_image = bloom_image.filter(ImageFilter.GaussianBlur(radius=10))
bloom_image = ImageChops.multiply(bloom_image, bloom_image)  # Intensify the bloom

# Convert background to RGB
image = image.convert('RGB')

# Composite the bloom and triangle onto the background
image.paste(bloom_image, (0, 0), bloom_image)
image.paste(triangle_image, (0, 0), triangle_image)

image.save('gradient_cubic_falloff_with_triangle.png')