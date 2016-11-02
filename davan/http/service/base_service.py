from davan.http.service.serviceIf import ServiceIf
 
class BaseService(ServiceIf):

    def __init__(self, service_name, config):
        self.invoked = 0
        self.error = 0
        self.service_name = service_name
        self.config = config
        
    def handle_request(self, input):
        """Retrieve data from the input source and return an object."""
        return "Function not implemented"

    def get_name(self):
        return self.service_name
    
    def stop_service(self):
        pass
    
    def start_service(self):
        pass
    
    def get_counters(self):
        return self.invoked, self.error

    def increment_invoked(self):
        self.invoked +=1 

    def increment_errors(self):
        self.error +=1 

    def is_enabled(self):
        return self.config[self.service_name+"Enabled"]