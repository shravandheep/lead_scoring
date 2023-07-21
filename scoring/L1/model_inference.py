import os
import joblib

import pandas as pd

from auxiliary.util.global_constants import _WTS_EXT_L1
from scoring.L1.translators import Translator

# Helpers 
def initialize_model(wts_path):

    all_wts = []
    model_dict = {}
    
    for r,d,f in os.walk(wts_path):
        for weights in f:
            all_wts.append(os.path.join(r, weights))
    
    for wt in all_wts:
        
        model_name = wt.split('/')[-1].replace(_WTS_EXT_L1, '')
        model = joblib.load(wt)
        model_dict[model_name] = model

    return model_dict


def transform_features(data, config_path):
    
    feature_translator = Translator(config_path) 
    features = feature_translator.translate(data)
    
    return features
                           
    
def encoding(features, encoders_dict):
    
    label_encoder = encoders_dict['label_encoder']
    scaler = encoders_dict['scaler']

    if not isinstance(features, pd.DataFrame):
        X = pd.DataFrame.from_dict(features, orient='index').T
    else:
        X = features

    for col in X.columns:
        if label_encoder.get(col):
            
            try:
                X[col] = label_encoder[col].transform(X[col])
            except Exception as e:
                print('For the column :', col, e)
                raise Exception('Error in Label encoding')
                

    ## TODO: Fix the scaler 
    # X = scaler.transform(X)
    return X
    
    
# TODO: Please don't use this function in the future
# This is a hack / hardcoded function
def handle_lead_type(data):
    
    default_values = {
        'LeadSource': 'MedicareFAQ',
        'Lead_Medium__c' : 'search',
        'Original_Lead_Ad_Source__c' : 'google'
    }
    
    for k,v in default_values.items():
        
        if not data.get(k, False) or data.get(k) == '':
            data[k] = v
            
    return data

def inference(node_dict, data, score_request):
                           
    model_config = node_dict['inference_cfg']    
    config_dict = node_dict['config_dict']
    
    data = handle_lead_type(data)
    filters_t = transform_features(data, config_dict['feature_config']) #include new data config 
    
    data_config = None
    considered_features = []
    
    selected_model = None
    selected_scaler = None
    selected_label_encoder = None
    
    for key, value in model_config.items():
        
        filters = value.get("filters", {})
        
        if all(filter_name in filters_t and filters_t[filter_name] in filter_values for filter_name, filter_values in filters.items()):
            
            # nuestar logic
            neu_match = "matched"
            
            
            selected_model = value["neustar_filter"][neu_match]["select_model"]
            data_config = value["neustar_filter"][neu_match]["data_source"]
            considered_features = value["neustar_filter"][neu_match]["considered_features"]
            selected_label_encoder = value["neustar_filter"][neu_match]["model_params"]['preprocessing_steps'][0]
            selected_scaler = value["neustar_filter"][neu_match]["model_params"]['preprocessing_steps'][1]
            break
    
    # Feature selection
    if config_dict.get(data_config):
        data = transform_features(data, config_dict[data_config])
    else:
        raise Exception("No data transform config was found for key {}. Please check".format(data_config))

    data = pd.DataFrame.from_dict(data, orient='index').T
    data = data[considered_features]
    
    # Encoding 
    label_encoder_dict = node_dict['label_encoders']
    scaler_dict = node_dict['scalers']
    

    if label_encoder_dict.get(selected_label_encoder):
        label_encoder = label_encoder_dict[selected_label_encoder]
    else:
        raise Exception("No Encoder matching found")
        
    if scaler_dict.get(selected_scaler):
        scaler = scaler_dict[selected_scaler]
    else:
        raise Exception("No Scaler matching found")
        
    encoders_dict = {
        'label_encoder' : label_encoder,
        'scaler' : scaler
    }
    
    data = encoding(data, encoders_dict)
    
    # Model selection
    if node_dict['model_dict'].get(selected_model):
        model = node_dict['model_dict'][selected_model]
    else:
        raise Exception("No model key was found. Please check")

    prediction = model.predict_proba(data)
    score = prediction[0][1]
    
    return score