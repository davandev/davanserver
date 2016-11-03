'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
import urllib
from threading import Thread,Event
import davan.config.config_creator as configuration
from davan.http.service.base_service import BaseService

class KeypadAliveService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,"KeypadAliveService", config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()    
        
    def stop_service(self):
        self.logger.info("Stopping service")
        self.event.set()

    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        
        self.logger.info("Starting re-occuring event")

        def loop():
            while not self.event.wait(300): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()

        Thread(target=loop).start()    
        return self.event.set
                                         
    def timeout(self):
        '''
        Timeout received, send a "ping" to key pad, to keep the http server socket on 
        keypad open.
        '''
        self.logger.info("Got a timeout, send keep alive to "+self.config['KEYPAD_URL'])
        try:
            urllib.urlopen(self.config['KEYPAD_URL'])
        except:
            self.logger.info("Failed to connect to keypad")
            pass
        
if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = KeypadAliveService()
    time.sleep(10)
    test.stop_service()
