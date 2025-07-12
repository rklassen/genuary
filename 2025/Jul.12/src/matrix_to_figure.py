import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.colors import LinearSegmentedColormap
from typing import List
from matplotlib.figure import Figure


def set_font_as_gloal_state_change(
    font_path: str
) -> None:
    '''
    Set the font globally for matplotlib plots
    '''
    try:
        if os.path.exists(font_path):
            from matplotlib.font_manager import FontProperties
            prop = FontProperties(fname=font_path)
            plt.rcParams['font.family'] = prop.get_name()
            print(f"Successfully loaded Public Sans Regular from: {font_path}")
        else:
            plt.rcParams['font.family'] = 'sans-serif'
    except Exception as e:
        plt.rcParams['font.family'] = 'sans-serif'


def matrix_to_figure(
        attention_matrix: np.ndarray,
        layer_num: int,
        head_num: int,
        tokens: List[str],
        total_weight: float,
        inverted_cmap: LinearSegmentedColormap,
        text_color: str,
        accent_color: str,
    ) -> Figure:
    '''
    Create an attention visualization chart for PDF inclusion
    '''

    # Create the visualization
    fig, ax = plt.subplots(figsize=(14, 12))

    # Create heatmap with inverted colormap and new range
    im = ax.imshow(
        attention_matrix,
        cmap=inverted_cmap,
        aspect='auto',
        vmin=0,
        vmax=0.4
    )

    # Set ticks and labels
    ax.set_xticks(range(len(tokens)))
    ax.set_yticks(range(len(tokens)))

    # Clean up token display
    display_tokens = [
        token.replace('[CLS]', 'CLS').replace('[SEP]', 'SEP')
        for token in tokens
    ]
    golden_ratio = 1.618
    token_fontsize = int(10 * golden_ratio**2)  # Golden ratio squared: ~26
    ax.set_xticklabels(
        display_tokens,
        rotation=45,
        ha='right',
        fontsize=token_fontsize
    )
    ax.set_yticklabels(display_tokens, fontsize=token_fontsize)

    # Add subtle grid
    ax.set_xticks(np.arange(-0.5, len(tokens), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(tokens), 1), minor=True)
    ax.grid(
        which="minor",
        color="black",
        linestyle='-',
        linewidth=0.8
    )

    # Add colorbar without label
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=30)
    colorbar_fontsize = int(10 * golden_ratio)  # Golden ratio: ~16
    colorbar_ticks = [0.0, 0.1, 0.2, 0.3, 0.4]
    colorbar_labels = [f"{tick:.1f}" for tick in colorbar_ticks]
    cbar.set_ticks(colorbar_ticks)
    cbar.set_ticklabels(colorbar_labels)
    cbar.ax.tick_params(
        labelsize=colorbar_fontsize,
        colors=text_color
    )

    # Add value annotations for high attention weights
    for i in range(len(tokens)):
        for j in range(len(tokens)):
            if attention_matrix[i, j] > 0.15:
                cell_value_label_color = (
                    'black' if attention_matrix[i, j] > 0.25 else 'white'
                )
                ax.text(
                    j,
                    i,
                    f'{attention_matrix[i, j]:.3f}',
                    ha="center",
                    va="center",
                    color=cell_value_label_color,
                    fontsize=8,
                    fontweight='500'
                )

    # Add title with search context
    plt.figtext(
        x=0.5,
        y=0.95,
        s=f'Layer {layer_num} Head {head_num} - Augusta/National/It/Is Attention',
        ha='center',
        fontsize=18,
        color=text_color,
        fontweight='600'
    )

    # Add subtitle with total weight
    plt.figtext(
        x=0.5,
        y=0.91,
        s=f'Total Target Edge Weight: {total_weight:.6f}',
        ha='center',
        fontsize=14,
        color=accent_color,
    )

    plt.tight_layout()
    plt.subplots_adjust(top=0.82)

    return fig