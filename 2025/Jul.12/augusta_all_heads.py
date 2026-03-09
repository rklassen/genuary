os.chdir(os.path.dirname(os.path.abspath(__file__)))
import csv
import matplotlib.pyplot as plt
import numpy as np
import os
import torch
from transformers import AutoTokenizer, AutoModel
from matplotlib.colors import LinearSegmentedColormap
from src.matrix_to_figure import matrix_to_figure, set_font_as_gloal_state_change


COLOR_LOW = '#121212'  # Charcoal
COLOR_ACCENT = '#FFDD00'  # Yellow accent
COLOR_TOP = '#FFFFFF'
inverted_edge_color = '#d1d1d1'
inverted_text_color = '#d1d1d1'
inverted_bg_color = COLOR_LOW
font_path = "./src/PublicSans-Regular.ttf"
heads_pdf_dir = "output_pdf/"
heads_png_dir = "output_png/"
heads_csv_dir = "output_csv/"
sentence = "Augusta National is a golf course I won't ever play, but it is a bucket list item"
model_name = "bert-base-uncased"


def matrix_to_csv(attention_matrix, tokens, output_path):
    '''Save attention matrix as CSV with tokens as column headers'''
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)        
        writer.writerow(tokens)  # header
        writer.writerows(map(list, attention_matrix))  # numerical data


# ✨ calculate `attentions: List[np.ndarray]` ✨
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(
    model_name,
    output_attentions=True,
    attn_implementation="eager"
)
inputs = tokenizer(
    sentence,
    return_tensors="pt",
    add_special_tokens=True
)
tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
with torch.no_grad():
    outputs = model(**inputs)
    attentions = outputs.attentions

# Remove SEP token from tokens list for all visualizations
original_tokens = tokens.copy()
sep_index = len(tokens) - 1
if tokens[sep_index] == '[SEP]':
    tokens = tokens[:-1]
    print(f"Removed SEP token. Filtered tokens: {tokens}")

# Verify filepaths.
folder = os.path.dirname(os.path.abspath(__file__))
output_folders = [
    os.path.join(folder, dir)
    for dir in [heads_pdf_dir, heads_png_dir, heads_csv_dir]
]
for d in output_folders:
    if not os.path.exists(d):
        # tell user about all folders rather than making them hit multiple
        # runtime errors with no end in sight
        print(f"Create the following folders: {d}")
        [print(f"    {d}") for d in output_folders]
        exit(1)

# Set font as a global state change
set_font_as_gloal_state_change(font_path)


# Create inverted colormap
color_positions = [0.0, 0.5, 1.0]
inverted_colors = [COLOR_LOW, COLOR_ACCENT, COLOR_TOP]
inverted_cmap = LinearSegmentedColormap.from_list(
    'InvertedBlues',
    list(zip(color_positions, inverted_colors)),
    N=256,
)

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
    'axes.facecolor': inverted_bg_color,
})


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
        csv_filename = f'layer_{layer_idx+1:02d}_head_{head_idx+1:02d}.csv'
        pdf_filename = f'layer_{layer_idx+1:02d}_head_{head_idx+1:02d}.pdf'
        png_filename = f'layer_{layer_idx+1:02d}_head_{head_idx+1:02d}.png'
        pdf_path = os.path.join(heads_pdf_dir, pdf_filename)
        png_path = os.path.join(heads_png_dir, png_filename)
        csv_path = os.path.join(heads_csv_dir, csv_filename)

        # Create the chart and save CSV
        matrix_to_figure(attention_matrix, layer_idx + 1, head_idx + 1, tokens, 0.0, inverted_cmap, inverted_text_color, COLOR_ACCENT)
        matrix_to_csv(attention_matrix, tokens, csv_path)
        
        total_charts += 1
        if total_charts % 12 == 0:  # Progress update every layer
            print(f"  Generated {total_charts} charts...")

print(f"\n🏌️  Generated {total_charts} attention head visualizations! 🏌️")
print(f"PNGs and CSVs saved to: {heads_png_dir} and {heads_csv_dir}")
print(f"{'='*60}")
