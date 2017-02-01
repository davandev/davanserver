import os
import logging
import urllib
from urllib import quote

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
        
def createFibaroUrl(baseurl, vd_id, labelId, value):
    '''
    Create url to update virtual device on fibaro system 
    @param baseurl, base url to fibaro system
    @param vd_id, virtual device id
    @param labelId, label id of virtual device 
    @param value, value to set.
    '''
    baseurl = baseurl.replace('<DEVICEID>', vd_id)
    baseurl = baseurl.replace('<LABELID>', labelId)
    tempValue = quote(value, safe='') 
    baseurl = baseurl.replace('<VALUE>', tempValue)
    return baseurl

def create_fibaro_url_set_device_value(baseurl, vd_id, value):
    '''
    Create url to update virtual device on fibaro system 
    @param baseurl, base url to fibaro system
    @param vd_id, virtual device id
    @param labelId, label id of virtual device 
    @param value, value to set.
    '''
    baseurl = baseurl.replace('<ID>', vd_id)
    tempValue = quote(value, safe='') 
    baseurl = baseurl.replace('<VALUE>', tempValue)
    return baseurl

def send_telegram_message(config, msg):
    '''
    Send telegram message to all configured receivers
    @param msg message to send
    '''
    #logger.info("Sending telegram msg[ " + msg + "]")
    for chatid in config['CHATID']:
        url = config['TELEGRAM_PATH'].replace('<CHATID>', chatid) + urllib.quote_plus(msg)
        urllib.urlopen(url)
