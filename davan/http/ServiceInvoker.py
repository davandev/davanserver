'''
@author: davandev
'''

import os
import logging
import imp
import time
import re

import davan.config.config_creator as app_config
import davan.util.application_logger as app_logger
import davan.util.constants as constants

class ServiceInvoker(object):
    '''
    Service Handler module, scanning for services,
    '''
    def __init__(self, configuration):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.services ={}
        self.expression = re.compile(r'\w+')
        self.config = configuration
        # Determine if services are started
        self.running = False
        
    def is_running(self):
        return self.running
    
    def discover_services(self):
        """
        Scan service folder for all matching services.
        """
        self.logger.info("Discover services")
        for root, _, files in os.walk(self.config['SERVICE_PATH']):
            for service_file in files:
                if (service_file.endswith(".py") and 
                    not service_file.endswith("__init__.pyc") and 
                    not service_file.endswith("base_service.py")):
                        module_name = service_file.replace(".py","")
                        #mod = imp.load_compiled(module_name,os.path.join(root, service_file))
                        mod = imp.load_source(module_name, os.path.join(root, service_file))
                        self.logger.debug("ModuleName:"+module_name)

                        try:    
                            attributes = getattr(mod, module_name)
                            service = attributes(self, self.config)
                            self.services[service.get_name()] = service
                        except :
                            continue
                        self.logger.debug("Discovered service [" + module_name + "] Service key[" + service.get_name()+"]")
        return self.services
    
    def start_services(self):
        """
        Start all services that are enabled in configuration
        """
        self.logger.info("Starting services")
        for name, service in self.services.items():
            if service.is_enabled() and not service.is_service_running():
                service.start_service()
            else:
                self.logger.debug("Service " + name + " is disabled")
        self.running = True 
        self.logger.info("All configured services started")
            
    def get_service(self, service):
        """
        @param service, name of selected service
        @return: service matching service name
        """
        result = self.expression.findall(service)[0]
        
        if result in self.services:
#            self.logger.debug("Invoking service: ["+ result+"]")
            return self.services[result]
        elif service.endswith(constants.MP3_EXTENSION) or service.endswith(constants.MP3_EXTENSION1):
#            self.logger.debug("Invoking service: [mp3]")
            return self.services[constants.MP3_SERVICE_NAME]
        elif service.endswith(constants.OGG_EXTENSION) or service.endswith(constants.OGG_EXTENSION1):
#            self.logger.debug("Invoking service: [ogg]")
            return self.services[constants.MP3_SERVICE_NAME]
        elif service.endswith(constants.HTML_EXTENSION) or service.endswith(constants.CSS_EXTENSION):
#            self.logger.debug("Invoking service: [html]")
            return self.services[constants.HTML_SERVICE_NAME]
        
        # No service found
        self.logger.debug("No service ["+str(service)+"] found")
        
        return None
    
    def stop_all_except(self, service_name):
        self.logger.info("Stopping all services")

        for service in self.services.values():
            #self.logger.debug("Stopping: " + str(service.get_name()))
            if service.service_name == service_name:
                continue
            service.stop_service()
        self.running = False
        self.logger.info("All started services stopped")
                    
    def stop_services(self):
        """
        Stop all services
        """
        self.logger.info("Stopping all services")

        for service in self.services.values():
            #self.logger.debug("Stopping: " + str(service.get_name()))
            service.stop_service()
        self.running = False
        self.logger.info("All started services stopped")
       
if __name__ == '__main__':
    config = app_config.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = ServiceInvoker()
    test.invoke_services()
    test.get_service("/tts=234?")
    test.get_service("/presence?name=david")
    time.sleep(10)
    test.logger.info("Stopping thread")
    test.stop_services()
