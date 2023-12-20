import os
import pandas as pd
import json
from datetime import datetime

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))


def calc_diff(actual, expected):
    if expected == 0:
        return 0
    elif expected == actual:
        return 0
    else:
        diff = min(
            abs(expected - actual),
            (abs(abs(actual - expected) - 12)),
        )
        return abs(diff)


def get_call_window_score(input_call_window, created_time):
    created_time = datetime.strptime(created_time, "%Y-%m-%d %H:%M:%S")
    values = input_call_window.split("|")[:8]
    keys = [
        "overall",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    dictionary = {keys[i]: int(value) for i, value in enumerate(values)}
    actual_call_day = created_time.strftime("%A")
    expected_call_window_on_day = dictionary.get(actual_call_day)
    expected_overall_call_window = dictionary.get("overall")
    actual_call_window = int(1 + int(created_time.strftime("%H")) / 2)

    overall_diff = calc_diff(actual_call_window, expected_overall_call_window)
    daywise_diff = calc_diff(actual_call_window, expected_call_window_on_day)

    daywise_score = max(0, 1 - daywise_diff / 12)
    overall_score = max(0, 1 - overall_diff / 12)

    weight_daywise = 0.7
    weight_overall = 0.3

    combined_score = (weight_daywise * daywise_score) + (weight_overall * overall_score)
    return combined_score


def score_boost(score, data, selected_model):
    # data = data.to_dict()

    data = data.to_dict(orient="records")[0]
    source_type = selected_model

    cpo_path = os.path.join(_FILE_PATH, "data_cpo.json")

    with open(cpo_path, "r") as json_file:
        data_cpo = json.load(json_file)

    campaign_id = data["CampaignID__c"]

    if campaign_id:
        cpo_score = data_cpo.get(campaign_id)
        if cpo_score:
            score = score * 0.67 + cpo_score * 0.33

    if source_type == "partner_model":
        score = score * 0.9
    elif source_type == "paid_model":
        score = score * 0.9
    else:
        score = score

    lead_type = data["Type"]
    if lead_type == "Online":
        score = score * 0.9

    created_time = data["CreatedDate"]
    input_call_window = data["Input Phone1 Call Window"]

    if input_call_window != "":
        call_score = get_call_window_score(input_call_window, created_time)
        final_score = score * 0.67 + call_score * 0.33
    else:
        final_score = score

    return final_score
