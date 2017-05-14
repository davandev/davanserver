# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
import time
import urllib2

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.timer_functions as timer_functions
import davan.util.helper_functions as helper_functions
from davan.util import application_logger as app_logger
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class DailyQuoteService(ReoccuringBaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')

    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.QUOTE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.quote_url = "http://www.dagenscitat.nu/citat.js"
        # Number of seconds until next event occur
        self.time_to_next_event = 25
        # Todays calendar events
        self.today_quote = None
                            
    def handle_timeout(self):
        '''
        Fetch quote from dagenscitat.nu 
        '''
        self.logger.info("Fetching quote")
        quote = urllib2.urlopen(self.quote_url).read()
        quote = quote.split("<")[1]
        self.today_quote = quote.split(">")[1]

    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        if self.today_quote == None: # First time timeout after 30 s.
            return self.time_to_next_event
        
        self.time_to_next_event = timer_functions.calculate_time_until_midnight()
        self.logger.info("Next timeout in " + str(self.time_to_next_event) +  " seconds")
        return self.time_to_next_event
        
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
            return ReoccuringBaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        quote = self.quote_url
        column  = column.replace("<SERVICE_VALUE>", quote)

        return column

    def get_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        result = "Dagens citat. "
        result += self.today_quote
    
        return helper_functions.encode_message(result)

if __name__ == '__main__':
    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = DailyQuoteService()
    test.start()
