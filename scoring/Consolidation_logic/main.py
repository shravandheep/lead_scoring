# General imports
import os
import logging

# Internal imports
from auxiliary.util.global_constants import NODE_CONSOLIDATION
from auxiliary.util.common_utils import setup_logger, check_and_unpack_data, create_arguments_dict

logger = setup_logger(NODE_CONSOLIDATION, logging.INFO)
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

    
    logger.info('Node initialized')


def process(data):
    """
    Process data from parent nodes. Parent nodes for Consolidation Node are L1 and L2 nodes

    Parameters :
    ----------
        data : dict of (parent, result) pairs
        kwargs : dict of config arguments

    Returns :
    -------
        result_dic : dict of result
    """

    required_keys = ['lead_id', 'l1_lead_score', 'l1_policy_score', 
                     'l2_lead_score', 'l2_policy_score']
    
    parsed_data, packet_id, _ = check_and_unpack_data(data)
    args_dict = create_arguments_dict(parsed_data, required_keys)
    
    # HACK 
    final_lead_score = args_dict['l1_lead_score']
    final_policy_score = args_dict['l1_policy_score']
    
    final_args = dict((k,v) for (k,v) in args_dict.items() if k in required_keys)

    result_dict = {
        **final_args,
        'lead_score' : final_lead_score,
        'policy_score' : final_policy_score
    }
        
    return result_dict


if __name__ == '__main__':
    pass
