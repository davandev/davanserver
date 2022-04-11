'''
@author: davandev
'''

import logging
import os
import traceback
import sys
import urllib.request, urllib.parse, urllib.error
import json
import davan.util.helper_functions as helper 
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService
from  pyecowitt.ecowitt import EcoWittListener
from davan.http.service.weather.PoolTempHandle import PoolTempHandle
from davan.http.service.weather.RainHandle import RainHandle
from davan.http.service.weather.MoistureHandle import MoistureHandle

       
class EcowittService(BaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.ECOWITT_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.aqi_active = False
        self.weather_data=[]
        self.is_dry = False
        self.handles = [
            MoistureHandle(config),
            PoolTempHandle(config),
            RainHandle(config)
            ]

    def parse_request(self, data):
        '''
        Parse received request to get interesting parts
        @param msg: received request 
        '''
        data = data.decode('ascii')
        data_copy = data.split('&')
        data_dict = {}
        for item in data_copy:
            items = item.split('=')
            data_dict[items[0]]= items[1]
        
        return data_dict
             
    def handle_request(self, data):
        '''
        '''
        try:
            if not self.is_running:
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, ""


            data_dict = self.parse_request(data)
            eco = EcoWittListener()
            self.weather_data = eco.convert_units(data_dict)
            self.logger.debug("Converted: " + str(self.weather_data) )
            #self.update_status()
            self.report_status()
            
            for handle in self.handles:
                handle.handle_data(self.weather_data)

            self.increment_invoked()
            return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, ""
  
        except:
            self.logger.info("Exception when processing request")
            self.increment_errors()
            traceback.print_exc(sys.exc_info())

    def update_status(self):
        self.logger.debug("Update status")
        try:
            air_quality = self.weather_data['pm25_ch1']
            if air_quality > 12 and self.aqi_active==False:
                self.aqi_active = True
                helper.send_telegram_message(self.config, "Inomhusluften har försämrats ["+str(air_quality)+"]")
            if air_quality <= 12 and self.aqi_active==True:
                self.aqi_active = False
                helper.send_telegram_message(self.config, "Inomhusluften är bra")
        except:
            self.logger.info("Failed to extract value")
            self.increment_errors()
            traceback.print_exc(sys.exc_info())

    def report_status(self):
        '''
        Update fibaro virtual device
        '''
        for key, values in self.config['FIBARO_VD_ECOWITT_MAPPINGS'].items():

            url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ECOWITT_ID'],
                                values[0],
                                str(self.weather_data[key]))
            helper.send_auth_request(url,self.config)

       

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
        _, _, result = self.handle_request("Status")
        data = json.loads(result)
        htmlresult = "<li>Status: " + data["Status"] + "</li>\n"
        htmlresult += "<li>Load: " + data["Load"] + " </li>\n"
        htmlresult += "<li>Battery: " + data["Battery"] + " </li>\n"
        htmlresult += "<li>Time: " + data["Time"] + " </li>\n"
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        return column

    def get_announcement(self):
        '''
        Compose and encode announcement data
        '''
        self.logger.info("Create weather announcement")
        if self.weather_data == None:
            self.logger.warning("Cached service data is none")
            return ""
        
        temp = str(self.weather_data['tempc'])
        temp = temp.replace(".",",")
        announcement = "Just nu är det "
        announcement += temp + " grader ute. "
        return announcement

if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    upspath = "/Ups?text=Status"
    test = EcowittService(None, config)
    test._handle_status_request()
