"""
Common utils
"""

# General imports
import os
import time
import boto3
import copy
import base64
import logging
import requests

from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Internal imports

# to handle the timeout configuration through an env variable
_ENV_TYPE = os.environ.get('ENV_TYPE')
local_flag = True if os.getenv('local') else False

def setup_logger(name, level):
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=level,
    )
    logger = logging.getLogger(name)
    logger.propagate = True # remove this if you want to turn off logging
    logger.disabled = local_flag # Make this True if you want to turn off logging
     
    return logger

def draw_bbox(img, x, title):
    '''
        Parameters :
    ----------
       img : numpy nd array of image
        x1, y1, x2, y2 : boxe

    '''

    figure, ax = plt.subplots(1)
    plt.title(title)
    
    cv_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    for i in x:
        rect = patches.Rectangle(
            (i[0], i[1]), i[2]-i[0], i[3]-i[1], edgecolor='r', facecolor="none", linewidth=5)
        ax.add_patch(rect)
    plt.imshow(cv_img)


def rect_overlap(x11, y11, x12, y12, x21, y21, x22, y22):
    """
        overlap defined as - area(R1)/area(R2)
        TODO - This suffices for this case - A better measure is IoU

    Parameters :
    ----------
        x11, y11, x12, y12 : vertices of the first rectangle
        x21, y21, x22, y22 : vertices of the second rectangle

    Returns :
    -------
        float measuring overlap
    """
    return float((x12-x11)*(y12-y11)) / ((x22-x21)*(y22-y21))


def check_and_unpack_data(data):
    """
    Validate type and parse. Format for data 

    data = {
          'parent_1': {
              'status': 'STATUS_SUCCESS'/'STATUS_FAILED'/'SKIPPIED',
              'result': result of parent_1 node
          }
          'parent_2': {
              'status': 'STATUS_SUCCESS'/"FAILED"/"SKIPPIED",
              'result': result of parent_2 node
          }
      }

    Parameters :
    ----------
        data : a dict of parent node results in JSON serialized format

    Returns :
    -------
        parsed_data : a dict of de-serialized and verified results
    """

    if not isinstance(data, dict):
        raise TypeError('Input to node not of type dict, it is of type {}'.format(type(data)))

    parsed_data = {}

    packet_id = data["packet_id"]
    graph_id = data["graph_id"]
    data = data["payload"]

    for parent_node, result in data.items():
        try:
            result = result.get("result", '{}')
            parsed_data[parent_node] = copy.deepcopy(result)
        except:
            raise ValueError('JSON Decode error')

    log.info("GRAPH ID: {}".format(graph_id))
    log.info("PACKET ID: {}".format(packet_id))
    log.info("INPUT PAYLOAD: {}".format(parsed_data))

    return parsed_data, packet_id, graph_id


def create_arguments_dict(parsed_data, input_required_args, allow_duplicate_args=[]):
    """
    Create arguments dict

    Parameters :
    ----------
        parsed_data : dict of parent nodes results

    Returns :
    -------
        arguments_dict : flat dictionary from all the parent results
    """

    arguments_dict = {}
    
    for _, result in parsed_data.items():
        for key, value in result.items():
            if key in arguments_dict and key not in allow_duplicate_args:
                raise KeyError("The key {} already exists. Ensure you do not duplicate keys across parent nodes".format(key))
            arguments_dict[key] = value

    # Ensure required keys from parent nodes are all present
    if len(set(input_required_args) - set(arguments_dict.keys())) != 0:
        raise KeyError("Following required keys from parent not present - {}".format(set(input_required_args) - set(arguments_dict.keys())))

    return arguments_dict

log = setup_logger(__name__, logging.INFO)

logging.getLogger('boto3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('s3transfer').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)
