import torch
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

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

# Extract attention for layer 6, head 1 (0-indexed, so layer 5, head 0)
layer_idx = 5  # Layer 6 (0-indexed)
head_idx = 0   # Head 1 (0-indexed)

attention_matrix = attentions[layer_idx][0, head_idx].numpy()
print(f"Attention matrix shape: {attention_matrix.shape}")

# Remove SEP token (last token) from visualization
sep_index = len(tokens) - 1  # SEP is typically the last token
if tokens[sep_index] == '[SEP]':
    # Remove SEP from tokens list
    tokens = tokens[:-1]
    # Remove SEP row and column from attention matrix
    attention_matrix = attention_matrix[:-1, :-1]
    print(f"Removed SEP token. New shape: {attention_matrix.shape}")
    print(f"Filtered tokens: {tokens}")

# Set up matplotlib with Public Sans Regular from local file
try:
    # Use specific Public Sans Regular font file
    font_path = "./PublicSans-Regular.ttf"
    import os
    if os.path.exists(font_path):
        from matplotlib.font_manager import FontProperties
        prop = FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
        print(f"Successfully loaded Public Sans Regular from: {font_path}")
    else:
        print(f"Font file not found at: {font_path}")
        # Fallback to system fonts
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
        # Convert hex to RGB, invert, then back to hex
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

# Create inverted colormap with new positioning
# COLOR_LOW at 0.0, COLOR_ACCENT at 0.2, COLOR_TOP at 0.4
color_positions = [0.0, 0.5, 1.0]  # Maps to 0.0, 0.2, 0.4 in the 0-0.4 range
inverted_colors = [COLOR_LOW, COLOR_ACCENT, COLOR_TOP]
inverted_cmap = LinearSegmentedColormap.from_list('InvertedBlues', 
                                                 list(zip(color_positions, inverted_colors)), N=256)

# Configure matplotlib for inverted appearance
inverted_edge_color = invert_color('#2E2E2E')  # Light gray
inverted_text_color = invert_color('#2E2E2E')   # Light gray
inverted_bg_color = COLOR_LOW  # Charcoal (10% white)
inverted_title_color = invert_color('#1a1a1a')  # Light gray
inverted_subtitle_color = invert_color('#4a4a4a') # Medium gray

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

# Create the inverted visualization
fig, ax = plt.subplots(figsize=(14, 12))

# Create heatmap with inverted colormap and new range
im = ax.imshow(attention_matrix, cmap=inverted_cmap, aspect='auto', vmin=0, vmax=0.4)

# Set ticks and labels
ax.set_xticks(range(len(tokens)))
ax.set_yticks(range(len(tokens)))

# Clean up token display (remove special tokens brackets for readability)
display_tokens = [token.replace('[CLS]', 'CLS').replace('[SEP]', 'SEP') for token in tokens]
golden_ratio = 1.618
token_fontsize = int(10 * golden_ratio**2)  # Golden ratio squared: ~26
ax.set_xticklabels(display_tokens, rotation=45, ha='right', fontsize=token_fontsize)
ax.set_yticklabels(display_tokens, fontsize=token_fontsize)

# Add subtle grid with inverted color (black instead of white)
ax.set_xticks(np.arange(-0.5, len(tokens), 1), minor=True)
ax.set_yticks(np.arange(-0.5, len(tokens), 1), minor=True)
ax.grid(which="minor", color="black", linestyle='-', linewidth=0.8)

# Add colorbar without label
cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=30)
colorbar_fontsize = int(10 * golden_ratio)  # Scale colorbar ticks by golden ratio: ~16
# Set custom ticks at 0.1 increments with one decimal place
colorbar_ticks = [0.0, 0.1, 0.2, 0.3, 0.4]
colorbar_labels = [f"{tick:.1f}" for tick in colorbar_ticks]
cbar.set_ticks(colorbar_ticks)
cbar.set_ticklabels(colorbar_labels)
cbar.ax.tick_params(labelsize=colorbar_fontsize, colors=inverted_text_color)

# Add value annotations for high attention weights with inverted colors
for i in range(len(tokens)):
    for j in range(len(tokens)):
        if attention_matrix[i, j] > 0.15:  # Adjusted threshold for new range
            # Invert the text color logic: black text on light background, white on dark
            text_color = 'black' if attention_matrix[i, j] > 0.25 else 'white'
            ax.text(j, i, f'{attention_matrix[i, j]:.3f}',
                   ha="center", va="center", color=text_color,
                   fontsize=8, fontweight='500')


###############################////////////////////////////////////////////////
# TITLE
###############################////////////////////////////////////////////////

plt.figtext(
    x = 0.5,
    y = 0.915,  # Moved down by ~0.5 line height (from 0.94)
    s = 'Attention Layer 6 Head 1',
    ha = 'center',
    fontsize = 20,
    color = inverted_text_color
)


plt.tight_layout()
plt.subplots_adjust(top=0.84)  # Reduced from 0.88 to make room for text


###############################////////////////////////////////////////////////
# SAVE
###############################////////////////////////////////////////////////

output_path = "/Users/richardklassen/Developer/genuary/2025/Jul.12/augusta.png"
plt.savefig(
    output_path,
    dpi=300,
    bbox_inches='tight',
    facecolor=inverted_bg_color,
    edgecolor='none',
)

pdf_output_path = "/Users/richardklassen/Developer/genuary/2025/Jul.12/augusta.pdf"
plt.savefig(
    pdf_output_path,
    bbox_inches='tight',
    facecolor=inverted_bg_color,
    edgecolor='none',
)
print(f"Saved attention visualizations {output_path} annd {pdf_output_path}")
plt.close()

# Analyze attention patterns
print(f"\nKey Attention Patterns:")


###############################////////////////////////////////////////////////
# SAVE
###############################////////////////////////////////////////////////

# Find strongest connections
strong_threshold = 0.5
strong_connections = np.where(attention_matrix > strong_threshold)
print(f"  Strong connections (>{strong_threshold}):")
for i, j in zip(strong_connections[0], strong_connections[1]):
    print(f"    '{tokens[i]}' → '{tokens[j]}': {attention_matrix[i, j]:.4f}")

# Self-attention analysis
self_attention = np.diag(attention_matrix)
high_self_attention = np.where(self_attention > 0.3)[0]
print(f"\n  High self-attention tokens (>0.3):")
for idx in high_self_attention:
    print(f"    '{tokens[idx]}': {self_attention[idx]:.4f}")

# Find tokens that receive most attention
incoming_attention = np.sum(attention_matrix, axis=0)
top_receivers = np.argsort(incoming_attention)[-5:][::-1]
print(f"\n  Top attention receivers:")
for i, idx in enumerate(top_receivers):
    print(f"    {i+1}. '{tokens[idx]}': {incoming_attention[idx]:.4f} total")

print(f"\n🏌️  Augusta National themed visualization complete! 🏌️")
print(f"{'='*60}")
