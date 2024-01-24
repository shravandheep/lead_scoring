# General imports
import os
import logging

# Internal imports
from auxiliary.util.global_constants import NODE_CONSOLIDATION
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

from consolidation_logic import compute_hybrid


logger = setup_logger(NODE_CONSOLIDATION, logging.INFO)
local_flag = True if os.getenv("local") else False


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


logger.info("Node initialized")


def get_likelihood(score):
    if score <= 0.1:
        return 1
    elif score > 0.1 and score <= 0.4:
        return 2
    elif score > 0.4 and score <= 0.7:
        return 3
    elif score > 0.7:
        return 4

    return -1


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

    required_keys = [
        "lead_id",
        "l1_score",
        "l1_reason",
        "l1_likelihood",
        "l2_score",
        "l2_reason",
        "lead_type",
        "confidence_scores",
    ]

    input_keys = [
        "lead_id",
        "l1_score",
        "l1_reason",
        "l1_likelihood",
        "l2_score",
        "l2_reason",
        "time_since_lead_creation",
        "lead_type",
        "data",
        "confidence_scores",
    ]

    parsed_data, packet_id, _ = check_and_unpack_data(data)

    args_dict = create_arguments_dict(parsed_data, ["data"])
    score_request = args_dict["data"][LEAD_DATA]["type"]

    if (
        score_request == "update_score_for_lead"
        or score_request == "request_score_for_lead"
    ):
        logger.info("Lead scoring consolidation invoked")
        args_dict = create_arguments_dict(parsed_data, input_keys)
        l1_score = args_dict["l1_score"]

        if args_dict["l2_score"]:
            l2_score = args_dict["l2_score"]
        else:
            l2_score = 0

        final_score, _, _ = compute_hybrid(
            l1_score, l2_score, args_dict["time_since_lead_creation"]
        )
        final_likelihood = get_likelihood(final_score)

        final_args = dict((k, v) for (k, v) in args_dict.items() if k in required_keys)
        final_score = round(float(final_score), 2)
        logger.info(f"Final score computed: {final_score}")
        result_dict = {
            **final_args,
            "score": final_score,
            "type": score_request,
            "likelihood": final_likelihood,
        }
    else:
        logger.info("Lead scoring consolidation not invoked")
        result_dict = {}

    return result_dict
