'''
@author: davandev
'''

import logging
import os
import traceback
from threading import Thread,Event

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService
import urllib2

class AnnouncementsService(BaseService):
    '''
    Monitor active scenes on Fibaro system, in some cases
    scenes that should always be running are stopped.
    Check status of each active scene and start it if stopped. 
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.ANNOUNCEMENT_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()
        self.daily_ordsprak = "http://www.knep.se/dagens/ordsprak.xml"
        self.daily_gata = "http://www.knep.se/dagens/gata.xml"

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
            while not self.event.wait(60): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()

        Thread(target=loop).start()    
        return self.event.set
                                         
    def timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        self.logger.info("Got a timeout, play announcements")
        try:
            quote = self.fetch_quote()
            tts = __builtin__.davan_services.get_service(constants.TTS_SERVICE_NAME)
            tts.start(quote)
            
        except Exception:
            self.logger.error(traceback.format_exc())

            self.increment_errors()
            self.logger.info("Caught exception") 
            pass

    def fetch_quote(self):
        '''
        Fetch quote from dagenscitat.nu 
        @return the result
        '''
        self.logger.info("Fetching quote")
        quote = urllib2.urlopen("http://www.dagenscitat.nu/citat.js").read()

        quote = quote.split("<")[1]
        result = quote.split(">")[1]

        return result

if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = AnnouncementsService()