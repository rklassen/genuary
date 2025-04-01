import numpy
from matplotlib import pyplot

def plot_quantization_surface(quant_levels, title, filename, fontname='General Sans'):
    
    x = numpy.arange(len(quant_levels[0]))
    y = numpy.arange(len(quant_levels))
    x, y = numpy.meshgrid(x, y)
    z = numpy.array(quant_levels)

    fig = pyplot.figure(figsize=(10.0, 10.0))
    ax = fig.add_subplot(111, projection='3d', proj_type='persp')
    ax.dist = 7  # Decrease the distance to increase perspective effect
    label_size = 20

    # Check if the specified font exists, otherwise use a fallback
    available_fonts = ['Aptos', 'Roboto', 'Meno', 'Consolas', 'Liberation Sans']
    if fontname not in pyplot.rcParams['font.family']:
        for fallback_font in available_fonts:
            if fallback_font in pyplot.rcParams['font.family']:
                fontname = fallback_font
                break

    ax.set_title(title, color='#6dead6', fontsize=int(1.75*float(label_size)), fontname=fontname)
    ax.set_xlabel('s (frequency)', color='#6dead6', fontsize=label_size, fontname=fontname)
    ax.set_ylabel('t (frequency)', color='#6dead6', fontsize=label_size, fontname=fontname)
    ax.set_zlabel('Quantization Level', color='#6dead6', fontsize=label_size, fontname=fontname)
    # surface = ax.plot_surface(y, -x, z, cmap='viridis', edgecolor='k', linewidth=0.2, shade=True)

    # Add contour lines to the z-axis
    max_value = max(max(row) for row in quant_levels)
    _ = ax.contour3D(y, -x, z, levels=int(max_value), cmap='viridis', linestyles="solid")
    # Add a 3D bar chart to visualize the quantization levels
    for i in range(len(quant_levels)):
        for j in range(len(quant_levels[i])):
            ax.bar3d(y[i, j], -x[i, j], 0, 0.5, 0.5, z[i, j], shade=True, color=pyplot.cm.viridis(z[i, j] / z.max()))

    # Add labels per line in the z dimension with spacing
    z_ticks = numpy.linspace(z.min(), z.max(), len(quant_levels))
    ax.set_zticks(z_ticks)
    ax.set_zticklabels([f"{tick:.1f}" for tick in z_ticks], fontsize=int(label_size / 1.75), color='#6dead6', fontname=fontname, verticalalignment='center_baseline')

    # Adjust gridline colors
    grid_color = '#555555'
    ax.xaxis._axinfo['grid'].update({'color': grid_color})
    ax.yaxis._axinfo['grid'].update({'color': grid_color})
    ax.zaxis._axinfo['grid'].update({'color': grid_color})

    # cube backdrop
    ax.xaxis.set_pane_color((0, 0, 0, 1))
    ax.yaxis.set_pane_color((0, 0, 0, 1))
    ax.zaxis.set_pane_color((0, 0, 0, 1))
    ax.grid(color='gray', linestyle='--', linewidth=0.5)

    # Set dark mode background
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    pyplot.savefig(filename, format='webp', facecolor=fig.get_facecolor())
    pyplot.close()


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

    # Rotate the luma chart 90 degrees clockwise
    plot_quantization_surface(luminance_levels, "Number of Luma Quantization Levels", "./2025/Apr.01/luma.webp")
    plot_quantization_surface(chrominance_levels, "Number of Chroma Quantization Levels", "./2025/Apr.01/chroma.webp")