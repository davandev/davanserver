import abc

class ServiceIf(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def handle_request(self, input):
        """Retrieve data from the input source and return an object."""
        return
    @abc.abstractmethod
    def get_name(self):
        return ""
    
    @abc.abstractmethod
    def stop_service(self):
        pass
    
    @abc.abstractmethod
    def start_service(self):
        pass