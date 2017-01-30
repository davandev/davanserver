'''
@author: davandev
'''

import logging
import os
import traceback
import sys
import time
import ntplib
import urllib
from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants 
from davan.http.service.base_service import BaseService
from datetime import datetime

class LightSchemaService(BaseService):
    '''
    Notice requires ntplib
    Read configuration
    For each configured room,
    StartTime, StopTime, Interval(week/weekdays/weekend), lightLevel(0-100), deviceId, buttonId, randomTime, virtualDeviceUpdateId
    07.25, 08.55, weekdays, dimmerValue, virtual device, buttonId, 15
    17.25, 20.55, weekdays, dimmerValue, virtual device, buttonId, 0
    Calculate the days light schema at 02:00 
    Push new schemas to each virtual device (for viewing only) 
    Set a timer for next action (closest one)
    at timeout, perform action, restart timer
    TodaysSchema[{Time1:Event(TurnOn, dimmervalue, virtualdevice, buttonId)},
                 {Time2:Event(TurnOn, dimmervalue, virtualdevice, buttonId)}]   
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.LIGHTSCHEMA_SERVICE, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.todaySchema = 
    
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        
        self.logger.info("Starting re-occuring event")


        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        self.logger.info("Day["+d+"]" + "Time["+h+":"+m+"]")
        
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
            self.maybe_send_update(True)
        except:
            self.increment_errors()
            self.maybe_send_update(False)
    
    def sync_time(self):
        '''
        Sync time once a day.
        '''
        try:
            self.logger.info("Attempt to sync time with ntp server")
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org')
            os.system('date ' + time.strftime('%m%d%H%M%Y.%S',time.localtime(response.tx_time)))
        except:
            self.logger.warn('Could not sync with time server.')
            
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
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
