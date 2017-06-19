# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
from datetime import *

import davan.util.constants as constants
import davan.util.timer_functions as timer_functions
import davan.util.helper_functions as helper_functions
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class ScaleService(ReoccuringBaseService):
    '''
    classdocs
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.SCALE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.time_to_next_event = 0
        
    def handle_timeout(self):
        '''
        Calculate sun movements 
        '''
        self.logger.info("starting tv service")
        
    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        if self.set == None: # First time timeout after 30 s.
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
        
        column  = column.replace("<SERVICE_VALUE>", "")

        return column

    def get_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        return helper_functions.encode_message("")