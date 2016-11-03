'''
Created on 8 feb. 2016

@author: Wilma
'''
import logging
import os
from urllib import quote
import davan.http.service.telldus.tdtool as telldus
import urllib
import datetime
from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class TelldusSensorService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TELLDUS_SENSOR_SERVICE, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()

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
#        try:

        response=telldus.listSensorsAndValues()
 
        self.logger.info("Telldus sensor values: response:!" + str(response))

        if not 'sensor' in str(response):
            self.logger.error("No response received from telldus")
            return 
        for sensor in response['sensor']:
            name = "%s" % (sensor['name'])
            self.logger.info("Sensor name: %s" %name )
            
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
                          
        
#        except Exception as e:
#            self.logger.info("Caught exception") 
#            pass
    def createSensorUrl(self, baseurl, labelId, tempValue):
        temp_url = baseurl.replace('<LABELID>',labelId)


        tempValue = quote(tempValue, safe='') 
        temp_url= temp_url.replace('<VALUE>','"' + tempValue+ '"')
        self.logger.info(temp_url)
        return temp_url
    
    def sendUrl(self, url):
        result = urllib.urlopen(url)        

        
#        request = urllib2.Request(url)
 #       base64string = base64.encodestring(self.config["FIBARO_USER_NAME"] + ":" + 
 #                                      self.config["FIBARO_PASSWORD"])
 #       request.add_header("Authorization", "Basic %s" % base64string)   
#        result = urllib2.urlopen(request)    
        self.logger.info("Result: " + str(result) )                
        
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = TelldusSensorService()
