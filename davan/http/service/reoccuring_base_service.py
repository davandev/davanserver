'''
@author: davandev
'''
import datetime
import time
from davan.http.service.base_service import BaseService
from threading import Thread,Event

class ReoccuringBaseService(BaseService):
    '''
    Default implementations of a few service methods  
    '''
    def __init__(self, service_name, service_provider, config):
        BaseService.__init__(self, service_name, service_provider, config)
        self.event = Event()
            
    def stop_service(self):
        self.logger.debug("Stopping service")
        self.event.set()

    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        
        # Workaround to avoid attribute error exception in .strptime()
        # Use strptime before starting thread. 
        # See http://bugs.python.org/issue7980
        time.strptime("01:00", '%H:%M')
        _ = datetime.datetime.strptime("01:00", '%H:%M')
        # End of workaround

        #self.logger.info("Starting re-occuring service ")
        def loop():
            while not self.event.wait(self.get_next_timeout()):
                self.increment_invoked()
                self.handle_timeout()

        Thread(target=loop).start()    
        return self.event.set
    

    def handle_timeout(self):
        """
        Default implementation when timeout occur
        """
        self.logger.warning("Default implementation")
        pass
    
    def get_next_timeout(self):
        """
        Default implementation 
        """
        self.logger.warning("Default implementation")
        pass