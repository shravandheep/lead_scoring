import os
import logging
from mlaaslib import App, get_config
from main import initialize_node
from main import process as main_process

from auxiliary.util.global_constants import NODE_L1
from auxiliary.util.common_utils import setup_logger

_ENV_TYPE = os.environ.get('ENV_TYPE')
log = setup_logger(NODE_L1, logging.INFO)

# App initialize
node = App('Policy scoring')

# get config
# config = get_config()

# model init
node_dict = initialize_node({})
log.info("initialize_node done")
log.info("ENV_TYPE is : {}".format(_ENV_TYPE))


@node.process
def process(payload):
    """
    Process data from parent nodes. Parent node for Policy is None.

    Parameters :
    ----------
        data : dict of (parent, result) pairs
        node_config : dict of node config
        kwargs : other params

    Returns :
    -------
        res_dic : dict of result
    """
    result_dict = main_process(payload, node_dict)
    return result_dict


if __name__ == "__main__":
    node.start()
