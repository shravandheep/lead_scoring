# General imports
import os
import logging

# Internal imports
from auxiliary.util.global_constants import NODE_L1, L2_MODEL_WTS_FILE
from auxiliary.util.common_utils import setup_logger, check_and_unpack_data, create_arguments_dict

logger = setup_logger(NODE_L1, logging.INFO)
local_flag = True if os.getenv('local') else False

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
    
    path_to_weights = os.path.join(weights_path, 'weights', L2_MODEL_WTS_FILE)
    model = initialize_model(path_to_weights)
    
    logger.info('Node initialized')
    
    return model


def process(data, model):
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
    args_dict = create_arguments_dict(parsed_data, ['input'])


    result_dict = {
        "L1_model_score": 1.0
    }
        
    return result_dict


if __name__ == '__main__':
    pass
