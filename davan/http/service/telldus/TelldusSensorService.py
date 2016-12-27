'''
@author: davandev
'''
import logging
import os
from urllib import quote
import urllib
import datetime
import traceback
from threading import Thread,Event
import davan.http.service.telldus.tdtool as telldus
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class TelldusSensorService(BaseService):
    '''
    Starts a re-occuring service that fetches sensor values from Telldus Live and 
    pushes the results(temperature, humidity and date) of each sensor to a 
    virtual device on the Fibaro system. 
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TELLDUS_SENSOR_SERVICE, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()

    def stop_service(self):
        '''
        Stops the service
        '''
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
            while not self.event.wait(900): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()
        Thread(target=loop).start()    
        return self.event.set
                                         
    def timeout(self):
        '''
        Timeout received, fetch sensor values from Telldus Live
        Push sensor data to Fibaro virtual device  
        '''
        self.logger.info("Got a timeout, fetch sensor states")

        response=telldus.listSensorsAndValues()

        if not 'sensor' in str(response):
            self.logger.error("No response received from telldus")
            return 
        for sensor in response['sensor']:
            name = "%s" % (sensor['name'])
            self.logger.debug("Sensor name: %s" %name )
            
            if self.config["SENSOR_MAP"].has_key(name):
                device_id = self.config["SENSOR_MAP"][name]
                url = self.config['UPDATE_DEVICE']
                url = url.replace('<DEVICEID>',device_id)
                sensorUrl = self.createSensorUrl(url, self.config['LABEL_TEMP'], sensor['temp'])
                self.sendUrl(sensorUrl)
                sensorUrl = self.createSensorUrl(url, self.config['LABEL_DATE'], str(datetime.datetime.fromtimestamp(int(sensor['lastUpdated']))))
                self.sendUrl(sensorUrl)
                if 'humidity' in sensor:
                    sensorUrl = self.createSensorUrl(url, self.config['LABEL_HUMIDITY'], sensor['humidity'])
                    self.sendUrl(sensorUrl)
                    self.maybe_notify_humidity_level(sensor['name'], sensor['humidity'])
                          
        
    def createSensorUrl(self, baseurl, labelId, tempValue):
        '''
        Create url to update virtual device on fibaro system 
        @baseurl, base url
        @labelId, label id of virtual device 
        @tempValue, current temperature value.
        '''
        temp_url = baseurl.replace('<LABELID>',labelId)
        tempValue = quote(tempValue, safe='') 
        temp_url= temp_url.replace('<VALUE>','"' + tempValue+ '"')
        return temp_url
    
    def sendUrl(self, url):
        '''
        Update fibaro system with sensor values
        @param url, url with sensor values
        '''
        urllib.urlopen(url)        

    def maybe_notify_humidity_level(self, sensor_name, humidity_value):
        '''
        Check if the received humidity value is higher than the configured limit.
        If higher then send telegram notifications to all configured receivers.
        @param sensor_name, name of the sensor
        @param humidity_value, humidity value
        '''
        try:
            self.logger.info(" Check if sensor" +sensor_name+ " has limit configured" )
            if self.config["SENSOR_HUMIDITY_LIMITS"].has_key(sensor_name):
                self.logger.info("Sensor "+ sensor_name +" has humidity limits configured. Current value["+humidity_value+"]")
                
                sensor_limit = self.config['SENSOR_HUMIDITY_LIMITS'][sensor_name]
                if int(humidity_value) > sensor_limit :
                    self.logger.info("Humidity value higher exceeds limit, send notifications")
                    message= constants.HUMIDITY_HIGH.replace("<room_name>", str(sensor_name) + " " + str(humidity_value))
                    self.logger.info("Message:" + message)
                    for chatid in self.config['CHATID']:
                        url = self.config['TELEGRAM_PATH'].replace('<CHATID>', chatid) + message
                        self.logger.info("Url:" + url)
                        urllib.urlopen(url)
        except :
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = TelldusSensorService()
