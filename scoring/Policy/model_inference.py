import os
import json
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
        
        # HACK
        enc_mapping = {
            'Original_Lead_Medium__c' : 'Lead_Medium__c'
        }
        
        if label_encoder.get(col) or col in list(enc_mapping.keys()):
            
            enc_col = enc_mapping.get(col, col)
            
            try:
                
                val = set(X[col].values)
                cle = set(label_encoder[enc_col].classes_)
                
                
                
                if val not in cle: 
                    X[col] = 'unknown'
                    
                X[col] = label_encoder[enc_col].transform(X[col])
                
                unknown_labels = list(val.difference(cle))
                
#                 if unknown_labels:
#                     # HACK : This should be handled by the config and not in code
#                     if 'unknown' in label_encoder[enc_col].classes_:
#                         X[col] = label_encoder[enc_col].transform(['unknown'])
#                     elif 'others' in label_encoder[enc_col].classes_:
#                         X[col] = label_encoder[enc_col].transform(['others'])
#                     else:
#                         raise Exception('Error in Encoding this value {}. The model has not been trained with this label for the field {}'.format(X[col], col))
#                 else:
#                     X[col] = label_encoder[enc_col].transform(X[col])

            except Exception as e:
                raise Exception('Error in Label encoding. For the field : {}, {}'.format(col, e))
                

    ## TODO: Fix the scaler 
    X = scaler.transform([X])
    return X
    

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
            
            data_config = lead_type["data_source"]
            considered_features = lead_type["considered_features"]
            selected_model = lead_type["select_model"]
            
            selected_label_encoder = lead_type["model_params"]['preprocessing_steps'][0]
            selected_scaler = lead_type["model_params"]['preprocessing_steps'][1]
            
            lead_type_f = _
            break
    else:

        reason = "Lead Source,Medium and Ad Source in combination did not match any of the lead model types" 
        
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

    ## Hack 
    enc_mapping = {
        'Original_Lead_Medium__c' : 'Lead_Medium__c'
    }

    data = encoding(data, encoders_dict)
    
    for k,v in enc_mapping.items():
        if k in data.columns:
            data.rename(columns={k : v}, inplace=True)
            
    # Model selection
    if node_dict['model_dict'].get(selected_model):
        model = node_dict['model_dict'][selected_model]
    else:
        raise Exception("No model key was found. Please check")

    
    prediction = model.predict_proba(data)
    score_ma = prediction[0][0]
    score_ms = prediction[0][1]
    
    quartiles = json.load(open(config_dict['quartiles']))
    likelihood_ma = get_likelihood(score_ma, quartiles)
    likelihood_ms = get_likelihood(score_ms, quartiles)
    
#     result_dict = {
#         'l1_score' : score,
#         'l1_likelihood' : likelihood,
#         'l1_reason' : '',
#         'lead_type' : lead_type_f
#     }

    result_dict = [

        {
        "type": "update_score_for_policy_ma",
        "score": score_ma,
        "likelihood": likelihood_ma,
    },
      {
        "type": "update_score_for_policy_ms",
        "score": score_ms,
        "likelihood": likelihood_ms,
      }
        
    ]
    
    return result_dict

def get_likelihood(score, quartiles):
    
    bucket = list(quartiles.values())
    
    if score < bucket[0]:
        return 1
    elif score > bucket[0] and score < bucket[1]:
        return 2
    elif score > bucket[1] and score < bucket[2]:
        return 3
    elif score > bucket[2]:
        return 4
    
    return -1