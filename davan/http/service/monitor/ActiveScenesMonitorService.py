'''
@author: davandev
'''

import logging
import os
import json
import urllib
import traceback
from threading import Thread,Event

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService


class ActiveScenesMonitorService(ReoccuringBaseService):
    '''
    Monitor active scenes on Fibaro system, in some cases
    scenes that should always be running are stopped.
    Check status of each active scene and start it if stopped. 
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.ACTIVE_SCENES_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.time_to_next_timeout = 900
        
    def get_next_timeout(self):
        return self.time_to_next_timeout
                                             
    def handle_timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        self.logger.info("Got a timeout, check state of monitored scenes " + str(self.config['MONITOR_SCENES']))
        try:
            for scene in self.config['MONITOR_SCENES']:
                scene_url = self.config['GET_STATE_SCENE_URL'].replace("<ID>",scene)
                self.logger.info("Check state of " + scene)

                result = urllib.urlopen(scene_url)
                res = result.read()

                data = json.loads(res)
                if data["runningInstances"] ==1:
                    self.logger.info("Scene already running")
                else:
                    self.logger.info("Scene not running")
                    self.logger.debug("Result:" + res)    
                    scene_url = self.config['START_SCENE_URL'].replace("<ID>",scene)
                    self.logger.info("Starting scene " + scene_url)
                    result = urllib.urlopen(scene_url)        
        except Exception:
            self.logger.error(traceback.format_exc())

            self.increment_errors()
            self.logger.info("Caught exception") 
            pass

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return ReoccuringBaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", "<li>Monitor: " + str(self.config['MONITOR_SCENES']) + " </li>\n")
        return column
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = ActiveScenesMonitorService()