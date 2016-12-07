'''
'''
import logging
import os

import json
import urllib

from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService


class ActiveScenesMonitorService(BaseService):
    '''
    Monitor active scenes on Fibaro system, in some cases
    scenes that should always be running are stopped.
    Check status of each active scene and start it if stopped. 
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.ACTIVE_SCENES_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()

    def stop_service(self):
        self.logger.info("Stopping service")
        self.event.set()
    
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        self.logger.info("Starting re-occuring event")

        def loop():
            while not self.event.wait(900): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()

        Thread(target=loop).start()    
        return self.event.set
                                         
    def timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        self.logger.info("Got a timeout, check state of monitored scenes " + str(self.config['MONITOR_SCENES']))
        try:
            for scene in self.config['MONITOR_SCENES']:
                scene_url = self.config['GET_STATE_SCENE_URL'].replace("<ID>",scene)
                self.logger.info("Check state of " + scene_url)

                result = urllib.urlopen(scene_url)
                res = result.read()
                self.logger.info("Result:" + res)    

                data = json.loads(res)
                if data["runningInstances"] ==1:
                    self.logger.info("Scene already running")
                else:
                    self.logger.info("Scene not running")
                    scene_url = self.config['START_SCENE_URL'].replace("<ID>",scene)
                    self.logger.info("Starting scene " + scene_url)
                    result = urllib.urlopen(scene_url)        
        except Exception:
            self.increment_errors()
            self.logger.info("Caught exception") 
            pass

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, id):
        """
        Override and provide gui
        """
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", "<li>Monitor: " + str(self.config['MONITOR_SCENES']) + " </li>\n")
        return column
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = ActiveScenesMonitorService()