'''
Created on 17 feb. 2017

@author: davandev
'''

import logging
import os
from davan.http.service.base_service import BaseService
from davan.util import application_logger as app_logger
import davan.util.constants as constants
import davan.config.config_creator as configuration
import davan.http.service.roxcore.RoxcoreSpeakerCommands as commands

class RoxcoreService(BaseService):
    '''
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.ROXCORE_SPEAKER_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.host_address = "http://" + config['ROXCORE_HOST_ADDRESS']


    def handle_request(self, msg):
        '''
        Play mp3 file on Roxcore speaker.
        @param msg, file to play 
        '''
        try:
            commands.replace_queue(self.host_address, msg)
            commands.send_play_with_index(self.host_address)
            commands.set_play_mode(self.host_address)
            self.increment_invoked()
        except:
            self.increment_errors()
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG
    
    def start(self):
        '''
        '''
        self.logger.info("Start roxcore service")

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
            return BaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        res = "Speakers:" + self.config['ROXCORE_HOST_ADDRESS']
        column  = column.replace("<SERVICE_VALUE>", res)

        return column
        
if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = RoxcoreService(config)
    test.handle_request("Skalskydd_aktiverat.mp3")
