'''
@author: davandev
'''

from davan.http.service.serviceIf import ServiceIf
import davan.util.constants as constants
 
class BaseService(ServiceIf):
    '''
    Default implementations of a few service methods  
    '''
    def __init__(self, service_name, service_provider, config):
        # Counter 
        self.invoked = 0
        self.error = 0
        # 
        self.service_name = service_name
        self.config = config
        self.services = service_provider
        
    def handle_request(self, input):
        """
        Retrieve data from the input source and return an object.
        @param input 
        """
        return "Function not implemented"

    def get_name(self):
        """
        Return service name
        """
        return self.service_name
    
    def stop_service(self):
        """
        Default implementation when stopping service
        """
        pass
    
    def start_service(self):
        """
        Default implementation when starting service
        """
        pass
    
    def get_counters(self):
        """
        Return counters
        """
        return self.invoked, self.error

    def increment_invoked(self):
        """
        Increment counter when service is invoked
        """
        self.invoked +=1 

    def increment_errors(self):
        """
        Increment counter when error has occured
        """
        self.error +=1 

    def is_enabled(self):
        """
        Return True if service is enabled, false otherwise
        """
        return self.config[self.service_name+"Enabled"]
    
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return False
    
    def get_html_gui(self, column_ud):
        """
        Override and provide gui
        """
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_ud))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", "<li>Enabled: " + str(self.config[self.service_name+"Enabled"]) + " </li>\n")
        return column
