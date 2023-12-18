# General imports
import os
import logging

# Internal imports
from auxiliary.util.global_constants import NODE_CONSOLIDATION
from auxiliary.util.global_constants import LEAD_DATA, NEUSTAR_DATA, LEAD_REQ_SCORE, POLICY_REQ_SCORE
from auxiliary.util.common_utils import setup_logger, check_and_unpack_data, create_arguments_dict

from consolidation_logic import compute_hybrid


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
    
    required_keys = ['lead_id', 'l1_score', 'l1_reason', 'l1_likelihood',
                     'l2_score', 'l2_reason']
    
    parsed_data, packet_id, _ = check_and_unpack_data(data)
    args_dict = create_arguments_dict(parsed_data, required_keys)
    score_request = args_dict['data'][LEAD_DATA]['type']
    
    
    l1_score = arrgs_dict['l1_score']
    
    if args_dict['l2_score']:
        l2_score = args_dict['l2_score']
    else:
        l2_score = 0
        
    final_score = compute_hybrid(l1_score. l2_score, 500)   ##check if we have time here
    
    
    
    
    # HACK 
    
    
    final_score = args_dict['l1_score']
    final_likelihood = args_dict['l1_likelihood']
    final_args = dict((k,v) for (k,v) in args_dict.items() if k in required_keys)
    
    

    result_dict = {
        **final_args,
        'score' : final_score,
        'type' : score_request,
        'likelihood' : final_likelihood
    }
        
    return result_dict


if __name__ == '__main__':
    pass
