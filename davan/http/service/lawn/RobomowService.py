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
        self.transition_time =300 
            
        # Hold the current state, assume start in standby
        self.current_state = "Standby"
        # Holds the expected next status
        self.next_state = "" 
        # Determine if powersocket should be turned off while not scheduled for mowing
        self.turn_off_power_on_schedule = False
        self.local_event = Event()

    def init_service(self):
        pass
    def parse_request(self, msg):
        '''
        '''
        msg = msg.split('?')
        res = msg[1].split('=')
        return float(res[1])

    def handle_request(self, msg):
        '''
        Request with current power consumption received from power socket via Fibaro server, 
        '''
        try:
            power = self.parse_request(msg)
            self.increment_invoked()
            new_state = self.get_state_name(power)
            self.logger.info("Received power usage["+str(power)+"] NewState["+new_state+"] CurrentState["+self.current_state+"]")
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
 
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            self.raise_alarm(constants.ROBOMOW_FAILURE, "Warning", constants.ROBOMOW_FAILURE)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def update_fibaro_device(self, state, change):
        '''
        Update virtual device with current state and time when state changed.
        '''
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS']['State'],
                                state)
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS']['Changed'],
                                change)
        helper.send_auth_request(url,self.config)


    def get_state_name(self,power):
        '''
        Determine state based on power consumption
        '''
        if power > self.power_level['Charging']:
            return "Charging"
        elif power == self.power_level['Off']:
            return "Off"
        elif power < self.power_level['Working']:
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
        # Update fibaro virtual device
        self.update_fibaro_device(self.next_state,str(current_date) +"-"+ str(current_time) )
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