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
from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants 
from davan.http.service.base_service import BaseService
from datetime import datetime, timedelta

class TimeEvent():
    def __init__(self, t, dv ,di, bi, vd, onoff):
        self.time = t
        self.virtualDevice =vd
        self.onoff = onoff
        self.buttonId =bi
        self.deviceId =di
        self.dimmerValue = dv

    def toString(self):
        return "VD["+self.virtualDevice+"] Action["+self.onoff+"] DeviceId["+self.deviceId+"] DimmerValue["+self.dimmerValue+"] ButtonId["+self.buttonId+"]"
        
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
            self.todaySchema.append(TimeEvent(starttime,items[4],items[5],items[6], items[8],"on"))
            stoptime = self.add_random_time(items[2],int(items[7]))
            self.todaySchema.append(TimeEvent(stoptime,items[4],items[5],items[6], items[8],"off"))
    
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
#         self.currentTime = str(h)+":"+str(min)+":"+str(sec)
        self.currentDay = wd
        self.logger.info("Day["+str(wd)+"]" + "Time["+str(self.currentTime)+"]")
        
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        self.logger.info("Starting re-occuring event")
        self.get_current_time_and_day()
        self.parse_configuration()
        #self.currentTime =  datetime.strptime(now, '%H:%M')
        self.todaySchema = self.sort_events(self.todaySchema)
        #self.todaySchema = sorted(self.todaySchema, key=lambda timeEvent: timeEvent.time)
        #self.logger.info("Next timer;" + self.todaySchema[0].time)
#         n = datetime.now()
#         t = n.timetuple()
#         y, m, d, h, min, sec, wd, yd, i = t
#         self.logger.info("Day["+str(wd)+"]" + "Time["+str(h)+":"+str(min)+"]")
        if (len(self.todaySchema)>0):
            self.nextSleepTime = self.calculate_next_timeout(self.todaySchema[0].time)
#        nextTimeout += self.add_random_time(self.todaySchema[0].randomTime)
            self.logger.info("Next timeout:" + str(self.nextSleepTime))
        else:
            self.logger.info("No more timers today")
        
        def loop():
            while not self.event.wait(self.nextSleepTime): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()
                if len(self.todaySchema)>0:
                    self.nextSleepTime = self.calculate_next_timeout(self.todaySchema[0].time)
                else:
                    self.logger.info("No more events today, set timer for 02:00")
                    
        Thread(target=loop).start()    
        return self.event.set
             
    def sort_events(self, events):
        self.logger.info("Sort events")
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
        import datetime as dt
        self.logger.info("Calculate next timeout")
#         n = datetime.now()
#         t = n.timetuple()
#         y, m, d, h, min, sec, wd, yd, i = t
#         self.logger.info("Day["+str(wd)+"]" + "Time["+str(h)+":"+str(min)+"]")
#         now = str(h)+":"+str(min)
        self.get_current_time_and_day()
        start_dt = dt.datetime.strptime(self.currentTime, '%H:%M:%S')
        end_dt = dt.datetime.strptime(event_time, '%H:%M')
        diff = (end_dt - start_dt) 
        if diff.days < 0:
            self.logger.warning("End is before start, fix it")
            diff = timedelta(days=0, seconds=diff.seconds)
        self.logger.info("Next timeout in " + str(diff.seconds)+" seconds")
        return diff.seconds
    
    def add_random_time(self, configured_time, randomValue):
        if randomValue == 0:
            return configured_time
        
        from random import randint
        random = (randint(0,randomValue))
        #self.logger.info("New randomValue: "+ str(random))

        start_dt = datetime.strptime(configured_time, '%H:%M')
        #random_dt = datetime.strptime(str(random), '%M')
        sum = (start_dt + timedelta(minutes=random)) 
        timeout = format(sum, '%H:%M')
        if "00:" in str(timeout):
            self.logger.info("Timer expires after midnight, use original value")
            timeout = configured_time
        self.logger.info("Configured["+str(configured_time)+"] random["+str(random)+"] NewValue["+ str(timeout)+"]")

        return timeout
    
    def timeout(self):
        '''
        Timeout received, send a "ping" to key pad, send telegram message if failure.
        '''
        self.logger.info("Got a timeout, trigger light event")
        try:
            event = self.todaySchema.pop(0)
            self.invoke_event(event)
#             nextTimeout = self.calculate_next_timeout()
#             nextTimeout += self.add_random_time(self.event.randomTime)
#             self.logger.info("Next timeout:" + str(nextTimeout))
#             self.maybe_send_update(True)
        except:
            self.increment_errors()
    
    def invoke_event(self, event):
        self.logger.info("Invoking event:" + event.toString())
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
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    service = LightSchemaService(config)
    service.start_service()
    
