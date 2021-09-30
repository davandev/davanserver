import logging
import os
import davan.util.helper_functions as helper 
from davan.util.StateMachine import StateMachine
from  davan.util.StateMachine import State

# class StateMachine():
#     def __init__(self, config, initialState):
#         self.logger = logging.getLogger(os.path.basename(__file__))
#         self.currentState = initialState
#         self.config = config
    
#     def handle_data(self,temp_change):
#         '''
#         Pass data to current state
#         '''
#         return self.currentState.handle_data(temp_change)

#     def next(self):
#         '''
#         Return the next state
#         '''
#         return self.currentState.next()
    
#     def change_state(self, new_state):
#         '''
#         Change to new state
#         '''
#         self.logger.info("["+self.currentState.name+"] --> ["+ str(new_state.name)+"]")
#         self.currentState = new_state
#         helper.send_telegram_message(self.config, new_state.get_message())

class RainingState(State):
    def __init__(self):
        State.__init__( self )
        
        self.name = "RainingState"
        self.transition = 0
    
    def handle_data(self,rainrate):
        if rainrate > 0 :
            self.transition = 0
        else:
            self.transition += 1
            self.logger.info("Verkar slutat regna "+ str(self.transition))

    def next(self):
        if self.transition == 3:
            return NoRainState()
        else:
            return None

    def get_message(self):
        return "Det har börjar regna"


class NoRainState(State):
    def __init__(self):
        State.__init__( self )
        self.name = "NoRainState"
        self.transition = 0
    
    def handle_data(self, rainrate):
        if rainrate > 0 :
            self.transition += 1
            self.logger.info("Verkar börjat regna "+ str(self.transition))
        else:
            self.transition = 0

    def next(self):
        if self.transition == 3:
            return RainingState()
        else:
            return None

    def get_message(self):
        return "Det har slutat regna"


class RainHandle():

    '''
    Constructor
    '''
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.config = config
        self.is_raining = False
        self.sm = StateMachine(config, RainingState())


    def handle_data(self, data):
        '''
        Process the recevied rain rate data
        '''
        rainrate = data['rainratemm']
        self.sm.handle_data(rainrate)
        next_state = self.sm.next() 
        
        if next_state:
            self.sm.change_state(next_state)

        # if rainrate > 0 and self.is_raining == False:                
        #     self.is_raining = True
        #     self._notify_state_change("Det har börjat regna")
        
        # if rainrate <= 0 and self.is_raining == True:
        #     self.is_raining = False
        #     self._notify_state_change("Det har nog slutat regna")


    # def _notify_state_change(self,msg):
    #     '''
    #     Update any pool temp change
    #     '''
    #     self.logger.debug(msg)
    #     helper.send_telegram_message(self.config, msg)