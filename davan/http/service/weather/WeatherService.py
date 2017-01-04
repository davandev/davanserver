# -*- coding: utf-8 -*-
'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
import json
import urllib2
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class WeatherService(BaseService):
    '''
    classdocs
    '''
    def __init__(self, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.WEATHER_SERVICE, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
            
    def handle_request(self, msg):
        '''
        '''
        pass

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, id):
        """
        Override and provide gui
        """
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        result = urllib2.urlopen(self.config["WUNDERGROUND_PATH"]).read()
        data = json.loads(result)
        htmlresult = "<li>Temp: " + str(data["current_observation"]["temp_c"]) + "</li>\n"
        htmlresult += "<li>Humidity: " + str(data["current_observation"]["relative_humidity"]) + " </li>\n"
        htmlresult += "<li>Pressure: " + str(data["current_observation"]["pressure_mb"]) + " bar </li>\n"
        htmlresult += "<li>Feels like: " + str(data["current_observation"]["feelslike_c"]) + " </li>\n"
        htmlresult += "<li>Rain: " + str(data["current_observation"]["precip_today_metric"]) + " mm</li>\n"
        htmlresult += "<li>Wind dir: " + str(data["current_observation"]["wind_dir"]) + " </li>\n"
        htmlresult += "<li>Wind degree: " + str(data["current_observation"]["wind_degrees"]) + " </li>\n"
        htmlresult += "<li>Time: " + str(data["current_observation"]["observation_time_rfc822"]) + " </li>\n"
        column = column.replace("<SERVICE_VALUE>", htmlresult)

        return column
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = WeatherService()
    test.handle_request("msg")
