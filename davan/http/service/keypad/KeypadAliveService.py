'''
@author: davandev
'''

import logging
import os
import urllib
from threading import Thread,Event
from datetime import datetime
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.http.service.base_service import BaseService

class KeypadAliveService(BaseService):
    '''
    Check if keypad is still running by sending a http request towards the keypad
    if there is no response from the keypad then a telegram message is sent.
    Re-occuring event every 5th minute 
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.KEYPAD_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()    
        self.connected = False
        self.connected_at =""
        self.disconnected_at = ""
        
    def stop_service(self):
        '''
        Stop the service
        '''
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
        '''
        Send telegram message if state has changed
        @param state, current state of keypad
        '''
        n = datetime.now()
        currentTime = format(n,"%H:%M")
        
        if self.connected == True and state == False:
            self.logger.info("Keypad state changed: False") 
            self.connected = False
            self.disconnected_at = currentTime
            helper.send_telegram_message(self.config, constants.KEYPAD_NOT_ANSWERING)

        elif self.connected ==False and state == True:
            self.logger.info("Keypad state changed : True") 
            self.connected = True
            self.connected_at = currentTime
            self.disconnected_at = ""
            helper.send_telegram_message(self.config, constants.KEYPAD_ANSWERING)
    
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        html = "<li>Connected: " + str(self.connected) + " </li>\n"
        html += "<li>Ok at: " + str(self.connected_at) + " </li>\n"
        html += "<li>Failed at: " + str(self.disconnected_at) + " </li>\n"
        column = column.replace("<SERVICE_VALUE>", html)
        return column
    
if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = KeypadAliveService()
    time.sleep(10)
    test.stop_service()
