# General imports
import os
import json
import pickle
import joblib
import logging
import traceback
import random

# Internal imports
from auxiliary.util.global_constants import NODE_L1
from auxiliary.util.global_constants import _ENC_EXT_L1, _CFG_EXT_L1
from auxiliary.util.global_constants import (
    WTS_PATH,
    CFG_PATH,
    ENC_PATH,
    SCL_ENC_PATH,
    LBL_ENC_PATH,
    KW_VEC_PATH,
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
    encoders_path = os.path.join(_FILE_PATH, ENC_PATH)
    weights_path = os.path.join(_FILE_PATH, WTS_PATH)
    path_to_inference = os.path.join(config_path, model_inf_config)
    parent_path_to_encoders = os.path.join(encoders_path, LBL_ENC_PATH)
    parent_path_to_scalers = os.path.join(encoders_path, SCL_ENC_PATH)

    # init model
    model_dict = initialize_model(weights_path)

    # init encoders
    label_encoders_dict = {}
    scalers_dict = {}
    config_dict = dict()

    for r, d, f in os.walk(parent_path_to_encoders):
        for enc in f:
            key = enc.replace(_ENC_EXT_L1, "")
            key = key.split("-")[0]
            # with open(os.path.join(r, enc), "rb") as f:
            # label_encoders_dict[key] = pickle.load(f)
            label_encoders_dict[key] = joblib.load(os.path.join(r, enc))

    for r, d, f in os.walk(parent_path_to_scalers):
        for scl in f:
            key = scl.replace(_ENC_EXT_L1, "")
            key = key.split("-")[0]
            # with open(os.path.join(r, scl), "rb") as f:
            # scalers_dict[key] = pickle.load(f)
            scalers_dict[key] = joblib.load(os.path.join(r, scl))

    # init model configs
    for r, d, f in os.walk(config_path):
        for files in f:
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

    try:
        combined_data.update(neustar_data["Results"])
    except KeyError: 
        neustar_data["Results"] = {"Customer Identity Error Code":"", "Individual EKEY":"", "Individual Name First":"", "Individual Name Middle":"", "Individual Name Last":"", "Individual HHID":"", "Individual First Name Match":"", "Individual Middle Name Match":"", "Individual Last Name Match":"", "Individual Address Matches":"", "Individual Phone1 Matches":"", "Individual Phone2 Matches":"", "Individual Email1 Matches":"", "Individual Email2 Matches":"", "Individual DOB Match":"", "Individual DOB":"", "Individual Gender":"", "Individual Gender Match":"", "Individual Person Type":"", "Individual Occupation":"", "Individual Marital Status":"", "Individual Ethnicity":"", "Individual Ethnicity Group":"", "Individual Religion":"", "Individual Country of Origin":"", "Individual Education":"", "Individual Business Owner":"", "Individual Occupation Group":"", "Individual Language Preference Code":"", "Individual Deceased":"", "Appended Phones Error Code":"", "Appended Phones1 Number":"", "Appended Phones1 Phone Confidence":"", "Appended Phones1 Line Type":"", "Appended Phones1 Active":"", "Appended Phones1 Contactability Score":"", "Appended Phones1 Call Window":"", "Appended Phones1 Verification Result Code":"", "Appended Phones1 Phone Usage: Past 12 months":"", "Appended Phones1 DNC":"", "Appended Phones2 Number":"", "Appended Phones2 Phone Confidence":"", "Appended Phones2 Line Type":"", "Appended Phones2 Active":"", "Appended Phones2 Contactability Score":"", "Appended Phones2 Call Window":"", "Appended Phones2 Verification Result Code":"", "Appended Phones2 Phone Usage: Past 12 months":"", "Appended Phones2 DNC":"", "Appended Phones3 Number":"", "Appended Phones3 Phone Confidence":"", "Appended Phones3 Line Type":"", "Appended Phones3 Active":"", "Appended Phones3 Contactability Score":"", "Appended Phones3 Call Window":"", "Appended Phones3 Verification Result Code":"", "Appended Phones3 Phone Usage: Past 12 months":"", "Appended Phones3 DNC":"", "Appended Emails 1 Email Address":"", "Appended Emails 2 Email Address":"", "Appended Emails 3 Email Address":"", "Appended Addresses1 Address Line One":"", "Appended Addresses1 Address Line Two":"", "Appended Addresses1 City":"", "Appended Addresses1 State":"", "Appended Addresses1 Zip5":"", "Appended Addresses1 Zip4":"", "Appended Addresses1 DPC":"", "Appended Addresses1 Type":"", "Appended Addresses1 RBDI":"", "Appended Addresses1 Latitude":"", "Appended Addresses1 Longitude":"", "Appended Addresses1 HHID":"", "Household HHID":"", "Match Type":"", "Number of Persons in Living Unit":"", "Number of Children in Living Unit":"", "Number of Adults in Living Unit":"", "Children: Presence of Child 0-18":"", "Children: Age 0-3":"", "Children: Age 0-3 Score":"", "Children: Age 0-3 Gender":"", "Children: Age 4-6":"", "Children: Age 4-6 Score":"", "Children: Age 4-6  Gender":"", "Children: Age 7-9":"", "Children: Age 7-9 Score":"", "Children: Age 7-9 Gender":"", "Children: Age 10-12":"", "Children: Age 10-12 Score":"", "Children: Age 10-12 Gender":"", "Children: Age 13-15":"", "Children: Age 13-15 Score":"", "Children: Age 13-15  Gender":"", "Children: Age 16-18":"", "Children: Age 16-18 Score":"", "Children: Age 16-18 Gender":"", "Estimated Household Income (Narrow)":"", "Estimated Household Income (Broad band)":"", "Property/Realty: Property indicator":"", "Property/Realty: Home Land Value":"", "Estimated Current Home Value":"", "Property/Realty: Home Total Value":"", "Property/Realty: Median Home  Value":"", "Dwelling Unit Size":"", "Dwelling Type":"", "Homeowner: Combined Homeowner/Renter":"", "Property/Realty: Year Built Confidence":"", "Property/Realty: Year Built":"", "Length of Residence":"", "Presence of credit card":"", "Presence of premium credit card":"", "Mail Responder":"", "Home Business":"", "Activity Date":"", "Census 2010: Tract and block group":"", "Core Based Statistical Areas (CBSA)":"", "Core Based Statistical Area Type":"", "Census: Rural-Urban County Size Code":"", "Median Family Household Income":"", "Household Composition":"", "Household Buying Power Score":"", "Household Net Asset Value":"", "Input Address RBDI":"", "Input Address Lattitude":"", "Input Address Longitude":"", "Input Phones Error Code":"", "Input Phone1 Number":"", "Input Phone1 Phone Confidence":"", "Input Phone1 Line Type":"", "Input Phone1 Active":"", "Input Phone1 Contactability Score":"", "Input Phone1 Call Window":"", "Input Phone1 Verification Result Code":"", "Input Phone1 Phone Usage: Past 12 months":"", "Input Phone1 DNC":"", "Input Phone2 Number":"", "Input Phone2 Phone Confidence":"", "Input Phone2 Line Type":"", "Input Phone2 Active":"", "Input Phone2 Contactability Score":"", "Input Phone2 Call Window":"", "Input Phone2 Verification Result Code":"", "Input Phone2 Phone Usage: Past 12 months":"", "Input Phone2 DNC":"", "Input Email1 Address":"", "Input Email1 Linkage Score":"", "Input Email2 Address":"", "Input Email2 Linkage Score":""}
        combined_data.update(neustar_data["Results"])

    try:
        if (
            score_request == "request_score_for_lead"
            or score_request == "update_score_for_lead"
        ):
            logger.info("Lead scoring invoked")
            result_dict = inference(node_dict, combined_data, score_request)
            result_dict["l1_score"] = round(float(result_dict["l1_score"]), 2)
        else:
            logger.info("Lead scoring not invoked")
            result_dict = {}
    except Exception as e:

        logger.info(f"Error in lead scoring")
        x = round(random.uniform(0.2, 0.4), 2)
        result_dict = {
            "l1_score": x,
            "l1_likelihood": 1,
            "l1_reason": traceback.format_exc(),
            "lead_type": "invalid combination",
            "confidence_scores": {
                "FirstName_Match": 0,
                "LastName_Match": 0,
                "City_Match": 0,
                "StateCode_Match": 0,
                "Phone_Match_Score": 0,
                "Email_Match_Score": 0,
            },
        }

    return result_dict


if __name__ == "__main__":
    pass
