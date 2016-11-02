'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os

import davan.config.config_creator as configuration
import davan.http.service.telldus.tdtool as telldus
from davan.http.service.base_service import BaseService

class TelldusService(BaseService):
    '''
    Telldus service, handling connection towards telldus Live
    Turn on and off of light controlled by telldus Live
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, "telldus", config)
        self.logger = logging.getLogger(os.path.basename(__file__))

    def handle_request(self, msg):
        msg = msg.split('?')
        res = msg[1].split('=')
        self.start(res[0],res[1])
        return 200,""
            
    def start(self, deviceId, action):
        '''
        Light on/off request received from Fibaro system,
        forward to Telldus Live.
        '''
        self.increment_invoked()
        if action == "off":
            action = 2
        elif action == "on":
            action = 1
        else: # turn on Bell
            action = 4 
        
        self.logger.info("DeviceId[" +deviceId+ "] Action:[" + str(action)+"]")
        telldus.doMethod(deviceId, action)
        
if __name__ == '__main__':
    from davan.util import application_logger as app_logger
    config = configuration.create()
    
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = TelldusService()
    telldus.listSensorsAndValues()