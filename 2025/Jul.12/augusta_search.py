import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import torch
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages
from transformers import AutoTokenizer, AutoModel



# Setup

COLOR_LOW = '#121212'  # Charcoal
COLOR_ACCENT = '#FFDD00'  # Yellow accent
COLOR_TEXT = '#2E2E2E'
COLOR_TOP = '#FFFFFF'
coronograph = 0.0 # selector for values along the identity diagonal
sentence = "Augusta National is a golf course I won't ever play, but it is a bucket list item"
model_name = "bert-base-uncased"
edge_color = COLOR_TEXT
bg_color = COLOR_LOW
font_path = "src/PublicSans-Regular.ttf"
pdf_path = "output_pdf/augusta_search_results.pdf"
how_many_pages_in_the_pdf = 24



#######################////////////////////////////////////////////////////////
# Evaluator Function
#######################////////////////////////////////////////////////////////


# Set up matplotlib with Public Sans Regular from local file
try:
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

# Create inverted colormap
color_positions = [0.0, 0.5, 1.0]
inverted_colors = [COLOR_LOW, COLOR_ACCENT, COLOR_TOP]
inverted_cmap = LinearSegmentedColormap.from_list(
    'InvertedBlues', 
    list(zip(color_positions, inverted_colors)),
    N=256
)

# Configure matplotlib for inverted appearance

plt.rcParams.update({
    'font.size': 11,
    'axes.linewidth': 1.2,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.bottom': True,
    'axes.spines.left': True,
    'axes.edgecolor': edge_color,
    'axes.labelcolor': COLOR_TEXT,
    'text.color': COLOR_TEXT,
    'xtick.color': COLOR_TEXT,
    'ytick.color': COLOR_TEXT,
    'figure.facecolor': bg_color,
    'axes.facecolor': bg_color
})


#######################////////////////////////////////////////////////////////
# RUN Model and score the results
#######################////////////////////////////////////////////////////////

# Get model outputs with attention
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, output_attentions=True, attn_implementation="eager")
inputs = tokenizer(sentence, return_tensors="pt", add_special_tokens=True)
tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
with torch.no_grad():
    outputs = model(**inputs)
    attentions = outputs.attentions

head_scores_unsored = [
    {
        'layer': layer_idx + 1,
        'head': head_idx + 1,
        'score': evaluator_function(attentions[layer_idx][0][head_idx].numpy()),
        'edge_details': {}
    }
    for layer_idx in range(len(attentions))
    for head_idx in range(attentions[layer_idx].shape[1])
]
# Sort by score descending for top heads
head_scores = sorted(head_scores_unsored, key=lambda x: x['score'], reverse=True)

#######################////////////////////////////////////////////////////////
# Generate multipage PDF with top performing heads
#######################////////////////////////////////////////////////////////

print(
    f'\nGenerating multipage PDF with top '
    f'{how_many_pages_in_the_pdf} attention heads...'
)

# Remove SEP token from tokens for visualization (same as other scripts)
original_tokens = tokens.copy()
if tokens[-1] == '[SEP]':
    tokens_for_viz = tokens[:-1]
else:
    tokens_for_viz = tokens

with PdfPages(pdf_path) as pdf:
    for i, head_info in enumerate(head_scores[:how_many_pages_in_the_pdf]):  # Top heads
        
        # Get the attention matrix for this head
        layer = head_info['layer']
        head = head_info['head']
        max_weight = head_info['max_weight']
        edge_details = head_info['edge_details']
        print(f"  Generating page {i+1}/{how_many_pages_in_the_pdf}: Layer {layer}, Head {head}")
        layer_attention = attentions[layer-1][0]  # Convert to 0-indexed
        attention_matrix = layer_attention[head-1].numpy()  # Convert to 0-indexed
        
        # Remove SEP token row and column if present
        if len(original_tokens) > len(tokens_for_viz):
            attention_matrix = attention_matrix[:-1, :-1]
        
        # Create the chart, save pdf
        fig = chart_to_pdf(
            attention_matrix = attention_matrix,
            layer_num = layer,
            head_num = head,
            tokens = tokens_for_viz,
            total_weight = max_weight,
            edge_details = edge_details
        )
        pdf.savefig(fig, facecolor=bg_color, edgecolor='none', bbox_inches='tight')
        plt.close(fig)

print(
    f"✅ Generated {pdf_path} with "
    f"{len(head_scores[:how_many_pages_in_the_pdf])} pages showing heads "
    f"with highest Augusta/National/It/Is attention"
)
print(
    f"Complete visualization analysis ready!"
)
