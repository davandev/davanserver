'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
import urllib
from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class KeypadAliveService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.KEYPAD_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()    
        self.connected = False
        
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
        Timeout received, send a "ping" to key pad, send telegram message if failure.
        '''
        self.logger.info("Got a timeout, send keep alive to "+self.config['KEYPAD_URL'])
        try:
            urllib.urlopen(self.config['KEYPAD_URL'])
            self.maybe_send_update(True)
        except:
            self.increment_errors()
            self.logger.info("Failed to connect to keypad")
            self.maybe_send_update(False)
            
    
    def maybe_send_update(self, state):
        
        if self.connected == True and state == False:
            self.connected = False
            for chatid in self.config['CHATID']:
                url = config['TELEGRAM_PATH'].replace('<CHATID>', chatid) + constants.KEYPAD_NOT_ANSWERING
                urllib.urlopen(url)
        elif self.connected ==False and state == True:
            self.connected = True
            for chatid in self.config['CHATID']:
                url = config['TELEGRAM_PATH'].replace('<CHATID>', chatid) + constants.KEYPAD_ANSWERING
                urllib.urlopen(url)

if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = KeypadAliveService()
    time.sleep(10)
    test.stop_service()
