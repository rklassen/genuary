import numpy as np
from mpl_toolkits.mplot3d import Axes3D
def plot_quantization_surface(quant_levels, title, filename, chroma=True):
    x = np.arange(len(quant_levels[0]))
    y = np.arange(len(quant_levels))
    x, y = np.meshgrid(x, y)
    z = np.array(quant_levels)

    fig = plt.figure(figsize=(12.8, 7.2))
    ax = fig.add_subplot(111, projection='3d')
    label_size = 20

    ax.set_title(title, color='#6dead6', fontsize=int(1.75*float(label_size)))
    ax.set_xlabel('s (frequency)', color='#6dead6', fontsize=label_size)
    ax.set_ylabel('t (frequency)', color='#6dead6', fontsize=label_size)
    ax.set_zlabel('Quantization Level', color='#6dead6', fontsize=label_size)
    surface = ax.plot_surface(y, -x, z, cmap='viridis', edgecolor='k', linewidth=0.2, shade=True)

    # Add contour lines to the z-axis
    ax.contour(y, -x, z, zdir='z', offset=z.min(), cmap='viridis', linestyles="solid")

    # Add labels per line in the z dimension with spacing
    z_ticks = np.linspace(z.min(), z.max(), len(quant_levels))
    ax.set_zticks(z_ticks)
    ax.set_zticklabels([f"{tick:.1f}" for tick in z_ticks], fontsize=int(label_size / 1.75), color='#6dead6', verticalalignment='center_baseline')

    # Adjust minor line labels to charcoal
    for line in ax.zaxis.get_ticklines(minor=True):
        line.set_color('charcoal')

    # cube backdrop
    ax.xaxis.set_pane_color((0, 0, 0, 1))
    ax.yaxis.set_pane_color((0, 0, 0, 1))
    ax.zaxis.set_pane_color((0, 0, 0, 1))
    ax.grid(color='gray', linestyle='--', linewidth=0.5)

    # Set dark mode background
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    plt.savefig(filename, format='webp', facecolor=fig.get_facecolor())
    plt.close()


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

    # Rotate the luma chart 90 degrees clockwise
    plot_quantization_surface(luminance_levels, "Number of Luma Quantization Levels", "./2025/Apr.01/luma.webp")
    plot_quantization_surface(chrominance_levels, "Number of Chroma Quantization Levels", "./2025/Apr.01/chroma.webp")