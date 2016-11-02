'''
Created on 8 feb. 2016

@author: Wilma
'''
import logging
import os
from urllib import quote
import davan.http.service.telldus.tdtool as telldus
#import urllib2, base64
import urllib
import datetime
from threading import Thread,Event
import davan.config.config_creator as configuration
from davan.http.service.base_service import BaseService

class TelldusSensorService(BaseService):
    '''
    classdocs
    Number of sensors: 10
2513889 None    23.8    114     2016-08-16 09:56:46
144895  Badrum  27.1    54      2016-08-19 17:32:55
365850  Datarum 26.3    49      2016-06-29 09:57:40
135627  Garage  16.5    44      2016-06-10 02:51:50
128361  Gillestuga      21.4    31      2016-03-19 17:24:20
105675  Kk     21.7    2015-10-30 06:17:44
424124  Sovrum  19.9    43      2015-05-15 09:06:24
421645  Tv-rum  22.6    50      2015-09-10 22:44:10
2354043 Tvtstuga      25.6    46      2016-08-19 23:54:02
134588  Wilma   24.0    56      2016-08-19 23:54:45

    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, "TelldusSensorService", config)
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
        Timeout received, send a "ping" to key pad, to keep the http server socket on 
        keypad open.
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
