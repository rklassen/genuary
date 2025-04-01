import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Quantization tables for JPEG encoding
# These are standard quantization tables used in JPEG compression.

# Luminance quantization table
LUMINANCE_QUANT_TABLE = [
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99],
]

# Chrominance quantization table
CHROMINANCE_QUANT_TABLE = [
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
]

# Print the tables for verification
if __name__ == "__main__":
    print("Luminance Quantization Table:")
    for row in LUMINANCE_QUANT_TABLE:
        print(row)

    print("\nChrominance Quantization Table:")
    for row in CHROMINANCE_QUANT_TABLE:
        print(row)

    def quantization_levels(quant_table):
        return [[round(256.0 / value, 1) if value != 0 else 0 for value in row] for row in quant_table]

    luminance_levels = quantization_levels(LUMINANCE_QUANT_TABLE)
    chrominance_levels = quantization_levels(CHROMINANCE_QUANT_TABLE)

    print("\nLuminance Quantization Levels:")
    for row in luminance_levels:
        print(" ".join(f"{value:5.1f}" for value in row))

    print("\nChrominance Quantization Levels:")
    for row in chrominance_levels:
        print(" ".join(f"{value:5.1f}" for value in row))

    import matplotlib.pyplot as plt

    def plot_quantization_surface(quant_levels, title, filename, chroma=True):
        x = np.arange(len(quant_levels[0]))
        y = np.arange(len(quant_levels))
        x, y = np.meshgrid(x, y)
        z = np.array(quant_levels)

        fig = plt.figure(figsize=(12.8, 7.2))
        ax = fig.add_subplot(111, projection='3d')
        if chroma:
            ax.set_title("Chrominance Quantization Surface", color='white')
            ax.set_xlabel('X (Chroma)', color='white')
            ax.set_ylabel('Y', color='white')
            ax.set_zlabel('Quantization Level', color='white')
            ax.plot_surface(y, -x, z, cmap='viridis', edgecolor='k')
        else:
            ax.set_title("Luminance Quantization Surface", color='white')
            ax.set_xlabel('X (Luma)', color='white')
            ax.set_ylabel('Y', color='white')
            ax.set_zlabel('Quantization Level', color='white')
            ax.plot_surface(y, -x, z, cmap='viridis', edgecolor='k')

        # Set dark mode background
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        plt.savefig(filename, format='webp', facecolor=fig.get_facecolor())
        plt.close()

    # Rotate the luma chart 90 degrees clockwise
    plot_quantization_surface(luminance_levels, "x Quantization Surface", "./2025/Apr.01/luma.webp")
    plot_quantization_surface(chrominance_levels, "Chrominance Quantization Surface", "./2025/Apr.01/chroma.webp")