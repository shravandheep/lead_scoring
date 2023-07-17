import requests
import os

# Internal imports
from auxiliary.util.global_constants import _CLOUDFRONT_URL
from auxiliary.util.global_constants import L2_MODEL_WTS
from auxiliary.util.global_constants import WTS_PATH

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))

# Internal imports
for wts in L2_MODEL_WTS:

    endpoint = _CLOUDFRONT_URL + wts
    file_name = wts.split('/')[-1]

    try:
        response = requests.get(endpoint)
        
        if response.status_code == 404:
            raise Exception("The object does not exist")
        elif response.status_code != 200:
            raise Exception("Unsuccessful Download")

        if response.status_code == 200:
            print('Weights downloaded successfully. Proceeding to saving the {} weights locally'.format(wts))
                
            os.makedirs(os.path.join(_FILE_PATH, WTS_PATH), exist_ok=True)
            local_path = os.path.realpath(os.path.join(_FILE_PATH, WTS_PATH, file_name))
            
            print('Local path :', local_path)

            with open(local_path, 'wb') as f:
                f.write(response.content)

    except Exception as e:
        print("Model wts {} download failed: ".format(wts), e)