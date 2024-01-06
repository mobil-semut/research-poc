import os
import logging
from dotenv import load_dotenv
load_dotenv('.env')

logger = logging.getLogger(__name__)

class UnconfiguredEnvironment(Exception):
    pass

def getenv(key, default=None, required=False, warn=False):
    env = os.getenv(key)
    if env is not None:
        return env
    if default is not None:
        if warn:
            logger.warn(
                f"Enviroment variable '{key}' is not set, defaulting to {default}")
        return default
    if required:
        raise UnconfiguredEnvironment(
            f"Enviroment variable {key} is not set, but is required !"
        )
    if warn:
        logger.warn(
            f"Enviroment variable '{key}' is not set and has no default !")
