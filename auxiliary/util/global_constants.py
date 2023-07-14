import os

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
_TMP_FILE_PATH = os.path.join(_FILE_PATH, '..', 'tmp')
os.makedirs(_TMP_FILE_PATH, exist_ok=True)

# Cache memory
os.environ['LRU_CACHE_CAPACITY'] = '1'


# Names of the nodes
NODE_INPUT = "input"
NODE_L1 = "L1_score"
NODE_L2 = "L2_score"
NODE_CONSOLIDATION = "lead_score_consolidation"

# S3 
_BUCKET_NAME = "eip-insurance-useast1"


## Model configs
# L1
L1_MODEL_WTS = 'https://eip-insurance-useast1.s3.amazonaws.com/model_experiments/weights/L2/L2_model.pth' #change after uploading 6 model wts
L1_MODEL_WTS_FILE = L1_MODEL_WTS.split('/')[-1]

#L2
L2_MODEL_WTS = 'https://eip-insurance-useast1.s3.amazonaws.com/model_experiments/weights/L2/L2_model.pth'
L2_MODEL_WTS_FILE = L1_MODEL_WTS.split('/')[-1]