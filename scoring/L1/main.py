# General imports
import os
import json
import pickle
import logging

# Internal imports
from auxiliary.util.global_constants import NODE_L1, L1_MODEL_WTS_FILE
from auxiliary.util.common_utils import setup_logger, check_and_unpack_data, create_arguments_dict

from scoring.L1.model_inference import initialize_model, inference

logger = setup_logger(NODE_L1, logging.INFO)
local_flag = True if os.getenv('local') else False


_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
config_path = os.path.join(_FILE_PATH, 'configs')
encoders_path = os.path.join(_FILE_PATH, 'encoders')
weights_path = os.path.join(_FILE_PATH, 'weights')

def initialize_node(node_config, **kwargs):
    """
    Initialize node

    Parameters :
    ----------
        kwargs : dict of config args

    Returns :
    -------
        None
    """
    
    path_to_inference = os.path.join(config_path, 'model_inference.json')
    path_to_encoders = os.path.join(encoders_path, 'label_encoders.pkl')
    path_to_scalers = os.path.join(encoders_path, 'scaler.pkl')
    
    
    model_dict = initialize_model(weights_path)
    
    with open(path_to_encoders, 'rb') as f:
        label_encoder = pickle.load(f)
        
    with open(path_to_scalers, 'rb') as f:
        scaler = pickle.load(f)
        
    with open(path_to_inference) as inf:
        inference_cfg = json.load(inf)
    
    config_dict = dict()
    
    for r,d,f in os.walk(config_path):
        for files in f:
            key = files.replace('.json', '')
            config_dict[key] = os.path.join(r, files)

    
    logger.info('Node initialized. Models, scalers, encoders Loaded')
    
    
    initialized_objects = {
        'model_dict' : model_dict,
        'inference_cfg' : inference_cfg,
        'config_dict' : config_dict,
        'label_encoder' : label_encoder,
        'scaler' : scaler
    }
    
    return initialized_objects


def process(data, node_dict):
    """
    Process data from parent nodes. Parent node for Border is Background

    Parameters :
    ----------
        data : dict of (parent, result) pairs
        kwargs : dict of config arguments

    Returns :
    -------
        result_dic : dict of result
    """

    parsed_data, packet_id, _ = check_and_unpack_data(data)
    args_dict = create_arguments_dict(parsed_data, ['data'])

    lead_data = args_dict['data']
    score = inference(node_dict, lead_data)
    
    result_dict = {
        'L1_model_score' : score
    }
        
    return result_dict


if __name__ == '__main__':
    pass
