'''
@author: davandev
'''
# coding: utf-8

import logging
import os
import traceback
import sys
import urllib
import json

import davan.util.helper_functions as helper
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService
import davan.http.service.tradfri.TradfriCommands as commands

class TradfriService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.TRADFRI_SERVICE_NAME, service_provider, config)                    
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.STATES = {"off":0 , "on":1 }
        
    def parse_request(self, msg):
        '''
        @param msg, received request
        '''
        msg = msg.split('?')
        res = msg[1].split('=')
        return res[0], res[1]
            
    def handle_request(self, msg):
        '''
        Light on/off request received from Fibaro system,
        forward to Tradfri gateway.
        '''
        try:
            device_name, action_str = self.parse_request(msg)
            self.increment_invoked()
            
            if device_name == "all":
                action = self.STATES[action_str]
                self.toggle_all_device_states(action)
                return
            elif action_str == "toggle":
                action = self.get_toggled_device_state(device_name)
            else:
                action = self.STATES[action_str]
            
            self.logger.info("Device[" +device_name+ "] Action[" + str(action_str)+"]")
            self.set_state(device_name, action)
        
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            helper.send_telegram_message(self.config, str(e)) 
            self.raise_alarm(constants.TRADFRI_NOT_ANSWERING, "Warning", constants.TRADFRI_NOT_ANSWERING)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG
    
    def set_state(self, device_name, state):
        '''
        Set the state of the device
        @param device_name, name of device
        @param state, the wanted state
        '''
        if device_name not in self.config['TRADFRI_DEVICES'].keys():
            self.logger.error("Cannot find the device_id " + device_name + " in configured devices")
            return
        
        device_id = self.config['TRADFRI_DEVICES'][device_name]
        self.logger.debug("Change state of device " + device_name + "[" + device_id + "]")
        commands.set_state(self.config, device_id, state)

        
    def get_toggled_device_state(self, device_name):
        '''
        Determine the state of the device, then return the opposite state
        @param device_name, name of device
        '''
        if device_name not in self.config['TRADFRI_DEVICES'].keys():
            self.logger.error("Cannot find the device_id " + device_name + " in configured devices")
            return
        
        try:
            device_id = self.config['TRADFRI_DEVICES'][device_name]
            current_state = commands.get_device_status(self.config, device_id)
            
            self.logger.debug("State of " + str(device_name) + " = " + str(current_state))
            
            if current_state == str(self.STATES["on"]):
                return self.STATES["off"]
            return self.STATES["on"]
        except Exception as e:
            self.logger.debug("Caught exception: " + str(e))
            raise Exception("Misslyckades att hämta status för "+ device_name)
            
    def toggle_all_device_states(self, state):
        self.logger.debug("Toggle all device states[" + str(state) + "]")        
    
    def list_all_devices(self):
        '''
        List all devices configured in Tradfri Live
        '''
        self.logger.info("List all Tradfri devices")
        devices = commands.get_status(self.config)
        self.logger.info("Found devices : " + str(devices))
        return devices


        
if __name__ == '__main__':
    from davan.util import application_logger as app_logger
    config = configuration.create()
    
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = TradfriService("",config)
    #test.get_toggle_device_state("KITCHEN")
    devices = test.list_all_devices()
    for device in devices:
        commands.get_device_status(config, device)
    #test.perform("KITCHEN","1")
