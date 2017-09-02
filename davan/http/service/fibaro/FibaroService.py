'''
@author: davandev
'''

import logging
import os
import json
import urllib
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService


class FibaroService(ReoccuringBaseService):
    '''
    Monitor active scenes on Fibaro system, in some cases
    scenes that should always be running are stopped.
    Check status of each active scene and start it if stopped. 
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.FIBARO_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.alarmStatus = {'Skalskydd':"-",'Alarm':'-','Garden':'-'}
        self.memory = {'Cache':"-",'Used':'-','Buffer':'-','Free':'-'}
        self.storage = {'System':"-",'Recovery':'-'}
        
        
    def get_next_timeout(self):
        return self.config['FibaroTimeout']
                                             
    def handle_timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        try:
            #Check alarmstate
            #Check cpu/mem
            #http://192.168.2.54/api/diagnostics
            #http://192.168.2.54/api/devices?id=69
            self.fetch_alarm_status()
            self.print_status()
            #self.fetch_diagnostics()
            
        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            self.logger.info("Caught exception") 
            pass
    
    def fetch_diagnostics(self):
        result = urllib.urlopen(self.config['FIBARO_API_ADDRESS'] + "diagnostics")
        res = result.read()
        data = json.loads(res)
#        for key, value in data.iteritems():
#            self.logger.info("key:"+str(key)+" value:"+str(value))
#            if key == "memory":
#                for k, v in value.iteritems():
                    
            
    def fetch_alarm_status(self):
        result = urllib.urlopen(self.config['FIBARO_API_ADDRESS'] + "devices?id=" + self.config['FibaroVirtualDeviceId'])
        res = result.read()
        data = json.loads(res)
        for key, value in data.iteritems():
            if key == "properties":
                for k, v in value.iteritems():
                    if k  == "ui.Label1.value":
                        self.alarmStatus["Skalskydd"] = str(v)
                    elif k == "ui.Label2.value":
                        self.alarmStatus["Alarm"] = str(v)
                    elif k == "ui.Label5.value":
                        self.alarmStatus["Garden"] = str(v)

    def print_status(self):
        self.logger.info(str(self.alarmStatus))
        
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

        result = "<li>Skalskydd: " + str(self.alarmStatus["Skalskydd"]) + " </li>\n"
        result +="<li>Alarm: " + str(self.alarmStatus["Alarm"]) + " </li>\n" 
        result +="<li>Garden: " + str(self.alarmStatus["Garden"]) + " </li>\n"
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = FibaroService()