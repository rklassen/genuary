import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import torch
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages
from transformers import AutoTokenizer, AutoModel


#######################////////////////////////////////////////////////////////
# Evaluator Function
#######################////////////////////////////////////////////////////////

def evaluator_function(
    attention_matrix: np.ndarray,
    tokens: list[str],
) -> float:
    '''
    a function that responds with a scalar representing how well the input head
    matches the search criteria.
    '''
    return 1.0
