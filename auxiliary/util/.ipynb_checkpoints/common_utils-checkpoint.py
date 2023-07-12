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
from auxiliary.util.global_constants import _S3_BASE_LINK, _BUCKET_NAME

# to handle the timeout configuration through an env variable
_ENV_TYPE = os.environ.get('ENV_TYPE')

def setup_logger(name, level):
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=level,
    )
    logger = logging.getLogger(name)
    logger.propagate = True # remove this if you want to turn off logging
    logger.disabled = True # Make this True if you want to turn off logging
     
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


def download_image_using_requests(image_url):

    start_time = time.time()
    response = requests.get(
        image_url,
        timeout=(2.00, 2.00),
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    log.info("Download status code: {}".format(response.status_code))
    response_content = response.content
    log.info("response content length ={}".format(len(response_content)))
    log.info("after requests content time taken ={}".format(time.time() - start_time))

    bytes_p = BytesIO(response_content)
    filesize = bytes_p.getbuffer().nbytes
    log.info("after bytes content time taken ={}".format(time.time() - start_time))
    log.info("bytes length ={}".format(bytes_p.getbuffer().nbytes))

    return bytes_p, filesize

def download_image_using_chunks(image_url, download_time = 20):
    start_time = time.time()
    temp = BytesIO()

    log.info("Downloading using chunks")

    with requests.get(image_url,
                      stream=True,
                      timeout=(4,4), headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }) as r:
        status_code = r.status_code
        r.raise_for_status()

        for chunk in r.iter_content(chunk_size=8192):
            if time.time() - start_time <= download_time:
                temp.write(chunk)
            else:
                raise Exception("Image is taking too long to download")

    log.info("Download status code: {}".format(status_code))

    filesize = temp.getbuffer().nbytes

    log.info("after bytes content time taken ={}".format(time.time() - start_time))
    log.info("bytes length ={}".format(temp.getbuffer().nbytes))

    return temp, filesize

def download_image_using_boto3(image_url):

    start_time = time.time()
    s3_key = image_url.replace(_S3_BASE_LINK, "")
    obj = bucket.Object(s3_key)
    bytes_p = obj.get()["Body"]
    log.info("Time taken to fetch bytes stream from s3: {}".format(time.time() - start_time))

    return bytes_p


def resize_image(cv_img, resize_max_dim):

    start = time.time()
    orig_h = cv_img.shape[0]
    orig_w = cv_img.shape[1]

    if orig_h > resize_max_dim or orig_w > resize_max_dim:
        log.info("Original Image size - {} x {}".format(orig_w, orig_h))
        
        # Case: W >= H
        if orig_w >= orig_h:
            ratio = resize_max_dim / float(orig_w)
            dim = (resize_max_dim, int(orig_h * ratio))
        # Case: H > W
        else:
            ratio = resize_max_dim / float(orig_h)
            dim = int(orig_w * ratio), resize_max_dim

        resized_img = cv2.resize(cv_img, dim, interpolation=cv2.INTER_AREA)
        log.info("Resized Image size - {} x {}".format(resized_img.shape[1], resized_img.shape[0]))
        log.info("Time Taken to resize image: {}".format(time.time() - start))

    else:
        resized_img = cv_img

    return resized_img

def download_image_local(img_path, mode='RGB'):
    
    start_t = time.time()
    filesize = os.path.getsize(img_path)
    img = Image.open(img_path)

    if mode == 'RGB':
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    elif mode == 'RGBA' :
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
        
    orig_h, orig_w = cv_img.shape[:2]

    return cv_img, filesize, orig_w, orig_h
        
def download_get_cv_image(image_url, mode='RGB'):
    start_t = time.time()
    filesize = None
    log.info('ENV_TYPE in function get_cv_image is : {}'.format(_ENV_TYPE))
    log.info('Downloading Images for {}...'.format(_ENV_TYPE))

    is_hosted = image_url.startswith(_S3_BASE_LINK)
    if is_hosted:
        log.info("Trying to download image using boto3...")
        file_stream = download_image_using_boto3(image_url)
        log.info("Image downloaded using boto3 in {}".format(time.time() - start_t))
    else:
        try:
            log.info("Trying to download image using requests")
            file_stream, filesize = download_image_using_chunks(image_url)
            log.info("Image downloaded using requests in {}".format(time.time() - start_t))
        except:
            log.info("Image Download Error")
            raise Exception("Image Download Error")

    try:
        img_f = Image.open(file_stream)
        log.info("img f shape ={}".format(img_f.size))
        log.info("after image open time taken ={}".format(time.time() - start_t))

        img = img_f.convert(mode)
        img_f.close()
        log.info("img shape ={}".format(img.size))
        log.info("after image convert to rgb time taken ={}".format(time.time() - start_t))
        
        if mode == 'RGB':
            cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        elif mode == 'RGBA' :
            cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

        log.info("after image convert to np array time taken ={}".format(time.time() - start_t))
    except:
        raise Exception("Image Download Error")

    orig_h, orig_w = cv_img.shape[:2]

    return cv_img, filesize, orig_w, orig_h


def decode_str_image(str_img):

    decoded_img = cv2.imdecode(np.frombuffer(base64.b64decode(str_img), dtype=np.uint8), flags=0)

    return decoded_img

def get_cv_image(url_or_path, is_path=False, resize=True):
    """
    Download image

    Parameters :
    ----------
        url_or_path : str denoting url or path
        is_path : boolean set to True if url_or_path is path
        resize : boolean set to True if Resizing is required

    Returns :
        resized_img : numpy nd array of resized image in BGR format
        cv_img : numpy nd array of image in BGR format
        filesize : file size of the image
    """
    filesize = None
    
    if not is_path:
        now = time.time()
        log.info('ENV_TYPE in function get_cv_image is : {}'.format(_ENV_TYPE))
        log.info('Downloading Images for {}...'.format(_ENV_TYPE))

        # todo: find a better way to do this (store url in a configs file)
        is_hosted = url_or_path.startswith(_S3_BASE_LINK)
        if is_hosted:
            log.info("Trying to download image using boto3...")
            file_stream = download_image_using_boto3(url_or_path)
            log.info("Image downloaded using boto3 in {}".format(time.time() - now))
        else:
            try:
                log.info("Trying to download image using requests")
                file_stream, filesize = download_image_using_requests(url_or_path)
                log.info("Image downloaded using requests in {}".format(time.time() - now))
            except:
                log.info("Image Download Error")
                raise Exception("Image Download Error")

        now = time.time()
        try:
            img_f = Image.open(file_stream)
            log.info("img f shape ={}".format(img_f.size))
            log.info("after image open time taken ={}".format(time.time() - now))

            img = img_f.convert('RGB')
            img_f.close()
            log.info("img shape ={}".format(img.size))
            log.info("after image convert to rgb time taken ={}".format(time.time() - now))
            
            cv_img = np.array(img)[:, :, ::-1]
            log.info("after image convert to np array time taken ={}".format(time.time() - now))
        except:
            raise Exception("Image Download Error")

    else:
        cv_img = cv2.imread(url_or_path)

    orig_h, orig_w = cv_img.shape[:2]
    log.info("Original Dimensions: {} {}".format(orig_w, orig_h))

    if resize:
        resized_img = resize_image(cv_img, 500) # Hardcoding here since all nodes use 500 as default
    else:
        resized_img = cv_img

    return resized_img, cv_img, filesize


def show_cv_image(img_to_display, title=''):
    """
    display image

    Parameters :
    ----------
        img_to_display : numpy nd array of image
        title : str 

    Returns :
    -------
        None
    """

    import matplotlib.pyplot as plt
    plt.imshow(cv2.cvtColor(img_to_display, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.show()


def show_all(imgs, titles):
    """
    Show multiple images in subplots

    Parameters :
    ----------
        imgs : list of numpy nd array of images
        titles : list of str

    Returns :
    -------
        None
    """

    import matplotlib.pyplot as plt
    if len(imgs) == len(titles):
        fig_size = (15, 10*len(imgs))
        kwargs = dict(figsize=fig_size)
        fig, ax = plt.subplots(1, len(imgs), **kwargs)
        for idx, (img, title) in enumerate(zip(imgs, titles)):
            ax[idx].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ax[idx].set_title(title)
        plt.show()
    else:
        print ('number of images and number of titles not same!')


def imshow_components(labels):
    """
    Create a colored component image

    Parameters :
    ----------
        labels : numpy 2D array of labelled components

    Returns :
    -------
        labeled_img : numpy nd array of the colored components.
    """

    # Map component labels to hue val
    label_hue = np.uint8(179*labels/np.max(labels))
    blank_ch = 255*np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

    # cvt to BGR for display
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

    # set bg label to black
    labeled_img[label_hue == 0] = 0

    return labeled_img


def upload_image_to_s3(pil_image, s3_key, bucket, mode_format = 'JPEG'):

    in_mem_file = BytesIO()
    pil_image.save(in_mem_file, format=mode_format.upper(), quality=100)
    in_mem_file.seek(0)

    s3_client.upload_fileobj(
        in_mem_file,
        bucket,
        s3_key,
        ExtraArgs={
            "ACL": "public-read",
            "ContentType": "image/{}".format(mode_format)
        }
    )


log = setup_logger(__name__, logging.INFO)

# Establish global connection with region and bucket
s3 = boto3.resource("s3", region_name="us-east-1")
s3_client = boto3.client("s3")
bucket = s3.Bucket(_BUCKET_NAME)

logging.getLogger('boto3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('s3transfer').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)
