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
                
                val = set(X[col].values)
                cle = set(label_encoder[col].classes_)
                unknown_labels = list(val.difference(cle))
                
                if unknown_labels:
                    # HACK : This should be handled by the config and not in code
                    if 'unknown' in label_encoder[col].classes_:
                        X[col] = label_encoder[col].transform(['unknown'])
                    elif 'others' in label_encoder[col].classes_:
                        X[col] = label_encoder[col].transform(['others'])
                    else:
                        raise Exception('Error in Encoding this value {}. The model has not been trained with this label for the field {}'.format(X[col], col))
                else:
                    X[col] = label_encoder[col].transform(X[col])
            except Exception as e:
                raise Exception('Error in Label encoding. For the field : {}, {}'.format(col, e))
                

    ## TODO: Fix the scaler 
    # X = scaler.transform(X)
    return X
    
    
# TODO: Please don't use this function in the future
# This is a hack / hardcoded function
def handle_lead_type(data):
    
    default_values = {
        'LeadSource': 'deafult',
        'Lead_Medium__c' : 'default',
        'Original_Lead_Ad_Source__c' : 'default'
    }
    
    for k,v in default_values.items():
        
        if data.get(k) == '' or not data.get(k): 
            data[k] = v
            
    return data

def inference(node_dict, data, score_request):
                           
    model_config = node_dict['inference_cfg']    
    config_dict = node_dict['config_dict']
    
    # Disabled temporarily
    # data = handle_lead_type(data)
    filters_t = transform_features(data, config_dict['feature_config']) #include new data config 
    lead_type_f = None
    
    
    data_config = None
    selected_model = None
    selected_scaler = None
    selected_label_encoder = None
    considered_features = list()
    
    for _, lead_type in model_config.items():
        
        filters = lead_type.get("filters", {})
        filter_condition = []
        
        for (fk, fv) in filters.items():
            
            condition_1 = fk in filters_t 
            condition_2 = filters_t[fk] in fv 
            condition_final = condition_1 and condition_2
            filter_condition.append(condition_final)
            
            
        if all(filter_condition):
            # TODO: Write a better neustar logic. This process might change in the future
            # nuestar logic
            
            neu_match = "matched"

            data_config = lead_type["neustar_filter"][neu_match]["data_source"]
            considered_features = lead_type["neustar_filter"][neu_match]["considered_features"]
            selected_model = lead_type["neustar_filter"][neu_match]["select_model"]
            selected_label_encoder = lead_type["neustar_filter"][neu_match]["model_params"]['preprocessing_steps'][0]
            selected_scaler = lead_type["neustar_filter"][neu_match]["model_params"]['preprocessing_steps'][1]
            
            lead_type_f = _
            break
    else:
        
        type_matching_keys = ['LeadSource', 'Lead_Medium__c', 'Original_Lead_Ad_Source__c']
        reason = "LeadSource, Lead_Medium__c and Original_Lead_Ad_Source__c in combination did not match any of the lead types" 
        
        raise Exception(reason)
    
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
    
    result_dict = {
        'l1_score' : score,
        'l1_reason' : '',
        'lead_type' : lead_type_f
    }
    
    return result_dict