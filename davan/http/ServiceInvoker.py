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
                if (service_file.endswith(".pyc") and 
                    not service_file.endswith("__init__.pyc") and 
                    not service_file.endswith("base_service.pyc")):
                        module_name = service_file.replace(".pyc","")
                        mod = imp.load_compiled(module_name,os.path.join(root, service_file))
                        try:    
                            attributes = getattr(mod, module_name)
                        except :
                            continue
                        
                        service = attributes(self.config)
                        self.services[service.get_name()] = service
                        self.logger.debug("Discovered service [" + module_name + "] Service key[" + service.get_name()+"]")
        return self.services
    
    def start_services(self):
        """
        Start all services that are enabled in configuration
        """
        self.logger.info("Starting services")
        for name, service in self.services.iteritems():
            if service.is_enabled():
                service.start_service()
            else:
                self.logger.debug("Service " + name + " is disabled")
        self.running = True 
            
    def get_service(self, service):
        """
        @param service, name of selected service
        @return: service matching service name
        """
        result = self.expression.findall(service)[0]
        
        if self.services.has_key(result):
            self.logger.debug("Invoking service: ["+ result+"]")
            return self.services[result]
        
        elif service.endswith(constants.HTML_EXTENSION) or service.endswith(constants.CSS_EXTENSION):
            self.logger.debug("Invoking service: [html]")
            return self.services["HtmlService"]
            
    def stop_services(self):
        """
        Stop all services
        """
        self.logger.info("Stopping all services")

        for service in self.services.itervalues():
            self.logger.debug("Stopping: " + str(service.get_name()))
            service.stop_service()
        self.running = False
        
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
