'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
import urllib2, base64
import re
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class AuthenticationService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.AUTH_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.ok_rsp = 200
        self.nok_rsp = 401
        self.reg_exp_arm = re.compile(r'\/authenticate\?action=([A-Za-z]+)')
        self.reg_exp_disarm = re.compile(r'\/authenticate\?action=(.+?)\&pin=([0-9]+)')

    # Implementation of BasePlugin abstract methods        
    def handle_request(self, msg):
        self.increment_invoked()
        response_code, result = self.start(msg)
        return response_code, result

    def parse_request(self,msg):
        self.logger.info("Parse request:" + msg)
        match = self.reg_exp_disarm.search(msg)
        if match:
            return match.group(1), match.group(2)

        match = self.reg_exp_arm.search(msg)
        if match:
            return match.group(1), None
        
        return None, None
    
    def authenticate_user(self, pin):
        if self.config['USER_PIN'].has_key(pin):
            return self.config['USER_PIN'][pin]
        return None
        
    def start(self, msg):
        '''
        Recevied request from Android keypad system to authenticate
        user, arm/disarm alarm..
        '''
        
        self.logger.info("Received request for authentication ["+ msg + "]")
        action, pin = self.parse_request(msg)
        if action and not pin:
            if action == "armAlarm" or action == "armSkalskydd":
                self.perform_security_action(action)
                return self.ok_rsp, ""
        
        elif action and pin:
            user = self.authenticate_user(pin)
            if user == None:
                return self.nok_rsp, ""            
            else:
                self.perform_security_action(action)
                return self.ok_rsp, "{user:" + user + "}"
        
    
    def perform_security_action(self, action):
        ''' 
        '''  
        
        if action in self.config:
            self.logger.debug("Action:" + self.config[action])
            request = urllib2.Request(self.config[action])
            base64string = base64.encodestring(self.config["FIBARO_USER_NAME"] + ":" + 
                                               self.config["FIBARO_PASSWORD"])
            request.add_header("Authorization", "Basic %s" % base64string)   
            result = urllib2.urlopen(request)    
            self.logger.info("Result: " + str(result) )
        
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = AuthenticationService()
    test.start("/authenticate?action=armSkalskydd")
