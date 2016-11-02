import os
import logging

global logger
logger = logging.getLogger(os.path.basename(__file__))

def debug_big(message):
    tmpStr = "\n==============================================================================\n"
    tmpStr += message + "\n"
    tmpStr += "==============================================================================\n"
    logger.info(tmpStr)

def debug_formated(obj):
    if isinstance(obj, dict):
        tmpStr = "\n==============================================================================\n"
        for k, v in sorted(obj.items()):
            tmpStr += u'{0:30} ==> {1:15}'.format(k, v) + "\n"
        tmpStr += "\n==============================================================================\n"
        logger.debug(tmpStr)

    # List or tuple
    elif isinstance(obj, list) or isinstance(obj, tuple):
        for x in obj:
            logger.debug(x)

    # Other
    else:
        print obj