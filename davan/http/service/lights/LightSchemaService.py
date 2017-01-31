'''
@author: davandev
'''

import logging
import os
import traceback
import sys
import time
#import ntplib
import urllib
from random import randint
from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper 
from davan.http.service.base_service import BaseService
from datetime import datetime, timedelta
from datetime import *

class TimeEvent():
    def __init__(self, s, t, dv ,di, bi, vd, onoff):
        self.slogan = s
        self.time = t
        self.virtualDevice =vd
        self.onoff = onoff
        self.buttonId =bi
        self.deviceId =di
        self.dimmerValue = dv

    def toString(self):
        return "Room[ "+self.slogan+" ] VD[ "+self.virtualDevice+" ] Action[ "+self.onoff+" ] DeviceId[ "+self.deviceId+" ] DimmerValue[ "+self.dimmerValue+" ] ButtonId[ "+self.buttonId+" ]"
        
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
        self.todaySchema = [] 
        self.currentTime = ""
        self.currentDay = -1
        self.config = config
        self.nextSleepTime = 0
        self.event = Event()    

    
    def parse_configuration(self):
        configuration = config['LIGHT_SCHEMA']
        for event in configuration:
            items = event.split(",")
            if not self.enabled_this_day(items[3]):
                self.logger.info("Timer not configured this day")
                continue
            
            starttime = self.add_random_time(items[1],int(items[7]))
            self.todaySchema.append(TimeEvent(items[0],starttime,items[4],items[5],items[6], items[8],"turnOn"))
            stoptime = self.add_random_time(items[2],int(items[7]))
            self.todaySchema.append(TimeEvent(items[0],stoptime,items[4],items[5],items[6], items[8],"turnOff"))
    
    def enabled_this_day(self, configured_interval):
        if (self.currentDay < 5 and configured_interval == "weekdays"):
            return True
        elif self.currentDay >= 5 and self.currentDay <=6 and configured_interval =="weekend":
            return True
        elif configured_interval == "week": 
            return True
        return False
        
    def get_current_time_and_day(self):
        n = datetime.now()
        self.currentTime = format(n,"%H:%M:%S")
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        self.currentDay = wd
        self.logger.info("Day["+str(wd)+"]" + " Time["+str(self.currentTime)+"]")
    
    def detemine_todays_events(self):
        if(str(datetime.today().weekday()) != str(self.currentDay)):
            self.get_current_time_and_day()
            self.parse_configuration()
            self.todaySchema = self.sort_events(self.todaySchema)
            if (len(self.todaySchema) > 0):
                self.nextSleepTime = self.calculate_next_timeout(self.todaySchema[0].time)
                self.logger.info("Next timeout " + self.todaySchema[0].time + " in " + str(self.nextSleepTime) +  " seconds")
        else:
            self._calculate_time_until_midnight()
            self.logger.info("No more timers scheduled, wait for next re-scheduling in "+ str(self.nextSleepTime) + " seconds")
        
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        self.logger.info("Starting re-occuring event")
        self.detemine_todays_events()
#         self.get_current_time_and_day()
#         self.parse_configuration()
#         self.todaySchema = self.sort_events(self.todaySchema)
#         if (len(self.todaySchema) > 0):
#             self.nextSleepTime = self.calculate_next_timeout(self.todaySchema[0].time)
# #        nextTimeout += self.add_random_time(self.todaySchema[0].randomTime)
#             self.logger.info("Next timeout " +self.todaySchema[0].time +" in "+ str(self.nextSleepTime)+ " seconds")
#         else:
#             self.logger.info("No more timers today")
#             self._calculate_time_until_midnight()
        
        def loop():
            while not self.event.wait(self.nextSleepTime): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()
                if len(self.todaySchema) > 0:
                    self.nextSleepTime = self.calculate_next_timeout(self.todaySchema[0].time)
                else:
                    self.detemine_todays_events()

#                     if(datetime.now().timetuple().wd != self.currentDay):
#                         self.logger.info("New day, recalculate timers")
#                         self.get_current_time_and_day()
#                         self.parse_configuration()
#                         self.todaySchema = self.sort_events(self.todaySchema)
#                         
#                     else:
#                         self.logger.info("No more events today, set timer for 02:00")
#                         self._calculate_time_until_midnight()
                    
        Thread(target=loop).start()    
        return self.event.set
    
    def _calculate_time_until_midnight(self):   
        tomorrow = date.today() + timedelta(1)
        midnight = datetime.combine(tomorrow, time())
        now = datetime.now()
        self.nextSleepTime = (midnight - now).seconds + 60
        self.logger.info("Sleep until midnight " + str(self.nextSleepTime) + " seconds")
              
    def sort_events(self, events):
        '''
        Sort all events based on when they expire. 
        Remove events where expire time is already passed.
        @param events list of all events
        '''
        future_events = []
        for event in self.todaySchema:
            if (event.time > self.currentTime):
                future_events.append(event)
            else:
                self.logger.info("Time ["+event.time+"] is already passed")
            
        sorted_events = sorted(future_events, key=lambda timeEvent: timeEvent.time)
        id = 0
        for event in sorted_events:
            self.logger.info("Event["+str(id)+"]" + event.time)
            id +=1
        return sorted_events
    
    def calculate_next_timeout(self, event_time):
        '''
        Calculate the number of seconds until the time expires
        @param event_time, expire time
        '''
        import datetime as dt
        self.logger.info("Calculate next timeout")
        self.get_current_time_and_day()
        start_dt = dt.datetime.strptime(self.currentTime, '%H:%M:%S')
        end_dt = dt.datetime.strptime(event_time, '%H:%M')
        diff = (end_dt - start_dt) 
        if diff.days < 0:
            self.logger.warning("End is before start, fix it")
            diff = timedelta(days=0, seconds=diff.seconds)
        #self.logger.info("Next timeout in " + str(diff.seconds)+" seconds")
        return diff.seconds
    
    def add_random_time(self, configured_time, randomValue):
        '''
        Adds a random value to the configured time.
        @param configured_time, configured expire time
        @param randomValue, the configured random value
        @return new expire time
        '''
        if randomValue == 0:
            return configured_time
        
        random = (randint(0,randomValue))

        start_dt = datetime.strptime(configured_time, '%H:%M')
        sum = (start_dt + timedelta(minutes=random)) 
        timeout = format(sum, '%H:%M')
        if "00:" in str(timeout):
            self.logger.info("Timer expires after midnight, use original value")
            timeout = configured_time
        self.logger.info("Configured["+str(configured_time)+"] random["+str(random)+"] NewValue["+ str(timeout)+"]")

        return timeout
    
    def timeout(self):
        '''
        Timeout received, fetch event and perform action.
        '''
        self.logger.info("Got a timeout, trigger light event")
        try:
            event = self.todaySchema.pop(0)
            self.invoke_event(event)
        except:
            self.increment_errors()
    
    def invoke_event(self, event):
        self.logger.info("Invoking event:" + event.toString())
        if event.onoff == "turnOn":
            url = helper.create_fibaro_url_set_device_value(
                    self.config['DEVICE_SET_VALUE_WITH_ARG_URL'], 
                    event.deviceId, 
                    event.dimmerValue)
        else:
            url = helper.create_fibaro_url_set_device_value(
                    self.config['DEVICE_SET_VALUE_URL'], 
                    event.deviceId, 
                    event.onoff)
            
        self.logger.info("Url:" + url)
        
    def sync_time(self):
        '''
        Sync time once a day.
        '''
        try:
            self.logger.info("Attempt to sync time with ntp server")
#            client = ntplib.NTPClient()
#            response = client.request('pool.ntp.org')
#            os.system('date ' + time.strftime('%m%d%H%M%Y.%S',time.localtime(response.tx_time)))
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
        #if not self.is_enabled():
        #    return BaseService.get_html_gui(self, column_id)
        
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        htmlresult = ""
        if len(self.todaySchema) >0:
            for event in self.todaySchema:
                htmlresult += "<li>Room[" + str(event.slogan) + "] Time["+str(event.time)+"] Action["+event.onoff+"]</li>\n"
        else:
                htmlresult += "<li>No more scheduled events today</li>\n"            
        column = column.replace("<SERVICE_VALUE>", htmlresult)

        return column        
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    service = LightSchemaService(config)
    service.start_service()
    print service.get_html_gui("2")
    
