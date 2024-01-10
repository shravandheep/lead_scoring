import os
import sys
import math
import random
import joblib
import json
import numpy as np
import pandas as pd

import torch
from torch.nn.utils.rnn import pad_sequence
from scipy.special import softmax

from auxiliary.util.common_utils import DynamoUtils
from auxiliary.util import global_constants as GConst
from scoring.L2.model_inference import generate_df, model_inference

history_table = DynamoUtils(GConst.HISTORY_TABLE)
weights_path = os.path.dirname(os.path.realpath(__file__))


# Helpers
def get_history_from_dynamodb(lead_id):
    items = history_table.query_by_partition_key(
        GConst.HISTORY_TABLE_PARTITION_KEY, lead_id
    )

    # Only one entry, list of dicts
    items = items[0]
    items.pop(GConst.HISTORY_TABLE_PARTITION_KEY)

    return items


def increasing_function(x):
    return round(math.log(x + 1), 3)


def normalize_list(lst):
    min_value = min(lst)
    max_value = max(lst)
    normalized_lst = [(value - min_value) / (max_value - min_value) for value in lst]
    return normalized_lst


# def initialize_model(wts_path):

#     wts = None

#     for r,d,f in os.walk(wts_path):

#         for weights in f:
#             wts = os.path.join(r, weights)

#     # Initialization

#     model = torch.load(wts)
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#     model.to(device)
#     model.eval()

#     return model


def transform_features(features, node_dict):
    Xp, time_since_lead_creation = generate_df(features, node_dict)

    return Xp, time_since_lead_creation


def do_inference(data, node_dict):
    lead_id = data["lead_id"]
    lead_history_from_dynamodb = get_history_from_dynamodb(lead_id)

    descending = sorted(list(lead_history_from_dynamodb.keys()))

    # Taking the last 30 entries
    keys_to_consider = descending

    all_changes = list()
    _ = [
        all_changes.extend(json.loads(lead_history_from_dynamodb[k])["changes"])
        for k in keys_to_consider
    ]


    Xp, time_since_lead_creation = transform_features(all_changes[:30], node_dict)
