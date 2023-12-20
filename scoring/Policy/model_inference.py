import os
import json
import joblib

import pandas as pd

from auxiliary.util.global_constants import _WTS_EXT_L1
from scoring.Policy.translators import Translator

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
                           
    
def encoding(features, encoders_dict, numeric_cols, categorical_cols):

    label_encoder = encoders_dict["label_encoder"]
    scaler = encoders_dict["scaler"]

    if not isinstance(features, pd.DataFrame):
        X = pd.DataFrame.from_dict(features, orient="index").T
    else:
        X = features
        
#     X = X.loc[:,~X.T.duplicated(keep='last')]

    for col in categorical_cols:
        
        if label_encoder.get(col):
            try:
                val = set(X[col].values)
                cle = set(label_encoder[col].classes_)

                if val not in cle:
                    X[col] = "unknown"

                X[col] = label_encoder[col].transform(X[col])

            except Exception as e:
                raise Exception(
                    "Error in Label encoding. For the field : {}, {}".format(col, e)
                )
                
    print(X[numeric_cols])
    
    
   
    

    X[numeric_cols] = scaler.transform(X[numeric_cols])
    
    return X
    
    

def inference(node_dict, data, score_request):

    model_config = node_dict["inference_cfg"]
    config_dict = node_dict["config_dict"]


    filters_t = transform_features(
        data, config_dict["feature_config"]
    )  # include new data config
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

            condition_1 = fk in filters_t[0]
            condition_2 = filters_t[0][fk] in fv
            condition_final = condition_1 and condition_2
            filter_condition.append(condition_final)

        if all(filter_condition):

            data_config = lead_type["data_source"]
#             considered_features = lead_type["considered_features"]
            numeric_cols = lead_type["numeric_features"]
            categorical_cols = lead_type["categorical_features"]
            selected_model = lead_type["model_wts"]
            considered_features = numeric_cols+categorical_cols

            selected_label_encoder = lead_type["model_params"]["preprocessing_steps"][0]
            selected_scaler = lead_type["model_params"]["preprocessing_steps"][1]

            lead_type_f = lead_type['select_model']

            break
    else:

        reason = "Lead Source, Medium and Ad Source in combination did not match any of the lead model types"

        raise Exception(reason)

    # Feature selection
    if config_dict.get(data_config):
        data = transform_features(data, config_dict[data_config])
    else:
        raise Exception(
            "No data transform config was found for key {}. Please check".format(
                data_config
            )
        )
    data = pd.DataFrame.from_dict(data[0], orient="index").T
    
    data_subset_features = data[considered_features]

    # Encoding
    label_encoder_dict = node_dict["label_encoders"]
    scaler_dict = node_dict["scalers"]
    
    print('*'*100)
    print(selected_label_encoder, selected_scaler)

    if label_encoder_dict.get(selected_label_encoder):
        label_encoder = label_encoder_dict[selected_label_encoder]
    else:
        raise Exception("No Encoder matching found")

    if scaler_dict.get(selected_scaler):
        scaler = scaler_dict[selected_scaler]
    else:
        raise Exception("No Scaler matching found")

    encoders_dict = {"label_encoder": label_encoder, "scaler": scaler}

    ## Hack
    enc_mapping = {"Original_Lead_Medium__c": "Lead_Medium__c"}

    data_subset_features = encoding(data_subset_features, encoders_dict, numeric_cols, categorical_cols)

    for k, v in enc_mapping.items():
        if k in data.columns:
            data_subset_features.rename(columns={k: v}, inplace=True)

    # Model selection
    if node_dict["model_dict"].get(selected_model):
        model = node_dict["model_dict"][selected_model]
    else:
        raise Exception("No model key was found. Please check")
        

    ordered_cols = model.get_booster().feature_names
    data_subset_features = data_subset_features[ordered_cols]
    prediction = model.predict_proba(data_subset_features)
    score_ma = prediction[0][0]
    score_ms = prediction[0][1]
    
    quartiles = json.load(open(config_dict['quartiles']))
    likelihood_ma = get_likelihood(score_ma, quartiles)
    likelihood_ms = get_likelihood(score_ms, quartiles)


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