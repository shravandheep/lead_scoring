import pandas as pd
import joblib
import os

from auxiliary.util import global_constants as GConst


_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
model_wts_path = os.path.join(_FILE_PATH, GConst.L2_MODEL_WTS)

# parent_path_to_model_wts = os.path.join(model_wts_path, KW_VEC_PATH)


reverse_field_mapping = {
    "NVMConnect__NextContactTime__c": "NVMConnect__NextContactTime__c",
    "Outbound_Calls__c": "Outbound_Calls__c",
    "Status": "Status",
    "created": "created",
    "Owner": "Owner_changes",
    "Phone": "Phone_changes",
    "MobilePhone": "Phone_changes",
    "Original_Phone_Number__c": "Phone_changes",
    "Other_Phone__c": "Phone_changes",
    "Email": "Phone_changes",
    "MiddleName": "Detail_changes",
    "LastName": "Detail_changes",
    "FirstName": "Detail_changes",
    "Birthdate__c": "Detail_changes",
}


reqd_cols = [
    "TIMEDIFF",
    "TIMESINCELEADCREATION",
    "TIME_TO_OUTBOUND_CALL",
    "TIMETONEXTCALL",
    "Cumulative_NVMConnect__NextContactTime__c",
    "Cumulative_Outbound_Calls__c",
    "Cumulative_Owner_changes",
    "Cumulative_Phone_changes",
    "Cumulative_Detail_changes",
    "Status_Attempting",
    "Status_Boberdoo",
    "Status_Nurturing",
]

ordinal_feat_standardize = [
    "TIMESINCELEADCREATION",
    "TIMEDIFF",
    "TIME_TO_OUTBOUND_CALL",
    "TIMETONEXTCALL",
]
ordinal_feat_normalize = [
    "Cumulative_NVMConnect__NextContactTime__c",
    "Cumulative_Outbound_Calls__c",
    "Cumulative_Owner_changes",
    "Cumulative_Phone_changes",
    "Cumulative_Detail_changes",
]


def Ordinal_FeatEngg(lead_history_df_merged_subsetcols, scaler):
    for f in ordinal_feat_standardize + ordinal_feat_normalize:
        encoder = scaler[f]
        lead_history_df_merged_subsetcols[f] = encoder.inverse_transform(
            [lead_history_df_merged_subsetcols[f]]
        )

    return lead_history_df_merged_subsetcols


def generate_time_based_feat(lead_history_df):
    ### TIME DIFFERENCE BETWEEN EVENTS
    lead_history_df["TIMEDIFF"] = (
        lead_history_df["update_time"].diff().dt.total_seconds().fillna(0)
    )

    #### NVM_Next_Contact_time
    NEXTCALL = lead_history_df["field_changed"] == "NVMConnect__NextContactTime__c"
    lead_history_df.loc[NEXTCALL, "new_value"] = pd.to_datetime(
        lead_history_df.loc[NEXTCALL, "new_value"], format="%Y-%m-%dT%H:%M:%S.%f"
    )
    lead_history_df.loc[NEXTCALL, "old_value"] = pd.to_datetime(
        lead_history_df.loc[NEXTCALL, "old_value"], format="%Y-%m-%dT%H:%M:%S.%f"
    )
    lead_history_df.loc[NEXTCALL, "TIMETONEXTCALL"] = (
        lead_history_df[NEXTCALL]["new_value"] - lead_history_df[NEXTCALL]["old_value"]
    )

    ### TIME BETWEEN CALLS
    OUTBOUNDCALLS = lead_history_df["field_changed"] == "Outbound_Calls__c"
    lead_history_df.loc[OUTBOUNDCALLS, "TIME_NEXT_CALL"] = (
        lead_history_df[OUTBOUNDCALLS]["update_time"].diff().dt.total_seconds()
    )

    ### TIME SINCE LEAD CREATION
    lead_history_df["TIMESINCELEADCREATION"] = lead_history_df["TIMEDIFF"].cumsum()
    return lead_history_df, lead_history_df["TIMESINCELEADCREATION"]


def generate_sequences(X):
    min_sequence_length = 1
    features = X.values
    number_of_sequences = len(features)
    max_length_events = 30
    X_ = []

    for i in range(min_sequence_length, number_of_sequences):
        sequence = torch.tensor(
            features[min_sequence_length - 1 : i], dtype=torch.float
        )
        sequence = torch.nn.functional.pad(
            sequence, pad=(0, 0, 0, max(0, max_length_events - sequence.size(0)))
        )
        X_.append(sequence)

    Xp_ = pad_sequence(X_, batch_first=True)

    return Xp_


def generate_df(lead_history, node_dict):
    lead_history_df = pd.DataFrame(lead_history)
    lead_history_df["field_changed"] = lead_history_df["field_changed"].map(
        reverse_field_mapping
    )
    lead_history_df["update_time"] = pd.to_datetime(lead_history_df["update_time"])

    lead_history_df, time_since_lead_creation = generate_time_based_feat(
        lead_history_df
    )  ### time based

    ### one hot encoding fields
    lead_history_df_not_status = lead_history_df[
        lead_history_df["field_changed"] != "Status"
    ]
    lead_history_df_not_status = pd.concat(
        [
            lead_history_df_not_status,
            pd.get_dummies(lead_history_df_not_status["field_changed"]),
        ],
        axis=1,
    )
    lead_history_df = pd.concat(
        [
            lead_history_df_not_status,
            lead_history_df[lead_history_df["field_changed"] == "Status"],
        ],
        axis=0,
    ).sort_values(by=["update_time"])

    ### creating dummy fields
    others_ = set(reverse_field_mapping.values()) - set(lead_history_df.columns)
    for cols in others_:
        lead_history_df[cols] = None

    lead_history_df_merged_ = pd.concat(
        [
            lead_history_df,
            lead_history_df[list(set(reverse_field_mapping.values()))]
            .cumsum(axis=0)
            .add_prefix("Cumulative_"),
        ],
        axis=1,
    )

    ### one hot encoding Status changes
    STATUS = lead_history_df_merged_["field_changed"] == "Status"
    lead_history_df_merged_.loc[STATUS, "Status"] = lead_history_df_merged_.loc[
        STATUS, "new_value"
    ]
    lead_history_df_merged_["Status"] = (
        lead_history_df_merged_["Status"].fillna(method="ffill").fillna("New")
    )

    lead_history_df_merged_ = pd.concat(
        [
            lead_history_df_merged_,
            pd.get_dummies(lead_history_df_merged_["Status"]).add_prefix("Status_"),
        ],
        axis=1,
    )

    ### creating dummy fields
    others_ = set(reqd_cols) - set(lead_history_df_merged_.columns)
    for cols in others_:
        lead_history_df_merged_[cols] = None

    lead_history_df_merged_subsetcols = lead_history_df_merged_[reqd_cols].fillna(0)

    X = Ordinal_FeatEngg(
        lead_history_df_merged_subsetcols, node_dict["scalers"]["scalers_dict"]
    )

    Xp_ = generate_sequences(X)  ### model input

    return Xp_, time_since_lead_creation


def initialize_model(wts_path):
    all_wts = []
    model_dict = {}

    for r, d, f in os.walk(wts_path):
        for weights in f:
            all_wts.append(os.path.join(r, weights))

    for wt in all_wts:
        model_name = wt.split("/")[-1].replace(_WTS_EXT_L2, "")
        model = torch.load(wt)
        model_dict[model_name] = model

    return model_dict


def model_inference(Xp_):
    model = torch.load("weights/lstm_wts_v3.1_champ.pt")

    outputs = model(Xp_)
    softmax = torch.nn.Softmax(dim=1)
    probabilities = softmax(outputs)
    probabilities = probabilities.tolist()[-1]

    return probabilities
