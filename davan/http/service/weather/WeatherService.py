# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import json
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper

from davan.http.service.reoccuring_base_service import ReoccuringBaseService


class WeatherService(ReoccuringBaseService):
    '''
    classdocs
    '''
    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.WEATHER_SERVICE, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.weather_data = None
        self.is_raining = False
        self.latest_result = ""
        self.time_to_next_timeout = 180
        self.forecast  =""
            
    def handle_request(self, msg):
        '''
        Handle received http request 
        @return latest received weather data
        '''
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, self.latest_result 
    
    def handle_timeout(self):
        '''
        Timeout received, fetch weather data from wunderground
        '''
        self.logger.debug("Fetch weather")
        try:
            self.latest_result = urllib.request.urlopen(self.config["WUNDERGROUND_PATH"]).read()
            self.weather_data = json.loads(self.latest_result)
            self.check_rain()
            self.update_virtual_device()
            self.get_forecast()
        except Exception:
            self.logger.error(traceback.format_exc())
            self.logger.debug("Received result ["+ str(self.latest_result) +"]")
            self.increment_errors()
            pass
    
    def get_next_timeout(self):
        '''
        Return time in seconds to next timeout
        '''
        return self.time_to_next_timeout
    
    def update_virtual_device(self):
        '''
        Update weather virtual device on HC2 
        '''
        # Build URL to Fibaro virtual device
        pressButton_url = self.config["VD_PRESS_BUTTON_URL"].replace("<ID>", self.config['WEATHER_VD_ID'])
        pressButton_url = pressButton_url.replace("<BUTTONID>", self.config["WEATHER_BUTTON_ID"])

        # Send HTTP request to notify status change
        urllib.request.urlopen(pressButton_url)
                
    def check_rain(self):
        '''
        Check if it is raining, then notify on telegram
        '''
        current_rain = str(self.weather_data["current_observation"]["precip_1hr_metric"]).strip()
        #self.logger.info("Check if it is raining["+current_rain+"]")
        if not (current_rain == "0.0" or current_rain == "0"):
            if not self.is_raining:
                self.logger.info("It has started to rain")
                helper.send_telegram_message(self.config, constants.RAIN_STARTED)
                self.services.get_service(constants.TTS_SERVICE_NAME).start(
                    constants.RAIN_STARTED,
                    constants.SPEAKER_KITCHEN)
                self.is_raining = True

        else:
            if self.is_raining:
                self.logger.info("It has stopped to rain")
                helper.send_telegram_message(self.config, constants.RAIN_STOPPED)
                self.services.get_service(constants.TTS_SERVICE_NAME).start(
                    constants.RAIN_STOPPED,
                    constants.SPEAKER_KITCHEN)
                self.is_raining = False
    
    def get_forecast(self):
        myweather_sum = self.weather_data['forecast']['txt_forecast']['forecastday']

        for period in myweather_sum:
            if period['period'] == 2:
                myforday = period['title']
                self.forecast = period['fcttext_metric']
                
                
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
        if self.weather_data == None:
            htmlresult = "<li>No weather data available</li>\n"            
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

    def get_announcement(self):
        '''
        Compose and encode announcement data
        '''
        self.logger.info("Create weather announcement")
        if self.weather_data == None:
            self.logger.warning("Cached service data is none")
            return ""
        
        temp = str(self.weather_data["current_observation"]["temp_c"])
        temp = temp.replace(".", ",")
        announcement = "Just nu är det "
        announcement += temp 
        announcement += " grader ute och det känns som "
        temp = str(self.weather_data["current_observation"]["feelslike_c"])
        temp = temp.replace(".", ",")
        announcement += temp + " grader. "
        #self.forecast = self.forecast.replace('°', '')
        #self.logger.info("Dagens prognos: "+ self.forecast)
        #announcement += "Dagens prognos." +self.forecast
        return announcement
                
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = WeatherService()
    test.handle_request("msg")
