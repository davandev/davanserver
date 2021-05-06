import json
import logging
import time
import os
import traceback
from threading import Thread,Event

import davan.util.helper_functions as helper 
import davan.util.timer_functions as timer_functions

import requests
import davan.config.config_creator as configuration
from davan.http.service.base_service import BaseService
import davan.util.constants as constants

class RobomowService(BaseService):
    def __init__(self, service_provider, config):
        '''
        '''
        BaseService.__init__(self, constants.ROBOMOW_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        #Power consumption in different scenarious.
        self.power_level = {
            'Charging':45, # 
            'Working':7,
            'Standby':8, 
            'Off':0.0, 
            'Unknown':-1}
        self.transition_time = 300 
            
        # Hold the current state, assume start in standby
        self.current_state = "Standby"
        # Holds the expected next status
        self.next_state = "" 
        self.max_activities = 12
        # Determine if powersocket should be turned off while not scheduled for mowing
        self.turn_off_power_on_schedule = False
        self.local_event = Event()
        self.isTimeToLawn = False
        self.activity_counter = 0


    def parse_request(self, msg):
        '''
        '''
        msg = msg.split('?')
        res = msg[1].split('=')
        return res[0],res[1]

    def handle_request(self, msg):
        '''
        Request with current power consumption received from power socket via Fibaro server, 
        '''
        try:
            reqType,value = self.parse_request(msg)
            self.logger.debug("Request[" + msg +"] ReqType["+reqType+"] Value["+value+"]")
            self.increment_invoked()
            if reqType =="service":
                if value == constants.TURN_ON:
                    self.logger.debug("Start reporting power changes")
                    self.start_reporting()                                          
                else:
                     self.logger.debug("Stop reporting power changes")                                          
                     self.stop_reporting()
                
            else:
                if self.isTimeToLawn:
                    new_state = self.get_state_name(float(value))
                    self.logger.info("Received power usage["+str(value)+"] NewState["+new_state+"] CurrentState["+self.current_state+"]")
                    if not self.is_enabled():
                        return

                    if new_state == self.current_state:
                        self.logger.info("No change in current state["+self.current_state+"], Reset Next["+self.next_state+"] -> [] ")
                        if self.next_state:
                            self.stop_timer()
                            self.next_state =""
                    else: # new_state != self.current_state
                        if new_state == self.next_state:
                            self.logger.info("No change in transition state ["+self.next_state+"]")
                        else:
                            self.logger.info("Change in transition state Next["+self.next_state+"] -> ["+new_state+"]")
                            if self.next_state:
                                self.stop_timer()
                            self.next_state = new_state
                            self.start_transition_timer()
                else:
                    self.logger.debug("Not scheduled to lawn, skip report")


        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            self.raise_alarm(constants.ROBOMOW_FAILURE, "Warning", constants.ROBOMOW_FAILURE)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def stop_reporting(self):
        self.logger.info("Stop reporting")
        self.isTimeToLawn = False
        self.next_state = "Off"
        current_time , _ ,current_date = timer_functions.get_time_and_day_and_date()
        self.update_new_fibaro_device('Deactive', current_date, current_time)

    def start_reporting(self):
        self.logger.info("Start reporting")
        self.activity_counter = 1
        self.isTimeToLawn = True

        for  id in range(1,self.max_activities):
            url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Activity'],
                                '-')
            url = url.replace('<id>',str(id))                                
            helper.send_auth_request(url,self.config)

        current_time , _ ,current_date = timer_functions.get_time_and_day_and_date()
        self.update_new_fibaro_device('Active', current_date, current_time)

    def update_new_fibaro_device(self, state, current_date, time_changed):
        '''
        Update virtual device with current state and time when state changed.
        '''
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Date'],
                                current_date)
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Status'],
                                state)
        self.logger.info("Url 1: " +str(url))
        helper.send_auth_request(url,self.config)

        value = time_changed + "   " +state
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Activity'],
                                value)
        url = url.replace('<id>',str(self.activity_counter))                                

        self.logger.info("Url 2: " +str(url))
        helper.send_auth_request(url,self.config)

    def get_state_name(self,power):
        '''
        Determine state based on power consumption
        '''
        if power > self.power_level['Charging']:
            return "Charging"
        elif power == self.power_level['Off']:
            return "Off"
        elif power <= self.power_level['Working']:
            return "Working"
        elif 7.5 <= power <= 30.0:
            return "Standby"
        return "Error"
    
    def start_transition_timer(self,):
        '''
        Start state transition timer
        '''
        self.local_event = Event()
        def countdown():
            try:                    
                self.increment_invoked()
                # Wait x seconds before actually changing state
                while not self.local_event.wait(self.transition_time):
                    self.change_state()
            except:
                self.logger.error(traceback.format_exc())
                self.increment_errors()

        Thread(target=countdown, name="RobmowTransitionTimer").start()    
        return self.local_event.set

    def stop_timer(self):
        '''
        State changed before transition timer
        '''
        self.logger.info("State changed during transition time")
        self.local_event.set()

    def change_state(self):
        '''
        Transition time expired without change of next state,
        then consider state actually changed.
        '''
        self.logger.info("Changing state to ["+self.next_state+"]")
        self.local_event.set()
        # Send telegram with new state
        helper.send_telegram_message(self.config, "Robomow["+self.next_state+"]")
        
        current_time, _ ,current_date = timer_functions.get_time_and_day_and_date()
        self.activity_counter = self.activity_counter+1
        # Update fibaro virtual device
        #self.update_fibaro_device(self.next_state,str(current_date) +"-"+ str(current_time) )
        try:
            self.update_new_fibaro_device(self.next_state, current_date, current_time)
        except:
            self.logger.error(traceback.format_exc())
        # Change state
        self.current_state = self.next_state
        # Reset next state
        self.next_state = ""

if __name__ == '__main__':
    from davan.util import application_logger as app_logger
    config = configuration.create()
    
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = RobomowService("",config)
    test.handle_request("RobomowService?power=5")