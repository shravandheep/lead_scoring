# General imports
import os
import json
import pickle
import joblib
import logging
import traceback

# Internal imports
from auxiliary.util.global_constants import NODE_L1
from auxiliary.util.global_constants import _ENC_EXT_L1, _CFG_EXT_L1
from auxiliary.util.global_constants import (
    WTS_PATH,
    CFG_PATH,
    ENC_PATH,
    SCL_ENC_PATH,
    LBL_ENC_PATH,
    KW_VEC_PATH
)
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

from scoring.L1.model_inference import initialize_model, inference

logger = setup_logger(NODE_L1, logging.INFO)
local_flag = True if os.getenv("local") else False

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
model_inf_config = "model_inference.json"


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

    # Paths
    config_path = os.path.join(_FILE_PATH, CFG_PATH)
    print(config_path)
    encoders_path = os.path.join(_FILE_PATH, ENC_PATH)
    print(encoders_path)
    weights_path = os.path.join(_FILE_PATH, WTS_PATH)
    print(weights_path)
    path_to_inference = os.path.join(config_path, model_inf_config)
    print(path_to_inference)
    parent_path_to_encoders = os.path.join(encoders_path, LBL_ENC_PATH)
    print(parent_path_to_encoders)
    parent_path_to_scalers = os.path.join(encoders_path, SCL_ENC_PATH)
    print(parent_path_to_scalers)

    # init model
    model_dict = initialize_model(weights_path)

    # init encoders
    label_encoders_dict = {}
    scalers_dict = {}
    config_dict = dict()

    for r, d, f in os.walk(parent_path_to_encoders):

        for enc in f:
            print(enc)
            key = enc.replace(_ENC_EXT_L1, "")
            key = key.split("-")[0]
            # with open(os.path.join(r, enc), "rb") as f:
            # label_encoders_dict[key] = pickle.load(f)
            label_encoders_dict[key] = joblib.load(os.path.join(r, enc))

    for r, d, f in os.walk(parent_path_to_scalers):
        for scl in f:
            print(scl)
            key = scl.replace(_ENC_EXT_L1, "")
            key = key.split("-")[0]
            # with open(os.path.join(r, scl), "rb") as f:
            # scalers_dict[key] = pickle.load(f)
            scalers_dict[key] = joblib.load(os.path.join(r, scl))

    # init model configs
    for r, d, f in os.walk(config_path):
        for files in f:
            print(files)
            key = files.replace(_CFG_EXT_L1, "")
            config_dict[key] = os.path.join(r, files)

    with open(path_to_inference) as inf:
        inference_cfg = json.load(inf)

    logger.info("Node initialized. Models, scalers, encoders Loaded")

    initialized_objects = {
        "model_dict": model_dict,
        "inference_cfg": inference_cfg,
        "config_dict": config_dict,
        "label_encoders": label_encoders_dict,
        "scalers": scalers_dict,
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
    args_dict = create_arguments_dict(parsed_data, ["data", "lead_id"])
    score_request = args_dict["data"][LEAD_DATA]["type"]

    # data sources
    combined_data = dict()

    lead_data = args_dict["data"][LEAD_DATA]["lead"]
    neustar_data = args_dict["data"].get(NEUSTAR_DATA, {})

    combined_data.update(lead_data)
    combined_data.update(neustar_data["Results"])

    #     node_dict['neustar_match'] = "not_matched" if not bool(neustar_data) else "matched"

    try:

        if (
            score_request == "request_score_for_lead"
            or score_request == "update_score_for_lead"
        ):
            print("MODEL INFERENCE")
            result_dict = inference(node_dict, combined_data, score_request)
        else:
            result_dict = {}
    except Exception as e:

        result_dict = {
            "l1_score": 0.4,
            "l1_likelihood": 1,
            "l1_reason": traceback.format_exc(),
        }

    return result_dict


if __name__ == "__main__":
    pass
