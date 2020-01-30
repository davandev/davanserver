

import logging
import os
import re

from davan.util import cmd_executor as cmd_executor
LOGGER = logging.getLogger(os.path.basename(__file__))

def get_device_status(config, device):
    LOGGER.debug("get_status")
    id = config["TRADFRI_ID"]
    id_key = config["TRADFRI_ID_KEY"]
    ip = config["TRADFRI_GATEWAY_IP"]
    
    cmd = "coap-client -v 0 -m get -u " + id + " -k " + id_key + " coaps://" + ip + ":5684/15001/" + device
    LOGGER.debug("Cmd["+cmd+"]")
    
    return cmd_executor.execute_block(cmd, "tradfri")

def get_status(config):
    LOGGER.debug("get_status")
    id = config["TRADFRI_ID"]
    id_key = config["TRADFRI_ID_KEY"]
    ip = config["TRADFRI_GATEWAY_IP"]
    cmd = "coap-client -v 0 -m get -u " + id + " -k " + id_key + " coaps://" + ip + ":5684/15001/"
    LOGGER.debug("Cmd["+cmd+"]")
    
    return cmd_executor.execute_block(cmd, "tradfri", return_output=True)

    
def set_state(config, device, state):
    LOGGER.debug("set_state")
    id = config["TRADFRI_ID"]
    id_key = config["TRADFRI_ID_KEY"]
    ip = config["TRADFRI_GATEWAY_IP"]

    cmd = 'coap-client -m put -u ' + id + ' -k ' + id_key +  ' -B 30 coaps://' + ip + ':5684/15001/' + device +' -e \'{ "3311" : [{ "5850" : '+ str(state) +' }] }\''
    LOGGER.debug("Cmd["+cmd+"]")
    
    return cmd_executor.execute_block(cmd, "tradfri")

def get_state(config, device):
    LOGGER.debug("get_state")
    id = config["TRADFRI_ID"]
    id_key = config["TRADFRI_ID_KEY"]
    ip = config["TRADFRI_GATEWAY_IP"]

    cmd = 'coap-client -m get -u ' + id + ' -k ' + id_key +  ' -B 30 coaps://' + ip + ':5684/15001/' + device
    LOGGER.debug("Cmd["+cmd+"]")
    
    rsp = cmd_executor.execute_block(cmd, "tradfri", return_output=True)
    LOGGER.debug("RSP["+rsp+"]")
    reg_exp = re.compile(r'5850\":(.+?),\"5851')
    match = reg_exp.search(rsp)
    if match:
        LOGGER.debug("Matching:" + str(match.group(1)))
        return match.group(1)
    return -1