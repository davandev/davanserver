'''
@author: davandev
'''

import abc

class ServiceIf(object, metaclass=abc.ABCMeta):
    '''
    Interface for services
    '''
    
    @abc.abstractmethod
    def handle_request(self, input):
        """
        Abstract method to override to handle received request.
        """
        return
    @abc.abstractmethod
    def get_name(self):
        """
        Abstract method returns name of the service  
        """
        return ""
    
    @abc.abstractmethod
    def stop_service(self):
        '''
        Abstract method to stop service
        '''
        pass
    
    @abc.abstractmethod
    def start_service(self):
        '''
        Abstract method to start service
        '''
        pass
    
    @abc.abstractmethod
    def is_service_running(self):
        '''
        Abstract method to determine if service is running
        '''
        pass
    