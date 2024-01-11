import requests
import os
import time

# Internal imports
from auxiliary.util.global_constants import _CLOUDFRONT_URL
from auxiliary.util.global_constants import (
    POLICY_WTS,
    POLICY_LBL_ENC,
    POLICY_SCL_ENC,
    L1_VEC,
)
from auxiliary.util.global_constants import (
    WTS_PATH,
    CFG_PATH,
    ENC_PATH,
    SCL_ENC_PATH,
    LBL_ENC_PATH,
    KW_VEC_PATH,
)

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))


for wts in POLICY_WTS:
    endpoint = _CLOUDFRONT_URL + wts
    file_name = wts.split("/")[-1]

    try:
        response = requests.get(endpoint)

        if response.status_code == 404:
            raise Exception("The object does not exist")
        elif response.status_code != 200:
            raise Exception("Unsuccessful Download")

        if response.status_code == 200:
            

            os.makedirs(os.path.join(_FILE_PATH, WTS_PATH), exist_ok=True)
            local_path = os.path.realpath(os.path.join(_FILE_PATH, WTS_PATH, file_name))

            

            with open(local_path, "wb") as f:
                f.write(response.content)

    except Exception as e:
        pass
        

for enc in POLICY_LBL_ENC:
    endpoint = _CLOUDFRONT_URL + enc
    file_name = enc.split("/")[-1]

    try:
        response = requests.get(endpoint)

        if response.status_code == 404:
            raise Exception("The object does not exist")
        elif response.status_code != 200:
            raise Exception("Unsuccessful Download")

        if response.status_code == 200:
            

            os.makedirs(os.path.join(_FILE_PATH, ENC_PATH), exist_ok=True)
            os.makedirs(os.path.join(_FILE_PATH, ENC_PATH, LBL_ENC_PATH), exist_ok=True)

            local_path = os.path.realpath(
                os.path.join(_FILE_PATH, ENC_PATH, LBL_ENC_PATH, file_name)
            )

            with open(local_path, "wb") as f:
                f.write(response.content)

    except Exception as e:
        pass
        

for enc in POLICY_SCL_ENC:
    endpoint = _CLOUDFRONT_URL + enc
    file_name = enc.split("/")[-1]

    try:
        response = requests.get(endpoint)

        if response.status_code == 404:
            raise Exception("The object does not exist")
        elif response.status_code != 200:
            raise Exception("Unsuccessful Download")

        if response.status_code == 200:
            

            os.makedirs(os.path.join(_FILE_PATH, ENC_PATH), exist_ok=True)
            os.makedirs(os.path.join(_FILE_PATH, ENC_PATH, SCL_ENC_PATH), exist_ok=True)

            local_path = os.path.realpath(
                os.path.join(_FILE_PATH, ENC_PATH, SCL_ENC_PATH, file_name)
            )

            

            with open(local_path, "wb") as f:
                f.write(response.content)

    except Exception as e:
        pass
        


for enc in L1_VEC:
    endpoint = _CLOUDFRONT_URL + enc
    file_name = enc.split("/")[-1]

    try:
        response = requests.get(endpoint)

        if response.status_code == 404:
            raise Exception("The object does not exist")
        elif response.status_code != 200:
            raise Exception("Unsuccessful Download")

        if response.status_code == 200:
            

            os.makedirs(os.path.join(_FILE_PATH, ENC_PATH), exist_ok=True)
            os.makedirs(os.path.join(_FILE_PATH, ENC_PATH, KW_VEC_PATH), exist_ok=True)

            local_path = os.path.realpath(
                os.path.join(_FILE_PATH, ENC_PATH, KW_VEC_PATH, file_name)
            )

            

            with open(local_path, "wb") as f:
                f.write(response.content)

    except Exception as e:
        pass
