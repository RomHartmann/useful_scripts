import logging
import os

logger = logging.getLogger(__name__)

def test_func():
    logger.info("My Secret env is {}".format(os.environ["SECRET_ENV"]))
    logger.info("My ConfigMap env is {}".format(os.environ["CONFIG_MAP"]))
    
    return "Hello World"
