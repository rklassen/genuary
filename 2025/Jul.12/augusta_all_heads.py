import torch
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os
import csv

COLOR_LOW = '#121212'  # Charcoal
COLOR_ACCENT = '#FFDD00'  # Yellow accent
COLOR_TOP = '#FFFFFF' 

# Set up the sentence and model
sentence = "Augusta National is a golf course I won't ever play, but it is a bucket list item"
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, output_attentions=True, attn_implementation="eager")
inputs = tokenizer(sentence, return_tensors="pt", add_special_tokens=True)
tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

# Get model outputs with attention
with torch.no_grad():
    outputs = model(**inputs)
    attentions = outputs.attentions

# Remove SEP token from tokens list for all visualizations
original_tokens = tokens.copy()
sep_index = len(tokens) - 1
if tokens[sep_index] == '[SEP]':
    tokens = tokens[:-1]
    print(f"Removed SEP token. Filtered tokens: {tokens}")

# Create heads_png subfolder
heads_dir = "/Users/richardklassen/Developer/genuary/2025/Jul.12/heads_png"
os.makedirs(heads_dir, exist_ok=True)

# Set up matplotlib with Public Sans Regular from local file
try:
    font_path = "./PublicSans-Regular.ttf"
    if os.path.exists(font_path):
        from matplotlib.font_manager import FontProperties
        prop = FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
        print(f"Successfully loaded Public Sans Regular from: {font_path}")
    else:
        print(f"Font file not found at: {font_path}")
        preferred_fonts = ['Arial', 'Helvetica', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        for font in preferred_fonts:
            if font in available_fonts or font == 'sans-serif':
                plt.rcParams['font.family'] = font
                print(f"Using fallback font: {font}")
                break
except Exception as e:
    print(f"Font setup error: {e}, using system default")
    plt.rcParams['font.family'] = 'sans-serif'

# Function to invert RGB color
def invert_color(color):
    """Invert RGB values: (r,g,b) -> (1-r, 1-g, 1-b)"""
    if isinstance(color, str):
        if color.startswith('#'):
            hex_color = color[1:]
            rgb = tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
            inverted_rgb = tuple(1.0 - c for c in rgb)
            return "#{:02x}{:02x}{:02x}".format(
                int(inverted_rgb[0] * 255),
                int(inverted_rgb[1] * 255),
                int(inverted_rgb[2] * 255)
            )
    elif isinstance(color, (tuple, list)):
        if len(color) >= 3:
            return tuple(1.0 - c for c in color[:3]) + (color[3:] if len(color) > 3 else ())
    return color

# Create inverted colormap
color_positions = [0.0, 0.5, 1.0]
inverted_colors = [COLOR_LOW, COLOR_ACCENT, COLOR_TOP]
inverted_cmap = LinearSegmentedColormap.from_list('InvertedBlues', 
                                                 list(zip(color_positions, inverted_colors)), N=256)

# Configure matplotlib for inverted appearance
inverted_edge_color = invert_color('#2E2E2E')
inverted_text_color = invert_color('#2E2E2E')
inverted_bg_color = COLOR_LOW

plt.rcParams.update({
    'font.size': 11,
    'axes.linewidth': 1.2,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.bottom': True,
    'axes.spines.left': True,
    'axes.edgecolor': inverted_edge_color,
    'axes.labelcolor': inverted_text_color,
    'text.color': inverted_text_color,
    'xtick.color': inverted_text_color,
    'ytick.color': inverted_text_color,
    'figure.facecolor': inverted_bg_color,
    'axes.facecolor': inverted_bg_color
})

def save_attention_csv(attention_matrix, tokens, output_path):
    """Save attention matrix as CSV with tokens as column headers"""
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row with tokens as column labels
        writer.writerow(tokens)
        
        # Write data rows (numerical values only, no row labels)
        for row in attention_matrix:
            writer.writerow(row.tolist())

def create_attention_chart(attention_matrix, layer_num, head_num, tokens, output_path):
    """Create an attention visualization chart for a specific head"""
    
    # Create the visualization
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Create heatmap with inverted colormap and new range
    im = ax.imshow(attention_matrix, cmap=inverted_cmap, aspect='auto', vmin=0, vmax=0.4)
    
    # Set ticks and labels
    ax.set_xticks(range(len(tokens)))
    ax.set_yticks(range(len(tokens)))
    
    # Clean up token display
    display_tokens = [token.replace('[CLS]', 'CLS').replace('[SEP]', 'SEP') for token in tokens]
    golden_ratio = 1.618
    token_fontsize = int(10 * golden_ratio**2)  # Golden ratio squared: ~26
    ax.set_xticklabels(display_tokens, rotation=45, ha='right', fontsize=token_fontsize)
    ax.set_yticklabels(display_tokens, fontsize=token_fontsize)
    
    # Add subtle grid
    ax.set_xticks(np.arange(-0.5, len(tokens), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(tokens), 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=0.8)
    
    # Add colorbar without label
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=30)
    colorbar_fontsize = int(10 * golden_ratio)  # Golden ratio: ~16
    # Set custom ticks at 0.1 increments with one decimal place
    colorbar_ticks = [0.0, 0.1, 0.2, 0.3, 0.4]
    colorbar_labels = [f"{tick:.1f}" for tick in colorbar_ticks]
    cbar.set_ticks(colorbar_ticks)
    cbar.set_ticklabels(colorbar_labels)
    cbar.ax.tick_params(labelsize=colorbar_fontsize, colors=inverted_text_color)
    
    # Add value annotations for high attention weights
    for i in range(len(tokens)):
        for j in range(len(tokens)):
            if attention_matrix[i, j] > 0.15:
                text_color = 'black' if attention_matrix[i, j] > 0.25 else 'white'
                ax.text(j, i, f'{attention_matrix[i, j]:.3f}',
                       ha="center", va="center", color=text_color,
                       fontsize=8, fontweight='500')
    
    # Add title
    plt.figtext(
        x=0.5,
        y=0.915,
        s=f'Attention Layer {layer_num} Head {head_num}',
        ha='center',
        fontsize=20,
        color=inverted_text_color
    )
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.84)
    
    # Save the chart
    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches='tight',
        facecolor=inverted_bg_color,
        edgecolor='none',
    )
    plt.close()

# Generate charts for all heads
print(f"Generating charts for all {len(attentions)} layers with {attentions[0].shape[1]} heads each...")
print(f"Total charts to generate: {len(attentions) * attentions[0].shape[1]}")

total_charts = 0
for layer_idx in range(len(attentions)):
    layer_attention = attentions[layer_idx][0]  # Get first (and only) batch
    num_heads = layer_attention.shape[0]
    
    print(f"\nProcessing Layer {layer_idx + 1}...")
    
    for head_idx in range(num_heads):
        # Get attention matrix for this head
        attention_matrix = layer_attention[head_idx].numpy()
        
        # Remove SEP token row and column
        if len(original_tokens) > len(tokens):  # SEP was removed
            attention_matrix = attention_matrix[:-1, :-1]
        
        # Create output filenames
        png_filename = f"layer_{layer_idx+1:02d}_head_{head_idx+1:02d}.png"
        csv_filename = f"layer_{layer_idx+1:02d}_head_{head_idx+1:02d}.csv"
        png_path = os.path.join(heads_dir, png_filename)
        csv_path = os.path.join(heads_dir, csv_filename)
        
        # Create the chart and save CSV
        create_attention_chart(attention_matrix, layer_idx + 1, head_idx + 1, tokens, png_path)
        save_attention_csv(attention_matrix, tokens, csv_path)
        
        total_charts += 1
        if total_charts % 12 == 0:  # Progress update every layer
            print(f"  Generated {total_charts} charts...")

print(f"\n🏌️  Generated {total_charts} attention head visualizations! 🏌️")
print(f"PNGs and CSVs saved to: {heads_dir}")
print(f"{'='*60}")
