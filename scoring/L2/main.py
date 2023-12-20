# General imports
import os
import random
import logging

import traceback

# Internal imports
from auxiliary.util.global_constants import NODE_L2
from auxiliary.util.global_constants import WTS_PATH
from auxiliary.util.global_constants import (
    LEAD_DATA,
    NEUSTAR_DATA,
    LEAD_REQ_SCORE,
    POLICY_REQ_SCORE,
)
from auxiliary.util.common_utils import (
    setup_logger,
    check_and_unpack_data,
    create_arguments_dict,
)

from scoring.L2.L2_model import do_inference

logger = setup_logger(NODE_L2, logging.INFO)
local_flag = True if os.getenv("local") else False

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

    logger.info("Node initialized")

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
    args_dict = create_arguments_dict(parsed_data, ["data"])
    score_request = args_dict["data"][LEAD_DATA]["type"]

    try:
        if score_request == "update_score_for_lead":
            score, time_since_lead_creation = do_inference(args_dict)  ### check
            reason = ""
            result_dict = {
                "l2_score": score,
                "time_since_lead_creation": time_since_lead_creation,
                "l2_reason": reason,
            }
        else:
            result_dict = {}
    except:
        result_dict = {
            "l2_score": 0,
            "time_since_lead_creation": 300,
            "l2_reason": traceback.format_exc(),
        }

    return result_dict


if __name__ == "__main__":
    pass
