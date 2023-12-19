import pandas as pd


def split_and_create_dict(data):
    if data == "null":
        return None  # Return None for null values
    values = data.split("|")[:8]
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
    return dictionary


def extract_value_all(row):
    if row["call_window"] is not None:
        day_name = row["Created_DAY"]
        return row["call_window"].get(day_name, None)
    return None


def extract_value_overall(row):
    if row["call_window"] is not None:
        day_name = "overall"
        return row["call_window"].get(day_name, None)
    return None


def calculate_call_window_difference(row):
    expected_window = row["Expected_Call_Window"]
    actual_window = row["Actual_Call_Window"]

    if expected_window == 0:
        return None
    elif expected_window == actual_window:
        return 0
    else:

        diff = min(
            abs(expected_window - actual_window),
            (abs(abs(actual_window - expected_window) - 12)),
        )
        return abs(diff)


def calculate_combined_score(row):
    daywise_diff = row["Daywise_window_diff"]
    overall_diff = row["Overall_window_diff"]

    if pd.isna(daywise_diff) or pd.isna(overall_diff):
        return np.nan

    daywise_score = max(0, 1 - daywise_diff / 12)
    overall_score = max(0, 1 - overall_diff / 12)

    combined_score = (weight_daywise * daywise_score) + (weight_overall * overall_score)

    return combined_score


def get_call_window_score(df_leads_neu):

    df_leads_neu["call_window"] = df_leads_neu["Input Phone1 Call Window"].apply(
        split_and_create_dict
    )
    df_leads_neu["CreatedDate"] = pd.to_datetime(df_leads_neu["CreatedDate"])
    df_leads_neu["Created_DAY"] = df_leads_neu["CreatedDate"].dt.day_name()

    df_leads_neu["Expected_Call_Window"] = df_leads_neu.apply(extract_value_all, axis=1)
    df_leads_neu["Overall_Call_Window"] = df_leads_neu.apply(
        extract_value_overall, axis=1
    )

    df_leads_neu["Actual_Call_Window"] = (
        df_leads_neu["CreatedDate"].dt.hour / 2
    ).astype(int) + 1
    df_leads_neu["Daywise_window_diff"] = df_leads_neu.apply(
        calculate_call_window_difference, axis=1
    )

    weight_daywise = 0.7
    weight_overall = 0.3

    df_leads_neu["Call_window_score"] = df_leads_neu.apply(
        calculate_combined_score, axis=1
    )
    return df_leads_neu["Call_window_score"]


def score_boost(score, data, selected_model):

    source_type = selected_model

    with open("data_cpo.json", "r") as json_file:
        data_cpo = json.load(json_file)

    if campaign_id:
        campaign_id = data["CampaignID__c"]
        cpo_score = data_cpo.get()
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

    call_score = get_call_window_score(data)
    final_score = score * 0.67 + call_score * 0.33

    return final_score
