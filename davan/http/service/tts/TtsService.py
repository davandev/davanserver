'''
Created on 8 feb. 2016

@author: davandeb
'''
import logging
import os
import urllib
import shutil

import davan.config.config_creator as configuration
import davan.util.cmd_executor as cmd_executor
from davan.util import application_logger as app_logger
from davan.http.service.base_service import BaseService

class TtsService(BaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')

    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, "tts", config)
        self.logger = logging.getLogger(os.path.basename(__file__))

    def handle_request(self, msg):
        self.start(msg.split('=')[1])
        return 200, ""
    
    def start(self, msg):
        '''
        Recevied request from Fibaro system to speak message.
        Check if message if already available, otherwise contact
        VoiceRSS to translate and get the mp3 file.
        @param msg to translate and speak.
        '''
        self.increment_invoked()
        if os.path.exists(self.config['SPEAK_FILE']):
            os.remove(self.config['SPEAK_FILE'])
        
        self.logger.info("Received request for new TTS message ["+ msg + "]")
        
        mp3_file = self.config['TTS_PRECOMPILED_ALARM_MSG_PATH'] + msg + ".mp3"

        self.logger.debug("Search for cached file: "+ mp3_file)
        if os.path.exists(mp3_file):
            self.logger.debug("Using cached mp3 file")
        else:   
            self.logger.debug("Generate mp3 for [" + msg+"]")
            self.generate_mp3(msg, mp3_file)
        
        shutil.copyfile(mp3_file, self.config['SPEAK_FILE'])
        cmd_executor.execute_block_in_shell(self.config['SPEAK_CMD'] + ' ' + 
                                   self.config['SPEAK_FILE'] , 
                                   self.config['SPEAK_CMD'])
    
    def generate_mp3(self, msg, mp3_file):
        ''' 
        Generate a mp3 file from the msg string.        
        Replace '_' with '%20' == whitespace
        @param msg message to translate
        @parm mp3_file output file where to store spoken msg.
        '''  
        encoded_msg = msg.replace("_", "%20")
        self.logger.debug("Encoded string [" + encoded_msg + "]")
        
        url = self.config['VOICERSS_URL'].replace("REPLACE_WITH_MESSAGE", encoded_msg)
        self.logger.debug("Url: ["+ url + "]")
        
        urllib.urlretrieve(url, mp3_file )

if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = TtsService()
    test.start("skalskyddet_aktiverat")
