import os
import sys
import random
import joblib
import pickle

import numpy as np
import pandas as pd

import time
import torch
from torch.nn.utils.rnn import pad_sequence
from scipy.special import softmax

from scoring.L1.plugins import Plugin 
from scoring.L1.translators import Translator


# Helpers 

def initialize_model(wts_path):

    all_wts = []
    model_dict = {}
    
    for r,d,f in os.walk(wts_path):
        for weights in f:
            all_wts.append(os.path.join(r, weights))
    
    for wt in all_wts:
        
        model_name = wt.split('/')[-1].replace('.sav', '')
        model = joblib.load(wt)
        model_dict[model_name] = model

    return model_dict


def transform_features(data, config_path):
    
    feature_translator = Translator(config_path) ##data config path
    features = feature_translator.translate(data)
    
    return features
                           
    
def encoding(features, node_dict):
    
    label_encoder = node_dict['label_encoder']
    scaler = node_dict['scaler']

    if not isinstance(features, pd.DataFrame):
        X = pd.DataFrame.from_dict(features, orient='index').T
    else:
        X = features

    print('LE :', label_encoder.keys())
    for col in X.columns:
        if label_encoder.get(col):
            X[col] = label_encoder[col].transform(X[col])

    X['class_url'] = 0
    X['Lead_Medium__c'] = 0
    
#     X = scaler.transform(X)
    return X
    

def inference(model_dict, data):
                           
    model_config = model_dict['inference_cfg']    
    config_dict = model_dict['config_dict']
    
    filters = transform_features(data, config_dict['feature_config']) #include new data config 
                           
                           
    for key, value in model_config.items():
        filters = value.get("filters", {})

        if all(filter_name in filters and \
               filters[filter_name] in filter_values for filter_name, filter_values in filters.items()):

            # TODO : Write the new star data logic either to query or to check cache
            # Nuestar logic
            neu_match = "not_matched"     
    

            select_model = value["neustar_filter"][neu_match]["select_model"]
            data_config = value["neustar_filter"][neu_match]["data_source"]
            considered_features = value["neustar_filter"][neu_match]["considered_features"]
            break
    
    
    if config_dict.get(data_config):
        data = transform_features(data, config_dict[data_config])
    else:
        raise Exception("No config was found. Please check")
    
    data.pop('CreatedDate')
    
    
    data = pd.DataFrame.from_dict(data, orient='index').T
    data = data[considered_features]
    
    data = encoding(data, model_dict)
    
    if model_dict['model_dict'].get(select_model):
        model = model_dict['model_dict'][select_model]
    else:
        raise Exception("No model key was found. Please check")

    prediction = model.predict_proba([data.values])[0]
    score = prediction[1]
    
    return score




