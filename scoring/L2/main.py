# General imports
import os
import random
import logging

# Internal imports
from auxiliary.util.global_constants import NODE_L2 
from auxiliary.util.global_constants import WTS_PATH
from auxiliary.util.common_utils import setup_logger, check_and_unpack_data, create_arguments_dict

from scoring.L2.L2_model import initialize_model

logger = setup_logger(NODE_L2, logging.INFO)
local_flag = True if os.getenv('local') else False

_FILE_PATH = os.path.realpath(os.path.dirname(__file__)) 

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
    
    weights_path = os.path.join(_FILE_PATH, WTS_PATH)
    
    # Fix model in the later patches
    # model = initialize_model(weights_path)
    
    model = None
    
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
    args_dict = create_arguments_dict(parsed_data, ['data'])

    result_dict = {
        'l2_lead_score' : random.random(),
        'l2_policy_score' : 0
    }
        
    return result_dict


if __name__ == '__main__':
    pass
