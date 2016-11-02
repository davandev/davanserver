# -*- coding: utf-8 -*-
'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
from threading import Thread,Event

import davan.config.config_creator as configuration
from davan.http.service.base_service import BaseService
import davan.util.cmd_executor as cmd

class SpeedtestService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, "speedtest", config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()
        
    def stop_service(self):
        self.logger.info("Stopping service")
        self.event.set()
                
    def handle_request(self, msg):
        '''
        Received request for speedtest statistics.
        '''
        self.increment_invoked()
        self.logger.debug("Recevied speedtest service request")
        f = open(self.config['SPEED_TEST_RESULT'])
        content = f.read()
        f.close()
#
        self.logger.debug("SpeedTest content: " + content)
        return 200, content
    
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
        Timeout received, iterate all active scenes to check that they are running.
        '''
        self.logger.info("Got a timeout, fetch internet speed")
        cmd.execute(self.config['SPEED_TEST_FILE'], "Speedtest")

if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = SpeedtestService(config)
    time.sleep(30)
    test.stop_service()