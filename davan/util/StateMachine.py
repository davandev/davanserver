import logging
import os
import davan.util.helper_functions as helper 

class State:
    def __init__(self):
        self.logger = logging.getLogger(os.path.basename(__file__))

    def handle_data(self, rainrate):
        assert 0, "run not implemented"
    def next(self):
        assert 0, "next not implemented"
    def get_message(self):
        assert 0, "next not implemented"


class StateMachine():
    def __init__(self, config, initialState):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.currentState = initialState
        self.config = config
    
    def handle_data(self,temp_change):
        '''
        Pass data to current state
        '''
        return self.currentState.handle_data(temp_change)

    def next(self):
        '''
        Return the next state
        '''
        return self.currentState.next()
    
    def change_state(self, new_state):
        '''
        Change to new state
        '''
        self.logger.info("["+self.currentState.name+"] --> ["+ str(new_state.name)+"]")
        self.currentState = new_state
        helper.send_telegram_message(self.config, new_state.get_message())

