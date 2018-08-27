# -*- coding: utf-8 -*-
'''
@author: davandev
'''
import datetime
        
import logging
import os
import json
import re
import time
import traceback
from datetime import date

import davan.config.config_creator as configuration
import davan.util.cmd_executor as cmd
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class ConnectivityService(ReoccuringBaseService):
    '''
    Starts a re-occuring service that will check connection connectivity"
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.CONNECTIVITY_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.command = "ping -c 1 www.google.com"
        self.time_to_next_timeout = 60
        current_time = datetime.datetime.now().strftime('%H:%M')
        self.connected_at = datetime.datetime.now().strptime(current_time,'%H:%M')
        self.disconnected_at = None
        self.disconnected_result =" 100% packet loss"
        
    def handle_request(self, msg):
        '''
        Received request for the latest speedtest measurements.
        '''
        self.logger.debug("SpeedTest content: " + self.encoded_string)
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, self.encoded_string

    def handle_timeout(self):
        try:
            result = cmd.execute_block(self.command, "ConnectivityTest", True)
            if self.disconnected_result in result:
                self.increment_errors()        
                if self.disconnected_at == None:
                    self.logger.error("Lost internet connectivity")
#                    self.disconnected_at = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                    self.raise_alarm(constants.CONNECTIVITY_SERVICE_NAME, "Warning", "Inget internet")
                    current_time = datetime.datetime.now().strftime('%H:%M')
                    self.disconnected_at = datetime.datetime.now().strptime(current_time,'%H:%M')
                    #self.disconnected_at = time.time()
            else:
                self.increment_invoked()
                if self.disconnected_at != None:
                    self.clear_alarm(constants.CONNECTIVITY_SERVICE_NAME)
                    # Got connection back again'
                    current_time = datetime.datetime.now().strftime('%H:%M')
                    self.connected_at = datetime.datetime.now().strptime(current_time, '%H:%M')
                    #self.connected_at = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                    self.report_down_time()
        except:
            if self.disconnected_at == None:
                self.disconnected_at = datetime.datetime.now().strptime('%H:%M')
#                self.disconnected_at = time.strftime("%Y-%m-%d %H:%M", time.localtime())

            self.logger.error(traceback.format_exc())
            self.increment_errors()        
    
    def report_down_time(self):
        result = "No internet connectivity from ["+ str(self.disconnected_at) +"] to [" + str(self.connected_at) + "]"
        self.logger.warning(result)
        diff = self.connected_at - self.disconnected_at
        if diff.seconds > 70:
            helper.send_telegram_message(self.config, result )
        self.disconnected_at = None
        
    def get_next_timeout(self):
        '''
        Return time to next speed measuring
        '''
        return self.time_to_next_timeout

if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = ConnectivityService("",config)
    current_time = datetime.datetime.now().strftime('%H:%M')
    test.disconnected_at = datetime.datetime.now().strptime(current_time, '%H:%M')
    
    time.sleep(70)
    current_time = datetime.datetime.now().strftime('%H:%M')
    test.connected_at = datetime.datetime.now().strptime(current_time, '%H:%M')
    test.report_down_time()