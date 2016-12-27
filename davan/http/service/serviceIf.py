'''
@author: davandev
'''

import abc

class ServiceIf(object):
    '''
    Interface for services
    '''
    __metaclass__ = abc.ABCMeta
    
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