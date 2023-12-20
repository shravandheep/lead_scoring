import os
import logging
from mlaaslib import App, get_config
from main import initialize_node
from main import process as main_process

from auxiliary.util.global_constants import NODE_CONSOLIDATION
from auxiliary.util.common_utils import setup_logger

_ENV_TYPE = os.environ.get("ENV_TYPE")
log = setup_logger(NODE_CONSOLIDATION, logging.INFO)

# App initialize
node = App("L2 scoring")

# get config
# config = get_config()

# model init
node_config = initialize_node({})
log.info("initialize_node done")
log.info("ENV_TYPE is : {}".format(_ENV_TYPE))


@node.process
def process(payload):
    """
    Process data from parent nodes. Parent node for L2 is None.

    Parameters :
    ----------
        data : dict of (parent, result) pairs
        node_config : dict of node config
        kwargs : other params

    Returns :
    -------
        res_dic : dict of result
    """
    result_dict = main_process(payload)
    return result_dict


if __name__ == "__main__":
    node.start()
