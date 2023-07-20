import os

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
_TMP_FILE_PATH = os.path.join(_FILE_PATH, '..', 'tmp')
os.makedirs(_TMP_FILE_PATH, exist_ok=True)

# Cache memory
os.environ['LRU_CACHE_CAPACITY'] = '1'


# Names of the nodes [This should match the name of the node in the graph]
NODE_INPUT = "input"
NODE_L1 = "l1_model"
NODE_L2 = "l2_model"
NODE_CONSOLIDATION = "lead_consolidation"

# Hardcoded file names
WTS_PATH = 'weights'
ENC_PATH = 'encoders'
CFG_PATH = 'configs'
SCL_ENC_PATH = 'scaler'
LBL_ENC_PATH = 'label_encoders'

# Extensions
_ENC_EXT_L1 = '.pkl'
_WTS_EXT_L1 = '.sav'
_CFG_EXT_L1 = '.json'

_WTS_EXT_L2 = '.pth'

LEAD_DATA = 'lead_data'
NEUSTAR_DATA = 'neustar_data'

LEAD_REQ_SCORE = 'request_score_for_lead'
POLICY_REQ_SCORE = 'request_score_for_policy'

# S3 
_BUCKET_NAME = "eip-insurance-useast1"
_CLOUDFRONT_URL = "https://d10nf2miq8av5z.cloudfront.net/"

## Model weights and configs
# L1
L1_WTS = [
    'model_experiments/weights/L1/not_paid_leads_with_neustar_not_matched.sav',
    'model_experiments/weights/L1/not_paid_leads_with_neustar_matched.sav',
    'model_experiments/weights/L1/paid_leads_with_neustar_not_matched.sav',
    'model_experiments/weights/L1/paid_leads_with_neustar_matched.sav',
    'model_experiments/weights/L1/partner_leads_with_neustar_not_matched.sav',
    'model_experiments/weights/L1/partner_leads_with_neustar_matched.sav'
]

L1_LBL_ENC = [
    'model_experiments/weights/L1/encoders/label_encoders_not_paid.pkl',
    'model_experiments/weights/L1/encoders/label_encoders_paid.pkl',
    'model_experiments/weights/L1/encoders/label_encoders_partner.pkl'
]

L1_SCL_ENC = [
    'model_experiments/weights/L1/encoders/scaler_not_paid.pkl',
    'model_experiments/weights/L1/encoders/scaler_paid.pkl',
    'model_experiments/weights/L1/encoders/scaler_partner.pkl'
]


#L2
L2_MODEL_WTS = ['model_experiments/weights/L2/L2_model.pth']