import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages
import os

# Color scheme and visualization setup
COLOR_LOW = '#121212'  # Charcoal
COLOR_ACCENT = '#FFDD00'  # Yellow accent
COLOR_TOP = '#FFFFFF'
coronograph = -2.0 # selector for values along the identity diagonal
how_many_pages_in_the_pdf = 24

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

def create_attention_chart_for_pdf(attention_matrix, layer_num, head_num, tokens, total_weight, edge_details):
    """Create an attention visualization chart for PDF inclusion"""
    
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
    
    # Add title with search context
    plt.figtext(
        x=0.5,
        y=0.95,
        s=f'Layer {layer_num} Head {head_num} - Augusta/National/It/Is Attention',
        ha='center',
        fontsize=18,
        color=inverted_text_color,
        fontweight='600'
    )
    
    # Add subtitle with total weight
    plt.figtext(
        x=0.5,
        y=0.91,
        s=f'Total Target Edge Weight: {total_weight:.6f}',
        ha='center',
        fontsize=14,
        color=COLOR_ACCENT
    )
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.82)
    
    return fig



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

print(f"Original tokens: {tokens}")

# Find the specific token indices
target_tokens = ['augusta', 'national', 'it']

# Find the second appearance of 'is'
is_indices = [i for i, token in enumerate(tokens) if token == 'is']
print(f"Found 'is' at indices: {is_indices}")

if len(is_indices) < 2:
    print("Error: Could not find second appearance of 'is'")
    exit(1)

second_is_index = is_indices[1]  # Second appearance
print(f"Second 'is' is at index: {second_is_index}")

# Find indices for target tokens
token_indices = {}
for target in target_tokens:
    try:
        idx = tokens.index(target)
        token_indices[target] = idx
        print(f"Found '{target}' at index: {idx}")
    except ValueError:
        print(f"Error: Could not find token '{target}' in sentence")
        exit(1)

# Add the second 'is' to our target set
token_indices['is_second'] = second_is_index
all_target_indices = list(token_indices.values())

print(f"\nTarget token indices: {token_indices}")
print(f"All target indices: {all_target_indices}")

def calculate_edge_weights(attention_matrix, indices):
    """Calculate maximum attention weight between all pairs of target indices"""
    max_weight = float('-inf')
    edge_details = []
    
    # Calculate weights for all possible edges between target tokens
    for i, idx_i in enumerate(indices):
        for j, idx_j in enumerate(indices):
            weight = attention_matrix[idx_i, idx_j]
            
            # Apply coronograph to identity diagonal (self-attention)
            if i == j:  # Identity diagonal
                weight *= coronograph
            
            # Track maximum weight
            max_weight = max(max_weight, weight)
            edge_details.append((idx_i, idx_j, weight))
    
    return max_weight, edge_details

# Analyze all heads
head_scores = []

print(f"\n{'='*80}")
print("ANALYZING ATTENTION WEIGHTS BETWEEN TARGET TOKENS")
print(f"{'='*80}")

for layer_idx in range(len(attentions)):
    layer_attention = attentions[layer_idx][0]  # Get first (and only) batch
    
    for head_idx in range(layer_attention.shape[0]):
        attention_matrix = layer_attention[head_idx].numpy()
        
        # Calculate maximum edge weight for this head
        max_weight, edge_details = calculate_edge_weights(attention_matrix, all_target_indices)
        
        head_scores.append({
            'layer': layer_idx + 1,
            'head': head_idx + 1,
            'max_weight': max_weight,
            'edge_details': edge_details
        })

# Sort heads by maximum weight (descending)
head_scores.sort(key=lambda x: x['max_weight'], reverse=True)

# Display top 10 heads
print(f"\nTOP 10 HEADS WITH HIGHEST ATTENTION WEIGHTS")
print(f"Between tokens: {list(token_indices.keys())}")
print(f"{'='*80}")

for i, head_info in enumerate(head_scores[:10]):
    layer = head_info['layer']
    head = head_info['head']
    maximum = head_info['max_weight']
    
    print(f"\n{i+1:2d}. Layer {layer:2d}, Head {head:2d}: Max Weight = {maximum:.6f}")
    
    # Show the strongest individual edges for this head
    edges = head_info['edge_details']
    edges.sort(key=lambda x: x[2], reverse=True)  # Sort by weight
    
    print(f"    Top edges:")
    for j, (from_idx, to_idx, weight) in enumerate(edges[:5]):
        from_token = tokens[from_idx]
        to_token = tokens[to_idx]
        print(f"      {j+1}. '{from_token}' → '{to_token}': {weight:.6f}")

print(f"\n{'='*80}")
print(f"SUMMARY STATISTICS")
print(f"{'='*80}")

# Calculate some statistics
all_weights = [head['max_weight'] for head in head_scores]
mean_weight = np.mean(all_weights)
std_weight = np.std(all_weights)
max_weight = np.max(all_weights)
min_weight = np.min(all_weights)

print(f"Total heads analyzed: {len(head_scores)}")
print(f"Mean maximum weight: {mean_weight:.6f}")
print(f"Standard deviation: {std_weight:.6f}")
print(f"Maximum weight: {max_weight:.6f}")
print(f"Minimum weight: {min_weight:.6f}")

# Show distribution by layer
print(f"\nTop head by layer:")
layer_best = {}
for head_info in head_scores:
    layer = head_info['layer']
    if layer not in layer_best or head_info['max_weight'] > layer_best[layer]['max_weight']:
        layer_best[layer] = head_info

for layer in sorted(layer_best.keys()):
    head_info = layer_best[layer]
    print(f"  Layer {layer:2d}: Head {head_info['head']:2d} (weight: {head_info['max_weight']:.6f})")

print(f"\n🏌️  Augusta National attention search complete! 🏌️")
print(f"{'='*60}")

# Generate multipage PDF with top performing heads
print(f'\nGenerating multipage PDF with top {how_many_pages_in_the_pdf} attention heads...')

# Remove SEP token from tokens for visualization (same as other scripts)
original_tokens = tokens.copy()
if tokens[-1] == '[SEP]':
    tokens_for_viz = tokens[:-1]
else:
    tokens_for_viz = tokens

pdf_path = "/Users/richardklassen/Developer/genuary/2025/Jul.12/augusta_search_results.pdf"

with PdfPages(pdf_path) as pdf:
    for i, head_info in enumerate(head_scores[:how_many_pages_in_the_pdf]):  # Top 10 heads
        layer = head_info['layer']
        head = head_info['head']
        max_weight = head_info['max_weight']
        edge_details = head_info['edge_details']
        
        print(f"  Generating page {i+1}/{how_many_pages_in_the_pdf}: Layer {layer}, Head {head}")
        
        # Get the attention matrix for this head
        layer_attention = attentions[layer-1][0]  # Convert to 0-indexed
        attention_matrix = layer_attention[head-1].numpy()  # Convert to 0-indexed
        
        # Remove SEP token row and column if present
        if len(original_tokens) > len(tokens_for_viz):
            attention_matrix = attention_matrix[:-1, :-1]
        
        # Create the chart
        fig = create_attention_chart_for_pdf(attention_matrix, layer, head, tokens_for_viz, max_weight, edge_details)
        
        # Save to PDF
        pdf.savefig(fig, facecolor=inverted_bg_color, edgecolor='none', bbox_inches='tight')
        plt.close(fig)

print(f"✅ PDF saved to: {pdf_path}")
print(f"📊 Generated {len(head_scores[:10])} pages showing heads with highest Augusta/National/It/Is attention")
print(f"🏌️  Complete visualization analysis ready! 🏌️")
