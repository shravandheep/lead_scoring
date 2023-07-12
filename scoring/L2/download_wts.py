import requests
import os

# Internal imports
from auxiliary.util.global_constants import L2_MODEL_WTS

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
WTS_PATH = 'weights'

try:
    response = requests.get(L2_MODEL_WTS)
    
    if response.status_code == 404:
        raise Exception("The object does not exist")
    elif response.status_code != 200:
        raise Exception("Unsuccessful Download")

    if response.status_code == 200:
        print('Weights downloaded successfully. Proceeding to saving the L2 weights locally')
            
        os.makedirs(os.path.join(_FILE_PATH, WTS_PATH), exist_ok=True)
        file_name = L2_MODEL_WTS.split('/')[-1]
        local_path = os.path.realpath(os.path.join(_FILE_PATH, WTS_PATH, file_name))
        
        print('Local path :', local_path)

        with open(local_path, 'wb') as f:
            f.write(response.content)

except Exception as e:
    print("Model wts download failed: ", e)