#!/usr/bin/env python
# -*- coding: utf-8 -*- 
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
import davan.util.helper_functions as helper
from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
import davan.util.helper_functions as helper


class WaterLevelMonitorService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.WATER_LEVEL_MONITOR_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.level = 0
        self.medel = 0
        self.total = 0
        self.iterations = 0        
        
    def get_next_timeout(self):
        return 300
                                             
    def handle_timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        try:
            self.fetch_water_level()
            self.logger.debug("WaterLevel:"+str(self.level))
            self.calculate()
            self.maybe_notify_value()

        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
    
    def calculate(self):
        self.total += self.level
        self.medel = self.total / self.iterations

    def maybe_notify_value(self):
        if self.level <= self.config['WaterLevelMaxLimit']:
            self.logger.info("Water level really high")

        if self.level >= self.config['WaterLevelMinLimit']:
            self.logger.info("Water level below limit")
            #helper.send_telegram_message(self.config, "Luftfuktigheten i badrummet["+str(self.humidity_value)+"], var god och ventilera")
            #msg = "Det är "+str(self.humidity_value)+" procents luftfuktighet i badrummet, sätt på fläkten"
            #self.services.get_service(constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_KITCHEN)
                        
    def fetch_water_level(self):
        '''
        Fetch and parse alarm status
        '''
        self.iterations +=1

        url = "http://192.168.2.29:5000/distance"
        result = urllib.request.urlopen(url)

        res = result.read()
        data = json.loads(res)
        #self.logger.info("data: "+str(data))
        distance = data[0]
        self.level = float(distance['Distance'])
        #self.logger.info("Distance: "+str(self.level))

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def update_virtual_device(self, invoked):
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_PUMP_ID'],
                                self.config['FIBARO_VD_PUMP_MAP']['distance'],
                                str(self.level))
        self.logger.info("Url: "+ url)
        helper.send_auth_request(url,self.config)

    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return ReoccuringBaseService.get_html_gui(self, column_id)

        result = "Water level: " + str(self.level) + "</br>\n"
        result += "Mean value: " + str(self.medel) + "</br>\n"
        result += "Iterations: " + str(self.iterations) + "</br>\n"
        result +="MinLimit: " + str(self.config['WaterLevelMinLimit']) + "</br>\n" 
        result +="MaxLimit: " + str(self.config['WaterLevelMaxLimit']) + "</br>\n" 
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = WaterLevelMonitorService(None, config)
    test.handle_timeout()
