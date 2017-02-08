# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.http.service.base_service import BaseService

class Mp3ProviderService(BaseService):
    '''
    classdocs
    '''
    def __init__(self, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.MP3_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
            
    def handle_request(self, msg):
        '''
        Received request for mp3 file.
        Verify that the mp3 file exist and return it
        @param msg, the wanted file.
        '''
        try:
            self.increment_invoked()
            self.logger.debug("Received mp3 service request for file: " + msg)
            res = msg.split('=')
            f = open(self.config['MP3_ROOT_FOLDER'] + res[1])
            content = f.read()
            f.close()
        except:
            self.increment_errors()
            self.logger.warning("Failed to open file: " + self.config['MP3_ROOT_FOLDER'] + res[1])
            return constants.RESPONSE_NOT_OK, constants.RESPONSE_FILE_NOT_FOUND
        
        return constants.RESPONSE_OK, constants.MIME_TYPE_MP3, content
    
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = Mp3ProviderService()
    test.handle_request("msg")
