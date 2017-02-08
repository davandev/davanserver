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
import json

class TimeEvent():
    def __init__(self, room, time, light_level ,device_id, label_id, virtual_device_id, onoff, enabled_when_armed):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.room = room
        self.time = time
        self.light_level = light_level
        self.device_id = device_id
        self.label_id = label_id
        self.virtual_device_id = virtual_device_id
        self.onoff = onoff
        if enabled_when_armed == "1":
            self.enabled_when_armed = True
        else:
            self.enabled_when_armed = False
        

    def toString(self):
        return "Room[ "+self.room+" ] "\
            "VD[ "+self.virtual_device_id+" ] "\
            "Action[ "+self.onoff+" ] "\
            "DeviceId[ "+self.device_id+" ] "\
            "DimmerValue[ "+self.light_level+" ] "\
            "ButtonId[ "+str(self.label_id)+" ] "\
            "Enabled_when_armed[ "+str(self.enabled_when_armed)+" ]"
        
class LightSchemaService(BaseService):
    '''
    Notice requires ntplib
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.LIGHTSCHEMA_SERVICE, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        # Sorted list of event to execute during the day
        self.todays_events = []
        # Current time  
        self.current_time = ""
        # Current weekday (0-6)
        self.current_day = -1
        self.config = config
        # Number of seconds until next event occur
        self.time_to_next_event = 0
        self.event = Event()    
  
    def stop_service(self):
        '''
        Stop the current service
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
        self.detemine_todays_events()
        
        def loop():
            while not self.event.wait(self.time_to_next_event): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()
                
                if len(self.todays_events) > 0:
                    self.time_to_next_event = self.calculate_next_timeout(self.todays_events[0].time)
                    self.logger.info("Next timeout " + self.todays_events[0].time + " in " + str(self.time_to_next_event) +  " seconds")
                else:
                    self.detemine_todays_events()

        Thread(target=loop).start()    
        return self.event.set

    def timeout(self):
        '''
        Timeout received, fetch event and perform action.
        '''
        self.logger.info("Got a timeout, trigger light event")
        try:
            event = self.todays_events.pop(0)
            self.invoke_event(event)
                                
        except:
            self.logger.error(traceback.format_exc())
            self.logger.info("Caught exception")
            self.increment_errors()
    
    def invoke_event(self, event):
        '''
        Execute event
        @param event event to be executed
        '''
        if event.enabled_when_armed and not self.alarm_is_armed():
            self.logger.info("Event is only triggered when alarm is armed")
            return
            
        self.logger.info("Invoking event:" + event.toString())
        if event.light_level != "-1" and event.onoff == "turnOn": # Lightlevel configured
            url = helper.create_fibaro_url_set_device_value(
                    self.config['DEVICE_SET_VALUE_WITH_ARG_URL'], 
                    event.device_id, 
                    event.light_level)
        else: # Just on/off switch
            url = helper.create_fibaro_url_set_device_value(
                    self.config['DEVICE_SET_VALUE_URL'], 
                    event.device_id, 
                    event.onoff)
        
        message = "Light is turned on"
        if event.onoff == "turnOff":
            message = "Light is turned off"
        
        # update status label of virtual device    
        self.update_virtual_device(event.virtual_device_id, "6", message)
        result = urllib.urlopen(url)        
            
    def schedule_events(self):
        '''
        Schedule all configured events and update all virtual devices with
        the schedules.
        '''
        configuration = self.config['LIGHT_SCHEMA']
        for event in configuration:
            items = event.split(",")
            if not self.enabled_this_day(items[3]):
                self.logger.info("Event Timer not configured this day")
                continue
            
            starttime = self.add_random_time(items[1],int(items[7]))
            self.todays_events.append(TimeEvent(items[0],  # Room name
                                                starttime, # Start time
                                                items[4],  # Light level
                                                items[5],  # Device id
                                                items[6],  # labelid
                                                items[8],  # virtualdevice id
                                                constants.TURN_ON,
                                                items[9]))
            
            stoptime = self.add_random_time(items[2],int(items[7]))
            self.todays_events.append(TimeEvent(items[0],
                                                stoptime,
                                                items[4],
                                                items[5],
                                                items[6], 
                                                items[8],
                                                constants.TURN_OFF,
                                                items[9]))
            
            self.update_virtual_device(items[8],items[6],str(starttime+ " => " + stoptime))
    
    def enabled_this_day(self, configured_interval):
        '''
        Check if this day is within the configured interval
        @return true if day is within interval false otherwise
        '''
        if (self.current_day < 5 and configured_interval == "weekdays"):
            return True
        elif self.current_day >= 5 and self.current_day <=6 and configured_interval =="weekend":
            return True
        elif configured_interval == "week": 
            return True
        return False
        
    def update_current_time_and_day(self):
        '''
        Set current_day and current_time
        '''
        n = datetime.now()
        self.current_time = format(n,"%H:%M:%S")
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        self.current_day = wd
        self.logger.info("Day["+str(wd)+"]" + " Time["+str(self.current_time)+"]")
    
    def detemine_todays_events(self):
        '''
        run at midnight, calculates all events that should occur this day. 
        '''
        if(str(datetime.today().weekday()) != str(self.current_day)): # Check if new day
            self.update_current_time_and_day()
            self.schedule_events()
            self.todays_events = self.sort_events(self.todays_events)
            if (len(self.todays_events) > 0):
                self.time_to_next_event = self.calculate_next_timeout(self.todays_events[0].time)
                self.logger.info("Next timeout " + self.todays_events[0].time + " in " + str(self.time_to_next_event) +  " seconds")
        else:
            self._calculate_time_until_midnight()
            self.logger.info("No more timers scheduled, wait for next re-scheduling in "+ str(self.time_to_next_event) + " seconds")
  
    def _calculate_time_until_midnight(self):   
        '''
        When all events are executed, calculate time until midnight
        '''
        tomorrow = date.today() + timedelta(1)
        midnight = datetime.combine(tomorrow, time())
        now = datetime.now()
        self.time_to_next_event = (midnight - now).seconds + 60
        self.logger.info("Sleep until midnight " + str(self.time_to_next_event) + " seconds")
              
    def sort_events(self, events):
        '''
        Sort all events based on when they expire. 
        Remove events where expire time is already passed.
        @param events list of all events
        '''
        future_events = []
        for event in self.todays_events:
            if (event.time > self.current_time):
                future_events.append(event)
            else:
                self.logger.info("Time ["+event.time+"] is already passed")
            
        sorted_events = sorted(future_events, key=lambda timeEvent: timeEvent.time)
        id = 0
        for event in sorted_events:
            self.logger.info("Event["+str(id)+"]" + str(event.time) + " " + str(event.room) + " " + str(event.onoff))
            id +=1
        return sorted_events
    
    def calculate_next_timeout(self, event_time):
        '''
        Calculate the number of seconds until the time expires
        @param event_time, expire time
        '''
        import datetime as dt
        self.logger.info("Calculate next timeout")
        self.update_current_time_and_day()
        start_dt = dt.datetime.strptime(self.current_time, '%H:%M:%S')
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
        
        random = (randint(-randomValue,randomValue))

        start_dt = datetime.strptime(configured_time, '%H:%M')
        sum = (start_dt + timedelta(minutes=random)) 
        timeout = format(sum, '%H:%M')
        if "00:" in str(timeout):
            self.logger.info("Timer expires after midnight, use original value")
            timeout = configured_time
        self.logger.info("Configured["+str(configured_time)+"] random["+str(random)+"] NewValue["+ str(timeout)+"]")

        return timeout
    

    def update_virtual_device(self, virtualdevice, labelid, message):
        '''
        Update virtual device on fibaro system with todays schedule
        @param virtualdevice virtual device id
        @param labelid label id on virtual device
        @param message message to display
        '''
        if virtualdevice != "-1":
            url = helper.createFibaroUrl(
                                self.config['UPDATE_DEVICE'], 
                                virtualdevice, 
                                self.config['LABEL_SCHEDULE'].replace("<BID>",labelid), 
                                message)
            result = urllib.urlopen(url)                
    
    def alarm_is_armed(self):
        '''
        Check if alarm is armed
        @return True if alarm is armed, False otherwise
        '''
        result = urllib.urlopen(self.config['FIBARO_API_ADDRESS'] + "globalVariables")
        res = result.read()
        data = json.loads(res)
        
        alarm = False 
        armed = False
        for items in data:
            if items["name"] =="AlarmState" and items["value"] == "Armed":
                armed = True
            if items["name"] =="AlarmType" and items["value"] == "Alarm":
                alarm = True
        if alarm and armed:
            return True 
        return False
        
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
        
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        htmlresult = ""
        if len(self.todays_events) >0:
            for event in self.todays_events:
                htmlresult += "<li>" + str(event.room) + " "+str(event.time)+" "+str(event.onoff)+"</li>\n"
        else:
                htmlresult += "<li>No more scheduled events today</li>\n"            
        column = column.replace("<SERVICE_VALUE>", htmlresult)

        return column        
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    service = LightSchemaService(config)
    service.alarm_is_armed()
    
