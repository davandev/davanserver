# -*- coding: utf-8 -*-
'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
import json
import urllib2
import urllib
from threading import Thread, Event
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
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
        self.event = Event()
        self.weather_data = None
        self.is_raining = False
        self.latest_result = ""

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
            while not self.event.wait(240): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()

        Thread(target=loop).start()    
        return self.event.set
            
    def handle_request(self, msg):
        '''
        '''
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML,self.latest_result 

    
    def timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        self.logger.info("Got a timeout, fetch weather")
        try:
            self.latest_result = urllib2.urlopen(self.config["WUNDERGROUND_PATH"]).read()
            self.weather_data = json.loads(self.latest_result)
            self.check_rain()
            self.update_virtual_device()
        except Exception:
            self.logger.error(traceback.format_exc())

            self.increment_errors()
            self.logger.info("Caught exception") 
            pass
    
    def update_virtual_device(self):
        '''
        Update weather virtual device on HC2 
        '''
        self.logger.info("Update virtual device")
        # Build URL to Fibaro virtual device
        pressButton_url = self.config["VD_PRESS_BUTTON_URL"].replace("<ID>", self.config['WEATHER_VD_ID'])
        pressButton_url = pressButton_url.replace("<BUTTONID>", self.config["WEATHER_BUTTON_ID"])

        # Send HTTP request to notify status change
        urllib.urlopen(pressButton_url)

        
    def check_rain(self):
        '''
        Check if it is raining, then notify on telegram
        '''
        self.logger.info("Check if it is raining")
        
        if (self.weather_data["current_observation"]["precip_1hr_metric"] > 0):
            if not self.is_raining:
                self.logger.info("It has started to rain")
                helper.send_telegram_message(self.config, constants.RAIN_STARTED)
                self.is_raining = True

        else:
            if self.is_raining:
                self.logger.info("It has stopped to rain")
                helper.send_telegram_message(self.config, constants.RAIN_STOPPED)
                self.is_raining = False
                 
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
        if self.weather_data == None:
            return column
        else:
            htmlresult = "<li>Temp: " + str(self.weather_data["current_observation"]["temp_c"]) + "</li>\n"
            htmlresult += "<li>Humidity: " + str(self.weather_data["current_observation"]["relative_humidity"]) + " </li>\n"
            htmlresult += "<li>Pressure: " + str(self.weather_data["current_observation"]["pressure_mb"]) + " bar </li>\n"
            htmlresult += "<li>Feels like: " + str(self.weather_data["current_observation"]["feelslike_c"]) + " </li>\n"
            htmlresult += "<li>Rain: " + str(self.weather_data["current_observation"]["precip_today_metric"]) + " mm</li>\n"
            htmlresult += "<li>Wind dir: " + str(self.weather_data["current_observation"]["wind_dir"]) + " </li>\n"
            htmlresult += "<li>Wind degree: " + str(self.weather_data["current_observation"]["wind_degrees"]) + " </li>\n"
            htmlresult += "<li>Time: " + str(self.weather_data["current_observation"]["observation_time_rfc822"]) + " </li>\n"
            column = column.replace("<SERVICE_VALUE>", htmlresult)
        return column
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = WeatherService()
    test.handle_request("msg")
