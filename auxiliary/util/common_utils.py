"""
Common utils
"""

# General imports
import os
import boto3
import copy
import logging

from boto3.dynamodb.conditions import Key

# Internal imports
from auxiliary.util import global_constants as GConst

# to handle the timeout configuration through an env variable
_ENV_TYPE = os.environ.get("ENV_TYPE")
local_flag = True if os.getenv("local") else False


class DynamoUtils:
    def __init__(self, table):
        """
        Params init
        """
        self.dynamodb = boto3.resource("dynamodb", region_name=GConst.DYNAMO_REGION)
        self.table = self.dynamodb.Table(table)

    def query_by_partition_key(self, partition_key, value):
        key_condition_expression = Key(partition_key).eq(value)

        # Query the table
        response = self.table.query(KeyConditionExpression=key_condition_expression)

        # Return the result
        return response["Items"]


def setup_logger(name, level):
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=level,
    )
    logger = logging.getLogger(name)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.propagate = True  # remove this if you want to turn off logging
    logger.disabled = local_flag  # Make this True if you want to turn off logging

    return logger


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
        raise TypeError(
            "Input to node not of type dict, it is of type {}".format(type(data))
        )

    parsed_data = {}

    packet_id = data["packet_id"]
    graph_id = data["graph_id"]
    data = data["payload"]

    for parent_node, result in data.items():
        try:
            result = result.get("result", "{}")
            parsed_data[parent_node] = copy.deepcopy(result)
        except:
            raise ValueError("JSON Decode error")

    log.info("GRAPH ID: {}".format(graph_id))
    log.info("PACKET ID: {}".format(packet_id))
    #     log.info("INPUT PAYLOAD: {}".format(parsed_data))

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
                raise KeyError(
                    "The key {} already exists. Ensure you do not duplicate keys across parent nodes".format(
                        key
                    )
                )
            arguments_dict[key] = value

    # Ensure required keys from parent nodes are all present
    if len(set(input_required_args) - set(arguments_dict.keys())) != 0:
        raise KeyError(
            "Following required keys from parent not present - {}".format(
                set(input_required_args) - set(arguments_dict.keys())
            )
        )

    return arguments_dict


log = setup_logger(__name__, logging.INFO)
