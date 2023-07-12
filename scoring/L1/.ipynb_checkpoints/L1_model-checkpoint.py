import sys
import random
import joblib

import numpy as np
import pandas as pd

import torch
from torch.nn.utils.rnn import pad_sequence
from scipy.special import softmax


weights_path = os.path.dirname(os.path.realpath(__file__))


# Helpers 

def increasing_function(x):
    return round(math.log(x + 1), 3)

def normalize_list(lst):
    min_value = min(lst)
    max_value = max(lst)
    normalized_lst = [(value - min_value) / (max_value - min_value) for value in lst]
    return normalized_lst

def initialize_model(wts_path):
    
    # Initialization

    model = torch.load(wts_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model.to(device)
    model.eval()
    
    return model


def transform_features(features):
    
    # Do something here
    
    return features


def inference(X):
    
    # Do inference here
    
    return X