import logging
import os
import davan.util.helper_functions as helper 
from davan.util.StateMachine import StateMachine
from  davan.util.StateMachine import State

#HEATING_STATE = "Heating"
#STANDBY_STATE = "Standby"

#HEAT_START_STATE = "Heat-Start"
#HEAD_TO_STANDBY_STATE = "Heat-Stop"

#LEARNING_STATE = "Learning"
#INITIAL_STATE = "Initial"


#HEATING_STARTED = 1
#HEATING_ENDED = 2
STARTED = 1
CANCELLED = 0
INITIAL = 0
LIMIT = 3
# class StateMachine():
#      def __init__(self, initialState):
#         self.currentState = initialState
     
#      def handle_data(temp_change):
#         return self.currentState.handle_data(temp_change)

#      def change_state(new_state):
#         self.currentState = new_state

# class Initial_state():
#     def get_next(temp_change):
#         Learning_state 

# class Learning_state():
#     self.transition_started = False

#     def get_next(temp_change):
#         if temp_change == INCREASE:
#             self.transition_started = True

#         else:

class BaseState:
    def __init__(self, temp, configured_temp):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.temp = temp
        self.configured_temp = configured_temp
        self.transition = 0

    def handle_data(self, rainrate):
        assert 0, "run not implemented"
    def next(self):
        assert 0, "next not implemented"
    def get_message(self):
        assert 0, "next not implemented"

class InitialState(BaseState):
    def __init__(self, temp=-1, configured_temp=-1):
        BaseState.__init__( self,temp, configured_temp )
        self.name = "InitialState"
    
    def handle_data(self, current_temp):
        self.temp = current_temp
        self.configured_temp = current_temp

    def next(self):
        return NoHeatingState(self.temp,self.configured_temp)

    def get_message(self):
        return "Poolen har uppnått önskad temperatur ["+str(self.configured_temp)+"]"


class HeatingMaxReachedState(BaseState):
    def __init__(self, temp, configured_temp):
        BaseState.__init__( self, temp, configured_temp )
        self.name = "HeatingMaxReachedState"
    
    def handle_data(self, current_temp):
        if current_temp < self.temp:
            self.transition += STARTED
        else:
            self.logger.info("Continue heating, current temp["+str(current_temp)+"] < configured temp["+str(self.configured_temp)+"]")                
            self.transition = CANCELLED

        if current_temp >= self.configured_temp:
            self.configured_temp = current_temp


    def next(self):
        if self.transition == LIMIT:
            return NoHeatingState(self.temp, self.configured_temp)

    def get_message(self):
        return "Poolen har uppnått önskad temperatur ["+str(self.configured_temp)+"]"


class HeatingState(BaseState):
    def __init__(self, temp, configured_temp):
        BaseState.__init__( self, self.temp, self.configured_temp )
        self.name = "HeatingState"
    
    def handle_data(self, current_temp):
        if current_temp >= self.configured_temp:
            self.configured_temp = current_temp
            self.transition += STARTED

        else:
            self.logger.info("Continue heating, current temp["+str(current_temp)+"] < configured temp["+str(self.configured_temp)+"]")                
            self.transition = CANCELLED

    def next(self):
        if self.transition == LIMIT:
            return HeatingMaxReachedState(self.temp, self.configured_temp)

    def get_message(self):
        return "Startar värmaren i poolen"

class NoHeatingState(BaseState):
    def __init__(self, temp, configured_temp):
        BaseState.__init__( self, temp, configured_temp )
        self.name = "NoHeatingState"
    
    def handle_data(self, current_temp):
        if current_temp > self.temp :
            self.transition += STARTED
        else:
            self.transition = CANCELLED

    def next(self):
        if self.transition == 2:
            return HeatingState(self.temp, self.configured_temp)
        else:
            self.logger.info("Heating not started")

    def get_message(self):
        return "Stänger av värmaren"

class PoolTempHandle():
    '''
    Constructor
    '''
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))

#        self.temp = -1
        self.config = config
#        self.configured_temp = -1
#        self.state = INITIAL_STATE
#        self.transition_state = 0
        self.sm = StateMachine(config, InitialState())

    def handle_data(self, data):
        '''
        Process the recevied pool temp data
        '''
        current_temp = data['temp1c']

        #self._log_state(current_temp, self.temp)

        # Check limit
        if current_temp < 10 :     
            self._notify_state_change("Temperaturen i pool är "+current_temp+" grader, vilket är för lågt!")

        self.sm.handle_data(current_temp)
        next_state = self.sm.next() 
        
        if next_state:
            self.sm.change_state(next_state)


        # if self.state == INITIAL_STATE:
        #     self.temp = current_temp
        #     self.configured_temp = current_temp
        #     self._change_state(STANDBY_STATE)

        # # # Check if wanted temp reached when heating.
        # elif self.state == HEATING_STATE:
        #     if current_temp >= self.configured_temp:
        #         self.transition_state = CANCELLED
        #         self.configured_temp = current_temp
        #         self._notify_state_change("Poolen har uppnått önskad temperatur ["+str(self.configured_temp)+"]")

        #     elif current_temp < self.temp:
        #         if self.transition_state == STARTED:
        #             self._notify_state_change("Stänger av värmaren")
        #             self._change_state(STANDBY_STATE)
        #         else:
        #             self.transition_state = STARTED
        #     else:
        #         self.logger.info("Continue heating, current temp["+str(current_temp)+"] < configured temp["+str(self.configured_temp)+"]")                
        #         self.transition_state = CANCELLED

        # # # Check if heating is starterd
        # elif self.state == STANDBY_STATE:
        #     if current_temp > self.temp :
        #         if self.transition_state == STARTED:
        #             self._notify_state_change("Börjar värma vattnet i poolen ["+str(current_temp)+"]")
        #             self._change_state(HEATING_STATE)
        #         else:
        #             self.transition_state = STARTED
        #     else:
        #         self.transition_state = CANCELLED
        #         self.logger.info("Heating not started")

        # self.temp = current_temp

    def _log_state(self,new_temp,prev_temp):
        '''
        Log the current state and temp
        '''
        self.logger.info("State["+self.state+ "] Temp ["+str(prev_temp)+"] -> ["+str(new_temp)+"]")

    def _change_state(self,new_state):
        '''
        Change state 
        '''
        self.logger.info("State["+self.state+ "] -> State["+new_state+"]")
        self.state = new_state
        self.transition_state = INITIAL

    def _notify_state_change(self,msg):
        '''
        Update any pool temp change
        '''
        self.logger.debug(msg)
        helper.send_telegram_message(self.config, msg)
