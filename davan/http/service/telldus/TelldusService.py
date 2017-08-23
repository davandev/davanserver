'''
@author: davandev
'''

import logging
import os
import traceback

import davan.config.config_creator as configuration
import davan.http.service.telldus.tdtool as telldus
import davan.util.constants as constants
from davan.http.service.base_service import BaseService
import davan.util.helper_functions as helper

class TelldusService(BaseService):
    '''
    Telldus service, acts as a proxy between Fibaro system and Telldus Live.
    Forwards on/off triggering of lights from Fibaro system towards Telldus Live
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TELLDUS_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))

    def parse_request(self, msg):
        '''
        Strip received request from uninteresting parts
        Example msg :"telldus?122379=on"
        @param msg, received request
        '''
        msg = msg.split('?')
        res = msg[1].split('=')
        return res[0], res[1]
            
    def handle_request(self, msg):
        '''
        Light on/off request received from Fibaro system,
        forward to Telldus Live.
        '''
        deviceId, action = self.parse_request(msg)
        self.increment_invoked()
        if action == "off":
            action = 2
        elif action == "on":
            action = 1
        elif action == "toggle":
            action = self.get_toggled_device_state(deviceId)
        else: # turn on Bell
            action = 4 
        
        self.logger.info("DeviceId[" +deviceId+ "] Action:[" + str(action)+"]")
        try:
            telldus.doMethod(deviceId, action)
        except:
            self.logger.error("Failed to execute telldus command")
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            helper.send_telegram_message(self.config, "Telldus svarar inte") 

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG
    
    def get_toggled_device_state(self, wanted_deviceId):
        self.logger.info("Find state of device: " + wanted_deviceId)
        response = telldus.listDevicesAndValues()
        for device in response['device']:
            if wanted_deviceId == device['id']:
                if (device['state'] == telldus.TELLSTICK_TURNON):
                    state = telldus.TELLSTICK_TURNOFF
                elif (device['state'] == telldus.TELLSTICK_TURNOFF):
                    state = telldus.TELLSTICK_TURNON
                else:
                    state = 'Unknown state'
        
        self.logger.info("Toggled device state ==" + str(state))
        return state
    
    def list_all_devices(self):
        '''
        List all devices configured in Telldus Live
        '''
        self.logger.info("List all Telldus devices")
        telldus.listDevices()
        
if __name__ == '__main__':
    from davan.util import application_logger as app_logger
    config = configuration.create()
    
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = TelldusService(config)
    test.list_all_devices()
