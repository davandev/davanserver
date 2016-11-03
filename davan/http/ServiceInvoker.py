'''
Created on 22 okt. 2016

@author: Wilma
'''
import os
import logging
import imp
import time
import re

import davan.config.config_creator as app_config
import davan.util.application_logger as app_logger
from davan.http.service.base_service import BaseService

class ServiceInvoker(object):
    '''
    classdocs
    '''
    def __init__(self, configuration):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.services ={}
        self.expression = re.compile(r'\w+')
        self.html = ".html"
        self.css = ".css"
        self.config = configuration
        self.running = False
        
    def is_running(self):
        return self.running
    
    def discover_services(self):
        self.logger.info("Discover services")
        for root, _, files in os.walk(self.config['SERVICE_PATH']):
            for file in files:
                if file.endswith(".pyc") and not file.endswith("__init__.pyc") and not file.endswith("base_service.pyc"):
                    module_name = file.replace(".pyc","")
                    mod = imp.load_compiled(module_name,os.path.join(root, file))
                    try:    
                        attributes = getattr(mod, module_name)
                    except :
                        continue
                    
                    service = attributes(self.config)
                    self.services[service.get_name()] = service
                    self.logger.info("Discovered service [" + module_name + "] Service key[" + service.get_name()+"]")
        return self.services
    
    def start_services(self):
        self.logger.info("Starting services")
        for name, service in self.services.iteritems():
            if service.is_enabled():
                service.start_service()
            else:
                self.logger.info("Service " + name + " is disabled")
        self.running = True 
            #self.logger.info("Starting service [" + str(service) + "] Service key[" + name+"]")
            
    def get_service(self, service):
        result = self.expression.findall(service)[0]
        if self.services.has_key(result):
            self.logger.info("Invoking service: ["+ result+"]")
            return self.services[result]
        elif service.endswith(self.html) or service.endswith(self.css):
            self.logger.info("Invoking service: [html]")
            return self.services["HtmlService"]
            
    def stop_services(self):
        self.logger.info("Stopping all services")
        for service in self.services.itervalues():
            self.logger.info("Stopping: " + str(service.get_name()))
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