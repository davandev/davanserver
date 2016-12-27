# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import json
from threading import Thread,Event

import davan.config.config_creator as configuration
import davan.util.cmd_executor as cmd
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class SpeedtestService(BaseService):
    '''
    Starts a re-occuring service that will measure internet speed (Download/Upload/ping)
    Requires speedtest-cli : install with "sudo pip install speedtest-cli"
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.SPEEDTEST_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()
        
    def stop_service(self):
        self.logger.info("Stopping service")
        self.event.set()
                
    def handle_request(self, msg):
        '''
        Received request for the latest speedtest measurements.
        '''
        self.increment_invoked()
        self.logger.debug("Recevied speedtest service request")
        f = open(self.config['SPEED_TEST_RESULT'])
        content = f.read()
        f.close()
#
        self.logger.debug("SpeedTest content: " + content)
        return constants.RESPONSE_OK, content
    
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        self.logger.info("Starting re-occuring event")
        def loop():
            while not self.event.wait(900): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()

        Thread(target=loop).start()    
        return self.event.set

    def timeout(self):
        '''
        Timeout received, start measure internet speed.
        '''
        self.logger.info("Got a timeout, fetch internet speed")
        cmd.execute(self.config['SPEED_TEST_FILE'], "Speedtest")

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_ud):
        """
        Override and provide gui
        """
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_ud))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        ok, result = self.handle_request("")
        data = json.loads(result)
        htmlresult = "<li>Ping: " + str(data["Ping_ms"]) + " ms</li>\n"
        htmlresult += "<li>Download: " + str(data["Download_Mbit"]) + " Mbit</li>\n"
        htmlresult += "<li>Upload: " + str(data["Upload_Mbit"]) + " Mbit</li>\n"
        htmlresult += "<li>Date: " + data["Date"] + " </li>\n"
        
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        
        return column

if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = SpeedtestService(config)
    time.sleep(30)
    test.stop_service()