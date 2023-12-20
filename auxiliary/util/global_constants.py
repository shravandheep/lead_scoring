import os

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
_TMP_FILE_PATH = os.path.join(_FILE_PATH, "..", "tmp")
os.makedirs(_TMP_FILE_PATH, exist_ok=True)

# Cache memory
os.environ["LRU_CACHE_CAPACITY"] = "1"


# Names of the nodes [This should match the name of the node in the graph]
NODE_INPUT = "input"
NODE_L1 = "l1_model"
NODE_L2 = "l2_model"
NODE_POLICY = "policy_model"
NODE_CONSOLIDATION = "lead_consolidation"

# Hardcoded file names
WTS_PATH = "weights"
ENC_PATH = "encoders"
CFG_PATH = "configs"
SCL_ENC_PATH = "scaler"
LBL_ENC_PATH = "label_encoders"
KW_VEC_PATH = "vectoriser"

# Extensions
_ENC_EXT_L1 = ".joblib"
_WTS_EXT_L1 = ".sav"
_CFG_EXT_L1 = ".json"

_ENC_EXT_POLICY = ".joblib"
_WTS_EXT_POLICY = ".sav"
_CFG_EXT_POLICY = ".json"

_WTS_EXT_L2 = ".pt"
_ENC_EXT_L2 = ".joblib"

LEAD_DATA = "lead_data"
NEUSTAR_DATA = "neustar_data"

LEAD_REQ_SCORE = "request_score_for_lead"
LEAD_UPD_SCORE = "update_score_for_lead"
POLICY_REQ_SCORE = "request_score_for_policy"

# S3
_BUCKET_NAME = "eip-insurance-useast1"
_CLOUDFRONT_URL = "https://d10nf2miq8av5z.cloudfront.net/"

# Dynamo
HISTORY_TABLE = "eip_history_table"
DYNAMO_REGION = "us-east-1"
HISTORY_TABLE_PARTITION_KEY = "leadID"

## Model weights and configs
# L1
L1_WTS = [
    "model_experiments/weights/L1/paid_model_xgb.sav",
    "model_experiments/weights/L1/not_paid_model_xgb.sav",
    "model_experiments/weights/L1/partner_model_xgb.sav",
]

L1_LBL_ENC = [
    "model_experiments/weights/L1/encoders/paid_encoder_obj-2.joblib",
    "model_experiments/weights/L1/encoders/seo_encoder_obj-2.joblib",
    "model_experiments/weights/L1/encoders/partner_encoder_obj-2.joblib",
]

L1_SCL_ENC = [
    "model_experiments/weights/L1/encoders/paid_scaler_obj.joblib",
    "model_experiments/weights/L1/encoders/seo_scaler_obj.joblib",
    "model_experiments/weights/L1/encoders/partner_scaler_obj.joblib",
]
L1_VEC_ENC = [
    "model_experiments/weights/L1/encoders/count_vectorizer.joblib",
    "model_experiments/weights/L1/encoders/tfidf_vectorizer.joblib",
]
L1_VEC = [
    "model_experiments/weights/L1/encoders/tfidf_vectorizer.joblib",
    "model_experiments/weights/L1/encoders/count_vectorizer.joblib",
]


# L2
L2_MODEL_WTS = ["model_experiments/weights/L2/lstm_wts_v3.1_champ.pt"]
L2_SCL_ENC = ["model_experiments/encoders/L2/encoders/scalers_dict.joblib"]

# POLICY
POLICY_WTS = [
    "model_experiments/weights/Policy/paid_model_xgb.sav",
    "model_experiments/weights/Policy/not_paid_model_xgb.sav",
    "model_experiments/weights/Policy/partner_model_xgb.sav",
]

POLICY_LBL_ENC = [
    "model_experiments/weights/Policy/encoders/paid_encoder_obj-2.joblib",
    "model_experiments/weights/Policy/encoders/not_paid_encoder_obj-2.joblib",
    "model_experiments/weights/Policy/encoders/partner_encoder_obj-2.joblib",
]

POLICY_SCL_ENC = [
    "model_experiments/weights/Policy/encoders/paid_scaler_obj-2.joblib",
    "model_experiments/weights/Policy/encoders/not_paid_scaler_obj-2.joblib",
    "model_experiments/weights/Policy/encoders/partner_scaler_obj-2.joblib",
]
