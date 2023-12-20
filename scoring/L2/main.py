# General imports
import os
import random
import logging
import joblib
import traceback

# Internal imports
from auxiliary.util.global_constants import NODE_L2
from auxiliary.util.global_constants import WTS_PATH
from auxiliary.util.global_constants import (
    LEAD_DATA,
    NEUSTAR_DATA,
    LEAD_REQ_SCORE,
    POLICY_REQ_SCORE,
    ENC_PATH,
    WTS_PATH,
    SCL_ENC_PATH,
    _ENC_EXT_L2,
)
from auxiliary.util.common_utils import (
    setup_logger,
    check_and_unpack_data,
    create_arguments_dict,
)

from scoring.L2.L2_model import do_inference
from scoring.L2.model_inference import initialize_model

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

    encoders_path = os.path.join(_FILE_PATH, ENC_PATH)
    print(encoders_path)

    parent_path_to_scalers = os.path.join(encoders_path, SCL_ENC_PATH)
    print(parent_path_to_scalers)

    scalers_dict = {}

    for r, d, f in os.walk(parent_path_to_scalers):
        for scl in f:
            print(scl)
            key = scl.replace(_ENC_EXT_L2, "")
            key = key.split("-")[0]
            # with open(os.path.join(r, scl), "rb") as f:
            # scalers_dict[key] = pickle.load(f)
            scalers_dict[key] = joblib.load(os.path.join(r, scl))

    # Fix model in the later patches
    # model = initialize_model(weights_path)

    logger.info("Node initialized. Models, scalers, encoders Loaded")

    initialized_objects = {
        # "model_dict": model_dict,
        "scalers": scalers_dict,
    }

    print(f"{initialized_objects}")

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
    args_dict = create_arguments_dict(parsed_data, ["data", "lead_id"])
    score_request = args_dict["data"][LEAD_DATA]["type"]

    try:
        if score_request == "update_score_for_lead":
            score, time_since_lead_creation = do_inference(
                args_dict, node_dict
            )  ### check
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
