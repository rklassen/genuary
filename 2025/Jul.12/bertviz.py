import matplotlib.pyplot as pyplot
import numpy
import os
from transformers import AutoTokenizer
from transformers import AutoModel

HEAD_INDEX = 0
ATTENTION_THRESHOLD = 0.05
os.makedirs('attention_visualizations', exist_ok=True)

model_name = 'bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, output_attentions=True)

sentence = "the forman was on the phone with the engineer while grabbing a coffee mug from his truck"
inputs = tokenizer(sentence, return_tensors='pt')
outputs = model(**inputs)

# Get tokens and process them
tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

# Remove the [SEP] token early in the process
sep_idx = tokens.index('[SEP]') if '[SEP]' in tokens else -1
if sep_idx >= 0:
    # Remove the [SEP] token from tokens
    tokens = tokens[:sep_idx] + tokens[sep_idx+1:]

# Rename [CLS] to "Significance" in bold
cls_idx = tokens.index('[CLS]')  if '[CLS]' in tokens else -1
if cls_idx >= 0:
    tokens[cls_idx] = "Significance"

num_tokens = len(tokens)

# Function to calculate the column amplitude score (formerly interactive spread)
def column_amplitude(column, attention_threshold=0.05):
    """
    Calculate the amplitude of a column based on interactions between all pairs of pixels.
    For each pixel, we consider all other pixels that follow it, and calculate the 
    product of their attention weights multiplied by their distance. Attention weights
    below the threshold are truncated to zero.
    
    Args:
        column: The column of attention weights
        attention_threshold: Threshold below which attention weights are truncated to zero
        
    Returns:
        float: Column amplitude score
    """
    # Truncate attention values below threshold to zero
    truncated_column = numpy.where(column >= attention_threshold, column, 0)
    
    num_rows = len(truncated_column)
    amplitude_score = 0
    
    # For each pixel
    for i in range(num_rows):
        # Only proceed if this pixel has significant attention
        if abs(truncated_column[i]) > ATTENTION_THRESHOLD:
            amplitude_score += truncated_column[i] ** 2  # Square the attention weight
            # # For each other pixel that follows it
            # for j in range(i+1, num_rows):
            #     # Only consider if the other pixel also has significant attention
            #     if truncated_column[j] > ATTENTION_THRESHOLD:
            #         # Calculate distance between pixels
            #         distance = j - i
            #         # Multiply both attention weights and distance
            #         column_i = truncated_column[i] ** 2
            #         column_j = truncated_column[j] ** 2
            #         interaction = column_i * column_j * distance
            #         # atomic sum
            #         amplitude_score += interaction
    
    return amplitude_score

