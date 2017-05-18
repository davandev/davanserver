# -*- coding: utf-8 -*-

'''
@author: davandev
'''

import logging
import os
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
import davan.http.service.announcement.Announcements as announcements
import datetime
import davan.util.timer_functions as timer_functions
import davan.util.fibaro_functions as fibaro_functions
import davan.util.helper_functions as helper_functions

class AnnouncementEvent():
    def __init__(self, slogan, time, announcement_id, speaker):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.slogan = slogan
        self.time = time
        self.announcement_id = announcement_id
        self.speaker_id = speaker
        

    def toString(self):
        return "Slogan[ "+self.slogan+" ] "\
            "AnnouncmentId[ "+self.announcement_id+" ] "\
            "Speaker[ "+self.speaker+" ]"
        

class AnnouncementsService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.ANNOUNCEMENT_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
#        self.event = Event()
        self.daily_ordsprak = "http://www.knep.se/dagens/ordsprak.xml"
        self.daily_gata = "http://www.knep.se/dagens/gata.xml"
        # Sorted list of event to execute during the day
        self.todays_events = []
        # Current time  
        self.current_time = ""
        # Current weekday (0-6)
        self.current_day = -1
        # Current date
        self.current_date = ""
        
        self.config = config 
        # Number of seconds until next event occur
        self.time_to_next_event = 0

    def handle_request(self, msg):
        '''
        Received request to play announcement
        @param msg, received request 
        '''
        self.logger.info("Msg:"+msg)
        announcement_id = (msg.split('=')[1])
        event = AnnouncementEvent("ExternalCall", "", announcement_id, "0")
        if self.invoke_event(event):
            return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_OK
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_NOT_OK
 
    def get_next_timeout(self):
        '''
        Calculate seconds until next timeout.
        @return nr of seconds until timout.
        '''
        if len(self.todays_events) > 0:
            self.time_to_next_event = timer_functions.calculate_next_timeout(self.todays_events[0].time)
            self.logger.info("Next timeout " + self.todays_events[0].time + " in " + str(self.time_to_next_event) +  " seconds")
        else:
            self.detemine_todays_events()

        return self.time_to_next_event        

    def handle_timeout(self):
        '''
        Timeout received, fetch event and perform action.
        '''
        self.logger.info("Got a timeout, trigger announcement event")
        try:
            event = self.todays_events.pop(0)
            self.invoke_event(event)
                                
        except:
            self.logger.error(traceback.format_exc())
            self.logger.info("Caught exception")
            self.increment_errors()
            
    def invoke_event(self, event):
        '''
        Timeout received, produce the announcement and play in configured speaker
        '''
        self.logger.info("Got a timeout, play announcement[" + event.slogan + "]")
        if fibaro_functions.is_alarm_armed(self.config):
            self.logger.info("Alarm is armed, skip announcement")
            return True
        try:
            service = self.services.get_service(event.announcement_id)
            if service != None:
                result = service.get_announcement()
            elif event.announcement_id == "morning" :
                result = announcements.create_morning_announcement()
                result += announcements.create_name_announcement()
                result += self.services.get_service(constants.CALENDAR_SERVICE_NAME).get_announcement()
                result += self.services.get_service(constants.WEATHER_SERVICE).get_announcement()
                result += self.services.get_service(constants.QUOTE_SERVICE_NAME).get_announcement()
                
#                result += announcements.create_quote_announcement()

            elif event.announcement_id == "night":
                result = announcements.create_night_announcement()
            elif event.announcement_id == "status":
                result = helper_functions.encode_message("Status uppdatering. ")
                result += self.services.get_service(constants.WEATHER_SERVICE).get_announcement()
                result += self.services.get_service(constants.CALENDAR_SERVICE_NAME).get_announcement()
                result += self.services.get_service(constants.DEVICE_PRESENCE_SERVICE_NAME).get_announcement()
            else:
                self.logger.info("Cant find announcement to play:" + event.announcement_id)
                return False
            self.logger.info("Announcement:" + result)
            self.services.get_service(constants.TTS_SERVICE_NAME).start(result,event.speaker_id)
            return True
        except Exception:
            self.logger.error(traceback.format_exc())

            self.increment_errors()
            self.logger.info("Caught exception") 
            return False

    def detemine_todays_events(self):
        '''
        run at midnight, calculates all events that should occur this day. 
        '''
        if(str(datetime.datetime.today().weekday()) != str(self.current_day)): # Check if new day
            self.current_time, self.current_day, self.current_date = timer_functions.get_time_and_day_and_date()
            self.schedule_events()
            self.todays_events = self.sort_events(self.todays_events)
            if (len(self.todays_events) > 0):
                self.time_to_next_event = timer_functions.calculate_next_timeout(self.todays_events[0].time)
                self.logger.info("Next timeout " + self.todays_events[0].time + " in " + str(self.time_to_next_event) +  " seconds")
        else:
            self.time_to_next_event = timer_functions.calculate_time_until_midnight()
            self.logger.info("No more timers scheduled, wait for next re-scheduling in "+ str(self.time_to_next_event) + " seconds")

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
                self.logger.debug("Time ["+event.time+"] is already passed")
            
        sorted_events = sorted(future_events, key=lambda timeEvent: timeEvent.time)
        id = 0
        for event in sorted_events:
            self.logger.info("Event["+str(event.slogan)+"] Timeout[" + str(event.time)+"]")
            id +=1
        return sorted_events

    def schedule_events(self):
        '''
        Parse all configured events
        '''
        configuration = self.config['ANNOUNCEMENTS_SCHEMA']
        for event in configuration:
            items = event.split(",")
            if not timer_functions.enabled_this_day(self.current_day,
                                                    self.current_date,
                                                    items[2].strip()):
                self.logger.info("Event Timer not configured this day")
                continue
            
            self.todays_events.append(AnnouncementEvent(items[0].strip(),  # Slogan
                                                items[1].strip(),  # time
                                                items[3].strip(),  # announcment id
                                                items[4].strip()))  # speaker_id
                                                
    
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = AnnouncementsService(config)
    test.timeout()
