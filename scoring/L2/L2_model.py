import os
import sys
import math
import random
import joblib

import numpy as np
import pandas as pd

import torch
from torch.nn.utils.rnn import pad_sequence
from scipy.special import softmax

from scoring.L2.model_inference import generate_df, model_inference


weights_path = os.path.dirname(os.path.realpath(__file__))


# Helpers 

def increasing_function(x):
    return round(math.log(x + 1), 3)

def normalize_list(lst):
    min_value = min(lst)
    max_value = max(lst)
    normalized_lst = [(value - min_value) / (max_value - min_value) for value in lst]
    return normalized_lst

# def initialize_model(wts_path):

#     wts = None

#     for r,d,f in os.walk(wts_path):

#         for weights in f:
#             wts = os.path.join(r, weights)
    
#     # Initialization

#     model = torch.load(wts)
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
#     model.to(device)
#     model.eval()
    
#     return model


def transform_features(features):
    
    Xp, time_since_lead_creation = generate_df(features)
    
    return Xp, time_since_lead_creation


def do_inference(X):
    
    Xp, time_since_lead_creation = transform_features(features)
    score = model_inference(Xp)
    
    return score, time_since_lead_creation